import os
import sqlite3
import face_recognition
from math import sqrt
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

print("Script is running...")

# Global flag for stopping the process
stop_requested = False

def authenticate_google_drive():
    """Authenticate and return a GoogleDrive instance."""
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()  # Creates local webserver and auto handles authentication
    drive = GoogleDrive(gauth)
    return drive

def download_files_from_drive(drive, folder_id, download_path):
    """Download all files from a Google Drive folder."""
    file_list = drive.ListFile({'q': f"'{folder_id}' in parents and trashed=false"}).GetList()
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    for file in file_list:
        if file['mimeType'].startswith('image/'):  # Only process image files
            print(f"Downloading {file['title']}...")
            file.GetContentFile(os.path.join(download_path, file['title']))

def create_database(db_name):
    """Create the database and the media_metadata table if it doesn't exist."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS media_metadata (
            id INTEGER PRIMARY KEY,
            file_path TEXT UNIQUE,
            filename TEXT,
            date_taken TEXT,
            date_added TEXT,
            make TEXT,
            model TEXT,
            resolution TEXT,
            iso TEXT,
            f_stop TEXT,
            shutter_speed TEXT,
            GPSInfo TEXT,
            cluster_id INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def add_missing_columns(db_name):
    """Ensure the table has all required columns."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(media_metadata);")
    columns = [col[1] for col in cursor.fetchall()]
    if "filename" not in columns:
        cursor.execute("ALTER TABLE media_metadata ADD COLUMN filename TEXT;")
    if "iso" not in columns:
        cursor.execute("ALTER TABLE media_metadata ADD COLUMN iso TEXT;")
    if "f_stop" not in columns:
        cursor.execute("ALTER TABLE media_metadata ADD COLUMN f_stop TEXT;")
    if "shutter_speed" not in columns:
        cursor.execute("ALTER TABLE media_metadata ADD COLUMN shutter_speed TEXT;")
    if "GPSInfo" not in columns:
        cursor.execute("ALTER TABLE media_metadata ADD COLUMN GPSInfo TEXT;")
    if "cluster_id" not in columns:
        cursor.execute("ALTER TABLE media_metadata ADD COLUMN cluster_id INTEGER;")
    conn.commit()
    conn.close()

def extract_gps_info(gps_data):
    """Convert raw GPS data into latitude and longitude."""
    def convert_to_degrees(value):
        d, m, s = value
        return d + (m / 60.0) + (s / 3600.0)

    if not gps_data:
        return None

    gps_info = {}
    for key, val in gps_data.items():
        decoded_key = GPSTAGS.get(key, key)
        gps_info[decoded_key] = val

    try:
        lat = convert_to_degrees(gps_info["GPSLatitude"])
        if gps_info["GPSLatitudeRef"] != "N":
            lat = -lat

        lon = convert_to_degrees(gps_info["GPSLongitude"])
        if gps_info["GPSLongitudeRef"] != "E":
            lon = -lon

        return f"{lat}, {lon}"
    except KeyError:
        return None

def extract_image_metadata(image_path):
    """Extract metadata from an image file."""
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        if exif_data is not None:
            metadata = {
                TAGS.get(tag): value for tag, value in exif_data.items() if tag in TAGS
            }
            gps_info = extract_gps_info(metadata.get("GPSInfo"))
            structured_metadata = {
                "DateTimeOriginal": metadata.get("DateTimeOriginal"),
                "Make": metadata.get("Make"),
                "Model": metadata.get("Model"),
                "Resolution": f"{image.size[0]}x{image.size[1]}",
                "ISO": metadata.get("ISOSpeedRatings"),
                "FStop": float(metadata.get("FNumber", 0)) if metadata.get("FNumber") else None,
                "ShutterSpeed": str(metadata.get("ExposureTime")) if metadata.get("ExposureTime") else None,
                "GPSInfo": gps_info,
                "DateAdded": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            print(f"✅ EXIF for {image_path}: {structured_metadata}")
            return structured_metadata
        else:
            print(f"⚠️ No EXIF found in {image_path}")
            return {}
    except Exception as e:
        print(f"❌ Error extracting metadata from {image_path}: {e}")
        return {}

def insert_metadata(db_name, file_path, metadata):
    """Insert metadata into the database."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO media_metadata (
                file_path, filename, date_taken, date_added, make, model, resolution, iso, f_stop, shutter_speed, GPSInfo
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            file_path,
            os.path.basename(file_path),
            metadata.get("DateTimeOriginal"),
            metadata.get("DateAdded"),
            metadata.get("Make"),
            metadata.get("Model"),
            metadata.get("Resolution"),
            metadata.get("ISO"),
            metadata.get("FStop"),
            metadata.get("ShutterSpeed"),
            metadata.get("GPSInfo")
        ))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"⚠️ Duplicate entry skipped for {file_path}")
    conn.close()

def file_already_processed(db_name, file_path):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM media_metadata WHERE file_path = ?', (file_path,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def extract_face_encodings(db_name):
    """Extract facial encodings for all images in the database."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT id, file_path FROM media_metadata;")
    image_data = cursor.fetchall()  # List of (id, file_path)
    conn.close()

    encodings = []
    image_ids = []

    for image_id, file_path in image_data:
        if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            try:
                print(f"Processing {file_path} for face encodings...")
                image = face_recognition.load_image_file(file_path)
                face_locations = face_recognition.face_locations(image)
                face_encodings = face_recognition.face_encodings(image, face_locations)

                if face_encodings:
                    encodings.extend(face_encodings)
                    image_ids.extend([image_id] * len(face_encodings))
                else:
                    print(f"⚠️ No faces detected in {file_path}.")
            except Exception as e:
                print(f"❌ Error processing {file_path}: {e}")

    return encodings, image_ids

