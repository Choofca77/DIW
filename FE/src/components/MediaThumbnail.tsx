import React from 'react';
import { Media } from '../types/Media';

interface Props {
  media: Media;
  isExpanded: boolean;
  onExpand: () => void;
  onCollapse: () => void;
}

const MediaThumbnail: React.FC<Props> = ({ media, isExpanded, onExpand, onCollapse }) => {
  const handleClick = () => {
    if (isExpanded) {
      onCollapse();
    } else {
      onExpand();
    }
  };

  return (
    <div 
      className={`
        relative transition-all duration-300 ease-in-out cursor-pointer
        ${isExpanded ? 'fixed inset-0 z-50 bg-black/80' : 'mb-4'}
      `}
      onClick={handleClick}
    >
      {media.type === 'image' ? (
        <img
          src={isExpanded ? media.path : media.thumbnail}
          alt=""
          className={`
            rounded-lg object-cover transition-all duration-300
            ${isExpanded ? 'w-full h-full object-contain' : 'w-full aspect-square'}
          `}
          loading="lazy"
        />
      ) : (
        <video
          src={isExpanded ? media.path : media.thumbnail}
          controls={isExpanded}
          muted
          className={`
            rounded-lg object-cover transition-all duration-300
            ${isExpanded ? 'w-full h-full object-contain' : 'w-full aspect-square'}
          `}
        />
      )}
    </div>
  );
};

export default MediaThumbnail;