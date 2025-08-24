
import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloudIcon } from './Icons';

interface FileUploadProps {
  onFilesAdded: (files: File[]) => void;
}

export const FileUpload: React.FC<FileUploadProps> = ({ onFilesAdded }) => {
  const [isDragging, setIsDragging] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    onFilesAdded(acceptedFiles);
    setIsDragging(false);
  }, [onFilesAdded]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    onDragEnter: () => setIsDragging(true),
    onDragLeave: () => setIsDragging(false),
  });

  return (
    <div
      {...getRootProps()}
      className={`h-full border-2 border-dashed rounded-lg flex flex-col justify-center items-center text-center p-4 cursor-pointer transition-colors duration-200 ${
        isDragActive || isDragging ? 'border-indigo-500 bg-indigo-900/20' : 'border-gray-600 hover:border-gray-500'
      }`}
    >
      <input {...getInputProps()} />
      <UploadCloudIcon className="w-10 h-10 text-gray-500 mb-2" />
      {isDragActive ? (
        <p className="text-indigo-400">Drop the files here ...</p>
      ) : (
        <>
          <p className="font-semibold">Drag & drop files here, or click to select</p>
          <p className="text-sm text-gray-400">Supported formats: PDF, DOCX, TXT</p>
        </>
      )}
    </div>
  );
};
