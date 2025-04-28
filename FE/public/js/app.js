// Utility function to handle both touch and click events
function addTouchClickListener(id, callback) {
  const el = document.getElementById(id);
  if (!el) return;

  el.addEventListener("click", callback);
  el.addEventListener("touchstart", (e) => {
    e.preventDefault(); // Prevents ghost clicks
    callback();
  });
}

// Toggle upload menu visibility
addTouchClickListener("settings-icon", () => {
  document.getElementById("upload-option").classList.toggle("show");
});

// Toggle filter menu visibility
addTouchClickListener("hamburger-icon", () => {
  document.getElementById("filter-options").classList.toggle("show");
});

// Toggle sub-filter under "Others"
window.toggleSubFilter = function () {
  document.getElementById("sub-filter-options").classList.toggle("show");
};

// Apply filter (replace with actual filtering logic)
window.applyFilter = function (type) {
  console.log(`Filtering by: ${type}`);
  // Insert real-time filtering logic here (e.g., filtering media displayed)
  closeFilterDropdown(); // Close dropdown after applying filter
};

// Close the filter dropdown
function closeFilterDropdown() {
  const filterOptions = document.getElementById("filter-options");
  filterOptions.classList.remove("show");
}

// Handle file uploads
document.getElementById("upload-input").addEventListener("change", (event) => {
  const files = event.target.files;
  if (files.length > 0) {
    console.log("Uploading new files:", files);
    // Insert file handling and indexing logic here
  }
});

// Toggle sub-filter visibility (Scenery/Objects)
const subFilterButton = document.querySelector('.nested-dropdown button');
if (subFilterButton) {
  subFilterButton.addEventListener('click', () => {
    const subFilterOptions = document.getElementById('sub-filter-options');
    subFilterOptions.classList.toggle('show');
  });
}
