
import React from 'react';
import type { ProcessedFile } from '../types';
import { FileItem } from './FileItem';

interface FileProgressListProps {
  files: ProcessedFile[];
  onFileSelect: (file: ProcessedFile) => void;
  selectedFileId?: string | null;
}

export const FileProgressList: React.FC<FileProgressListProps> = ({ files, onFileSelect, selectedFileId }) => {
  return (
    <div className="flex flex-col" style={{height: '100%'}}>
      {files.length === 0 ? (
        <div className="flex-grow flex items-center justify-center text-gray-500">
          <p>Upload documents to begin.</p>
        </div>
      ) : (
        <div style={{overflowY: 'auto', paddingRight: '8px', height: '100%'}}>
          <div style={{display: 'flex', flexDirection: 'column', gap: '12px'}}>
            {files.map(file => (
              <FileItem
                key={file.id}
                file={file}
                onSelect={() => onFileSelect(file)}
                isSelected={selectedFileId === file.id}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
