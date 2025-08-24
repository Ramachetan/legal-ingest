
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
    <div className="flex flex-col h-full">
      {files.length === 0 ? (
        <div className="flex-grow flex items-center justify-center text-gray-500">
          <p>Upload documents to begin.</p>
        </div>
      ) : (
        <div className="overflow-y-auto pr-2 flex-grow">
          <ul className="space-y-3">
            {files.map(file => (
              <li key={file.id}>
                <FileItem
                  file={file}
                  onSelect={() => onFileSelect(file)}
                  isSelected={selectedFileId === file.id}
                />
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
