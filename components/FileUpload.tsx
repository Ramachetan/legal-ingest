
import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloudIcon } from './Icons';

interface FileUploadProps {
  onFilesAdded: (files: File[]) => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onFilesAdded }) => {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    onFilesAdded(acceptedFiles);
  }, [onFilesAdded]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    multiple: true,
    onDragEnter: () => {},
    onDragOver: () => {},
    onDragLeave: () => {},
  });

  return (
    <div
      {...getRootProps()}
      className={`upload-area ${
        isDragActive ? 'drag-active' : ''
      }`}
    >
      <input {...getInputProps()} />
      <UploadCloudIcon style={{width: '48px', height: '48px', color: '#64748b', marginBottom: '12px'}} />
      {isDragActive ? (
        <p style={{color: '#3b82f6', fontWeight: '600'}}>Drop the files here ...</p>
      ) : (
        <>
          <p style={{fontWeight: '600', marginBottom: '8px'}}>Drag & drop files here, or click to select</p>
          <p className="text-sm text-gray-400">Supported formats: PDF, DOCX, TXT</p>
        </>
      )}
    </div>
  );
};
