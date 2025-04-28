import React, { useEffect, useState } from 'react';
import { Media } from '../types/Media';
import { useInView } from 'react-intersection-observer';
import Masonry from 'react-masonry-css';

interface MediaWallProps {
  filter: Partial<Media>;
  uploadedFiles: FileList | null;
}

const MediaWall: React.FC<MediaWallProps> = ({ filter, uploadedFiles }) => {
  const { ref } = useInView({ threshold: 0.1, triggerOnce: true });
  const [expanded, setExpanded] = useState<string | null>(null);
  const [expandedImage, setExpandedImage] = useState<Media | null>(null);
  const [layout, setLayout] = useState<'grid' | 'carousel' | 'floating'>('grid');
  const [images, setImages] = useState<Media[]>([]);
  const [selectedImage, setSelectedImage] = useState<string | null>(null); // State for modal

  useEffect(() => {
    fetch('http://localhost:5000/images')
      .then((response) => response.json())
      .then((data) => {
        console.log('Fetched images:', data); // Debugging log
        setImages(data);
      })
      .catch((error) => console.error('Error fetching images:', error));
  }, []);

  // TODO: Fetch and filter media from the database based on the `filter` prop
  console.log('Filter applied:', filter);
  console.log('Uploaded files:', uploadedFiles);

  // Define the breakpoint columns for Masonry layout
  const breakpointColumns = {
    default: 4,
    1100: 3,
    700: 2,
    500: 1,
  };

  // Handle thumbnail click for expanding/collapsing
  const handleThumbnailClick = (id: string) => {
    if (expanded === id) {
      setExpanded(null);  // Collapse if the same thumbnail is tapped
    } else {
      setExpanded(id);  // Expand the clicked thumbnail
    }
  };

  const handleImageClick = (image: Media) => {
    setExpandedImage(image);
  };

  const handleClose = () => {
    setExpandedImage(null);
  };

  return (
    <div ref={ref} className="p-4 relative">
      {/* Layout Selector */}
      <div className="mb-4">
        <select
          value={layout}
          onChange={(e) => setLayout(e.target.value as 'grid' | 'carousel' | 'floating')}
          className="p-2 border rounded"
        >
          <option value="grid">Grid Layout</option>
          <option value="carousel">Carousel Layout</option>
          <option value="floating">Floating Layout</option>
        </select>
      </div>

      {/* Render Layout */}
      {layout === 'grid' && (
        <div>
          {images.length === 0 ? (
            <p>No images available</p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {images.map((image) => (
                <div
                  onClick={() => {
                    console.log('Image clicked:', image.filename); // Log the clicked image
                    setSelectedImage(image.filename); // Open modal
                  }}
                  className="relative cursor-pointer"
                >
                  <img
                    src={`http://localhost:5000/images/${image.filename}`}
                    alt={`Image ${image.id}`}
                    className="w-full h-full object-cover rounded-lg shadow-md hover:scale-105 transition-transform"
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {layout === 'carousel' && (
        <div className="flex overflow-x-scroll space-x-4">
          {images.map((image) => (
            <div
              key={image.id}
              className="flex-shrink-0 w-64 cursor-pointer"
              onClick={() => handleImageClick(image)}
            >
              <img
                src={`http://localhost:5000/images/${image.filename}`}
                alt={`Image ${image.id}`}
                className="w-full h-full object-cover rounded-lg shadow-md hover:scale-105 transition-transform"
              />
            </div>
          ))}
        </div>
      )}

      {layout === 'floating' && (
        <div className="relative">
          {images.map((image) => (
            <div
              key={image.id}
              className="absolute cursor-pointer animate-float"
              style={{
                top: `${Math.random() * 80}vh`,
                left: `${Math.random() * 80}vw`,
              }}
              onClick={() => handleImageClick(image)}
            >
              <img
                src={`http://localhost:5000/images/${image.filename}`}
                alt={`Image ${image.id}`}
                className="w-32 h-32 object-cover rounded-lg shadow-md hover:scale-105 transition-transform"
              />
            </div>
          ))}
        </div>
      )}

      {/* Expanded Image */}
      {expandedImage && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
          <div className="relative">
            <button
              onClick={() => setExpandedImage(null)}
              className="absolute top-4 right-4 text-white text-2xl"
            >
              ✖
            </button>
            <img
              src={expandedImage.src}
              alt={expandedImage.title}
              className="max-w-full max-h-full rounded-lg"
            />
            <div className="text-white text-center mt-4">
              <h2 className="text-xl font-bold">{expandedImage.title}</h2>
              <p>Tags: {expandedImage.tags.join(', ')}</p>
              <p>Location: {expandedImage.location}</p>
            </div>
          </div>
        </div>
      )}

      {/* Modal */}
      {selectedImage && (
        <div className="fixed inset-0 z-50">
          {/* Background Overlay */}
          <div
            className="absolute inset-0 bg-black bg-opacity-75"
          onClick={() => setSelectedImage(null)} // Close modal on background click
></div>

          {/* Modal Content */}
          <div className="relative flex items-center justify-center h-full">
          <div className="relative bg-white p-4 rounded-lg">
            <img
              src={`http://localhost:5000/images/${selectedImage}`}
              alt="Selected"
              className="max-w-full max-h-screen"
            />
            <button
              onClick={() => setSelectedImage(null)} // Close modal on button click
              className="absolute top-2 right-2 bg-red-500 text-white px-2 py-1 rounded-full"
            >
              ✕
            </button>
</div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MediaWall;