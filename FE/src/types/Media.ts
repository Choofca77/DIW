// src/types/Media.ts

// Define the structure of a Media item
export interface Media {
  id: string; // Unique identifier for the image
  src: string; // Image source URL
  title: string; // Image title
  tags: string[]; // Tags associated with the image
  location: string; // Location where the image was taken
  dateCreated?: string; // Date when the media was created (optional)
  faces?: string[]; // List of faces detected in the media (optional)
  eventType?: string; // Type of event associated with the media (optional)
  objects?: string[]; // List of objects detected in the media (optional)
  scenery?: string[]; // List of scenery tags in the media (optional)
  type: 'image' | 'video';
  path: string;
  thumbnail: string; // Added thumbnail property
  filename: string; // Added filename property
  has_face?: boolean; // Added optional property
}

// Define the structure for applying filters to media items
export interface Filter {
  category: 'faces' | 'date' | 'eventType' | 'location' | 'objects' | 'scenery';  // Category to filter by
  value?: string | Date | string[];  // Value to filter (could be string, Date, or array of strings)
}

// Define a simpler Filter type with common categories
export type SimpleFilter = 'birthday' | 'wedding' | 'holiday' | 'date' | 'face' | 'location' | 'scenery' | 'objects';

// Function to filter media based on the Filter interface
export function filterMedia(media: Media[], filter: Filter): Media[] {
  return media.filter((item) => {
      let matches = true;
    // Apply the filter logic based on the filter values
    if (filter.category === 'faces' && Array.isArray(filter.value)) {
      const hasFace = Array.isArray(filter.value) && item.faces?.some((face) => (filter.value as string[]).includes(face)) ? true : false;
      if (!hasFace) {
        matches = false;
      }
    }

    if (filter.category === 'date' && filter.value) {
      const date = item.dateCreated ? new Date(item.dateCreated) : null;
      const filterDate = filter.value as Date;
      if (date && date.toDateString() !== filterDate.toDateString()) {
        matches = false;
      }
    }

    if (filter.category === 'eventType' && filter.value) {
      if (item.eventType !== filter.value) {
        matches = false;
      }
    }

    if (filter.category === 'location' && filter.value) {
      if (item.location !== filter.value) {
        matches = false;
      }
    }
    if (filter.category === 'objects' && Array.isArray(filter.value)) {
      const hasObject = Array.isArray(filter.value) && item.objects?.some((obj) => (filter.value as string[]).includes(obj)) ? true : false;
      if (!hasObject) {
        matches = false;
      }
    }

    if (filter.category === 'scenery' && Array.isArray(filter.value)) {
      const hasScene = Array.isArray(filter.value) && item.scenery?.some((scene) => (filter.value as string[]).includes(scene)) ? true : false;
      if (!hasScene) {
        matches = false;
      }
    }

    return matches;
  });
}
