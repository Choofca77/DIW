import React, { useState, useRef, useEffect } from 'react';
import { Calendar, MapPin, Tag, Users, Image } from 'lucide-react';
import { motion } from 'framer-motion';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  onUpload: (files: FileList) => void;
  onFilterChange: React.Dispatch<React.SetStateAction<{}>>;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const [isSubFilterOpen, setIsSubFilterOpen] = useState(false);
  const sidebarRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (sidebarRef.current && !sidebarRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [onClose]);

  if (!isOpen) return null; // Don't render the sidebar if it's not open

  return (
    <motion.div
      ref={sidebarRef}
      initial={{ x: '100%' }}
      animate={{ x: isOpen ? '0%' : '100%' }}
      transition={{ duration: 0.3 }}
      style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)', width: '250px', height: '100vh', position: 'fixed', top: 0, right: 0, padding: '20px', color: '#fff', zIndex: 50 }}
    >
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid gray' }}>
        <h2 style={{ fontSize: '1.5rem' }}>Filters</h2>
        <button onClick={onClose} style={{ fontSize: '1.2rem', background: 'none', border: 'none', color: '#fff' }}>
          ✖
        </button>
      </div>

      {/* Filter Options */}
      <div style={{ marginTop: '20px' }}>
        {/* Date Filter */}
        <div style={{ marginBottom: '10px' }}>
          <button style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '10px', border: '1px solid gray', borderRadius: '5px', background: 'none', color: '#fff', width: '100%' }}>
            <Calendar style={{ width: '20px', height: '20px' }} />
            Filter by Date
          </button>
        </div>

        {/* Faces Filter */}
        <div style={{ marginBottom: '10px' }}>
          <button style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '10px', border: '1px solid gray', borderRadius: '5px', background: 'none', color: '#fff', width: '100%' }}>
            <Users style={{ width: '20px', height: '20px' }} />
            Filter by Faces
          </button>
        </div>

        {/* Event Type Filter */}
        <div style={{ marginBottom: '10px' }}>
          <button style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '10px', border: '1px solid gray', borderRadius: '5px', background: 'none', color: '#fff', width: '100%' }}>
            <Tag style={{ width: '20px', height: '20px' }} />
            Filter by Event Type
          </button>
        </div>

        {/* Location Filter */}
        <div style={{ marginBottom: '10px' }}>
          <button style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '10px', border: '1px solid gray', borderRadius: '5px', background: 'none', color: '#fff', width: '100%' }}>
            <MapPin style={{ width: '20px', height: '20px' }} />
            Filter by Location
          </button>
        </div>

        {/* Objects & Scenery Filter */}
        <div>
          <button
            onClick={() => setIsSubFilterOpen(!isSubFilterOpen)}
            style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '10px', border: '1px solid gray', borderRadius: '5px', background: 'none', color: '#fff', width: '100%' }}
          >
            <Image style={{ width: '20px', height: '20px' }} />
            Filter by Objects & Scenery
          </button>
          {isSubFilterOpen && (
            <div style={{ marginLeft: '20px', marginTop: '10px' }}>
              {/* Scenery Filter */}
              <button style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '10px', border: '1px solid gray', borderRadius: '5px', background: 'none', color: '#fff', width: '100%' }}>
                Scenery
              </button>
              {/* Objects Filter */}
              <button style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '10px', border: '1px solid gray', borderRadius: '5px', background: 'none', color: '#fff', width: '100%' }}>
                Objects
              </button>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default Sidebar;