def normalize_encoding(encoding):
    """Normalize a single encoding vector."""
    magnitude = sqrt(sum(x**2 for x in encoding))
    if magnitude == 0:
        return encoding  # Avoid division by zero
    return [x / magnitude for x in encoding]

def normalize_encodings(encodings):
    """Normalize all encodings."""
    return [normalize_encoding(encoding) for encoding in encodings]

def euclidean_distance(vec1, vec2):
    """Calculate the Euclidean distance between two vectors."""
    return sqrt(sum((a - b) ** 2 for a, b in zip(vec1, vec2)))

def cluster_faces(encodings, eps=0.5, min_samples=2):
    """Cluster facial encodings using a pure Python DBSCAN-like algorithm."""
    if not encodings:
        print("⚠️ No encodings provided for clustering.")
        return []

    labels = [-1] * len(encodings)  # Initialize all labels as -1 (unclustered)
    cluster_id = 0

    for i, encoding in enumerate(encodings):
        if labels[i] != -1:  # Skip already clustered points
            continue

        # Find neighbors within `eps` distance
        neighbors = []
        for j, other_encoding in enumerate(encodings):
            if euclidean_distance(encoding, other_encoding) <= eps:
                neighbors.append(j)

        if len(neighbors) < min_samples:
            labels[i] = -1  # Mark as noise
        else:
            # Expand cluster
            labels[i] = cluster_id
            while neighbors:
                neighbor = neighbors.pop()
                if labels[neighbor] == -1:  # Previously marked as noise
                    labels[neighbor] = cluster_id
                elif labels[neighbor] == -1:  # Not yet visited
                    labels[neighbor] = cluster_id
                    # Add neighbors of this point
                    for k, other_encoding in enumerate(encodings):
                        if euclidean_distance(encodings[neighbor], other_encoding) <= eps:
                            neighbors.append(k)
            cluster_id += 1

    print(f"✅ Clustering complete. Found {cluster_id} clusters.")
    return labels

def update_cluster_ids(db_name, image_ids, labels):
    """Update the database with cluster IDs."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        for image_id, cluster_id in zip(image_ids, labels):
            cursor.execute("UPDATE media_metadata SET cluster_id = ? WHERE id = ?", (cluster_id, image_id))
        conn.commit()
        conn.close()
        print("✅ Database updated with cluster IDs.")
    except sqlite3.Error as e:
        print(f"❌ Database update error: {e}")

def process_folder(folder_path, db_name, limit=100000):
    global stop_requested
    processed_count = 0

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if stop_requested:
                print("⚠️ Process stopped by user.")
                return

            file_path = os.path.join(root, file)
            print(f"Processing file: {file_path}")

            if file_already_processed(db_name, file_path):
                print(f"⚠️ Skipping {file_path}, already processed.")
                continue

            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                metadata = extract_image_metadata(file_path)
                insert_metadata(db_name, file_path, metadata)
                processed_count += 1

                if processed_count >= limit:
                    print(f"✅ Limit of {limit} files reached. Stopping.")
                    return

def stop_process():
    global stop_requested
    stop_requested = True

if __name__ == "__main__":
    db_name = "media_metadata.db"
    download_path = "downloaded_images"

    # Ask the user for input type
    input_type = input("Enter 'local' to process local files or 'drive' to process Google Drive files: ").strip().lower()

    if input_type == "local":
        # Process local files
        folder_path = input("Enter the path to the local folder: ").strip()
        create_database(db_name)
        add_missing_columns(db_name)
        print("Processing local files...")
        process_folder(folder_path, db_name)
        print(f"✅ Metadata extraction complete. Data stored in {db_name}.")
    elif input_type == "drive":
        # Process Google Drive files
        folder_id = input("Enter the Google Drive folder ID: ").strip()
        drive = authenticate_google_drive()
        print("Downloading files from Google Drive...")
        download_files_from_drive(drive, folder_id, download_path)
        create_database(db_name)
        add_missing_columns(db_name)
        print("Processing downloaded files...")
        process_folder(download_path, db_name)
        print(f"✅ Metadata extraction complete. Data stored in {db_name}.")
    else:
        print("❌ Invalid input. Please enter 'local' or 'drive'.")

    try:
        # Step 3: Extract facial encodings
        print("Extracting facial encodings...")
        encodings, image_ids = extract_face_encodings(db_name)
        if not encodings:
            print("❌ No facial encodings found. Exiting.")
            exit()

        # Step 4: Normalize encodings
        print("Normalizing encodings...")
        encodings = normalize_encodings(encodings)

        # Step 5: Cluster faces
        print("Clustering faces...")
        labels = cluster_faces(encodings, eps=0.5, min_samples=2)
        if not labels:
            print("❌ Clustering failed. Exiting.")
            exit()

        # Step 6: Update database with cluster IDs
        print("Updating database with cluster IDs...")
        update_cluster_ids(db_name, image_ids, labels)

        print("✅ Face clustering and metadata extraction complete!")
    except KeyboardInterrupt:
        stop_process()
        print("⚠️ Process interrupted by user.")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
