// Function to load thumbnails dynamically
function loadThumbnails(media) {
  const container = document.getElementById('thumbnail-flow');
  container.innerHTML = ''; // Clear existing thumbnails

  media.forEach(item => {
      const thumbnail = document.createElement('div');
      thumbnail.classList.add('thumbnail');
      thumbnail.style.backgroundImage = `url(${item.thumbnail})`; // Add the media thumbnail
      thumbnail.addEventListener('click', function() {
          expandThumbnail(item);
      });

      container.appendChild(thumbnail);
  });
}

// Example function to expand the media when clicked
function expandThumbnail(item) {
  alert(`Expanding media: ${item.title}`);
}
