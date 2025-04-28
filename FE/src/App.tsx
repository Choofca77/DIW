import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import MediaWall from './components/MediaWall';

const App: React.FC = () => {
  const [isHamburgerOpen, setIsHamburgerOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [filter, setFilter] = useState({});
  const [uploadedFiles, setUploadedFiles] = useState<FileList | null>(null);

  const handleUpload = (files: FileList) => {
    setUploadedFiles(files);
    // TODO: Add logic to index new media into the database
    console.log('Uploaded files:', files);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <h1 className="text-center text-2xl font-bold my-4">Digital Wall</h1>
      {/* Header */}
      <header className="bg-white shadow-sm fixed top-0 left-0 right-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          {/* Settings Icon */}
          <div className="relative">
            <button
              onClick={() => setIsSettingsOpen(!isSettingsOpen)}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              style={{ width: 40, height: 40 }}
              aria-label="Settings"
            >
              <span className="text-lg font-bold">⚙️</span>
            </button>
            {isSettingsOpen && (
              <div className="absolute top-12 left-0 bg-white shadow-lg rounded-lg p-4">
                {/* Upload Icon */}
                <label
                  htmlFor="file-upload"
                  className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors cursor-pointer"
                >
                  Upload Media
                </label>
                <input id="file-upload" type="file" multiple className="hidden" />
              </div>
            )}
          </div>

          {/* Hamburger Icon */}
          <div className="relative">
            <button
              onClick={() => setIsHamburgerOpen(!isHamburgerOpen)}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              style={{ width: 40, height: 40 }}
              aria-label="Menu"
            >
              <span className="text-lg font-bold">☰</span>
            </button>
            {isHamburgerOpen && (
              <Sidebar
                isOpen={isHamburgerOpen}
                onClose={() => setIsHamburgerOpen(false)}
                onFilterChange={setFilter}
                onUpload={handleUpload}
              />
            )}
          </div>
        </div>
      </header>

      {/* Media Wall */}
      <main className="pt-16">
        <MediaWall filter={filter} uploadedFiles={uploadedFiles} />
      </main>
    </div>
  );
};

export default App;