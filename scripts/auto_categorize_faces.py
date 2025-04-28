import os
import sqlite3
import dlib
import math
import shutil
from PIL import Image
from collections import defaultdict

# Load Dlib's face detector and face recognition model
face_detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
face_recognition_model = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")

def get_image_paths_from_database(db_name, table_name):
    """Retrieve image file paths from the database."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute(f"SELECT id, file_path FROM {table_name};")
        image_data = cursor.fetchall()  # Returns a list of tuples (id, file_path)
        conn.close()
        if not image_data:
            print("⚠️ No image paths found in the database.")
        return image_data
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return []

def extract_face_encodings(image_data):
    """Extract facial encodings from all images."""
    encodings = []
    image_ids = []

    for image_id, file_path in image_data:
        if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            try:
                print(f"Processing {file_path}...")
                image = dlib.load_rgb_image(file_path)
                faces = face_detector(image, 1)  # Detect faces

                if len(faces) > 0:
                    for face in faces:
                        shape = shape_predictor(image, face)
                        encoding = face_recognition_model.compute_face_descriptor(image, shape)
                        encodings.append(list(encoding))  # Convert to list for compatibility
                        image_ids.append(image_id)
                else:
                    print(f"⚠️ No faces detected in {file_path}.")
            except Exception as e:
                print(f"❌ Error processing {file_path}: {e}")

    if not encodings:
        print("⚠️ No facial encodings extracted from the images.")
    return encodings, image_ids

def euclidean_distance(vec1, vec2):
    """Calculate the Euclidean distance between two vectors."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec1, vec2)))

def hierarchical_clustering(encodings, threshold=0.6):
    """
    Perform Hierarchical Agglomerative Clustering (HAC) on facial encodings.
    Groups faces into clusters based on a distance threshold.
    """
    clusters = []
    for encoding in encodings:
        added_to_cluster = False
        for cluster in clusters:
            # Compare with the first encoding in the cluster
            if euclidean_distance(encoding, cluster[0]) <= threshold:
                cluster.append(encoding)
                added_to_cluster = True
                break
        if not added_to_cluster:
            clusters.append([encoding])  # Start a new cluster
    return clusters

def assign_cluster_ids(encodings, clusters):
    """
    Assign cluster IDs to each encoding based on the clustering results.
    """
    labels = [-1] * len(encodings)
    for cluster_id, cluster in enumerate(clusters):
        for encoding in cluster:
            index = encodings.index(encoding)
            labels[index] = cluster_id
    return labels

def update_database_with_clusters(db_name, table_name, image_ids, labels):
    """Update the database with cluster IDs."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        for image_id, cluster_id in zip(image_ids, labels):
            cursor.execute(f"UPDATE {table_name} SET cluster_id = ? WHERE id = ?", (cluster_id, image_id))
        conn.commit()
        conn.close()
        print("✅ Database updated with cluster IDs.")
    except sqlite3.Error as e:
        print(f"❌ Database update error: {e}")

def save_clustered_faces(db_name, table_name, output_folder):
    """Save images into folders based on their cluster IDs."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute(f"SELECT file_path, cluster_id FROM {table_name} WHERE cluster_id IS NOT NULL;")
        clustered_data = cursor.fetchall()
        conn.close()

        if not clustered_data:
            print("⚠️ No clustered data found in the database.")
            return

        for file_path, cluster_id in clustered_data:
            cluster_folder = os.path.join(output_folder, f"cluster_{cluster_id}")
            if not os.path.exists(cluster_folder):
                os.makedirs(cluster_folder)

            try:
                shutil.copy(file_path, cluster_folder)
            except Exception as e:
                print(f"❌ Error copying {file_path} to cluster folder: {e}")

        print(f"✅ Clustered faces saved in {output_folder}.")
    except sqlite3.Error as e:
        print(f"❌ Error retrieving clustered data: {e}")

def print_cluster_summary(db_name, table_name):
    """Print a summary of the clusters."""
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute(f"SELECT cluster_id, COUNT(*) FROM {table_name} GROUP BY cluster_id;")
        clusters = cursor.fetchall()
        conn.close()

        print("\nCluster Summary:")
        for cluster_id, count in clusters:
            print(f"Cluster {cluster_id}: {count} images")
    except sqlite3.Error as e:
        print(f"❌ Error retrieving cluster summary: {e}")

if __name__ == "__main__":
    # SQLite database and table name
    db_name = "media_metadata.db"
    table_name = "media_metadata"
    output_folder = "output_faces"

    try:
        # Step 1: Retrieve image paths from the database
        print("Retrieving image paths from the database...")
        image_data = get_image_paths_from_database(db_name, table_name)
        if not image_data:
            print("❌ No image paths retrieved from the database. Exiting.")
            exit()
        print(f"✅ Retrieved {len(image_data)} image paths.")

        # Step 2: Extract facial encodings
        print("Extracting facial encodings...")
        encodings, image_ids = extract_face_encodings(image_data)
        if not encodings:
            print("❌ No faces found in the images. Exiting.")
            exit()
        print(f"✅ Extracted {len(encodings)} facial encodings.")

        # Step 3: Perform hierarchical clustering
        print("Clustering faces using Hierarchical Agglomerative Clustering...")
        clusters = hierarchical_clustering(encodings, threshold=0.6)
        labels = assign_cluster_ids(encodings, clusters)
        print(f"✅ Clustering complete. Found {len(clusters)} clusters.")

        # Step 4: Update database with cluster IDs
        print("Updating database with cluster IDs...")
        update_database_with_clusters(db_name, table_name, image_ids, labels)

        # Step 5: Save clustered faces into folders
        print("Saving clustered faces into folders...")
        save_clustered_faces(db_name, table_name, output_folder)

        # Step 6: Print cluster summary
        print_cluster_summary(db_name, table_name)

        print("✅ Face clustering complete!")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
