
import React from 'react';
import type { ProcessedFile } from '../types';
import {
  FileTextIcon,
  FileCodeIcon,
  CheckCircleIcon,
  XCircleIcon,
  LoaderIcon,
  ClockIcon
} from './Icons';

interface FileItemProps {
  file: ProcessedFile;
  onSelect: () => void;
  isSelected: boolean;
}

const getFileIcon = (fileName: string) => {
  if (fileName.endsWith('.pdf')) return <FileCodeIcon className="w-6 h-6 text-red-400" />;
  if (fileName.endsWith('.docx')) return <FileTextIcon className="w-6 h-6 text-blue-400" />;
  if (fileName.endsWith('.txt')) return <FileTextIcon className="w-6 h-6 text-gray-400" />;
  return <FileTextIcon className="w-6 h-6 text-gray-400" />;
};

const getStatusIcon = (status: ProcessedFile['status']) => {
  switch (status) {
    case 'completed':
      return <CheckCircleIcon className="w-5 h-5 text-green-400" />;
    case 'failed':
      return <XCircleIcon className="w-5 h-5 text-red-400" />;
    case 'in-progress':
      return <LoaderIcon className="w-5 h-5 text-blue-400 animate-spin" />;
    case 'pending':
      return <ClockIcon className="w-5 h-5 text-yellow-400" />;
    default:
      return null;
  }
};

export const FileItem: React.FC<FileItemProps> = ({ file, onSelect, isSelected }) => {
  const completedSteps = file.steps.filter(s => s.status === 'completed').length;
  const totalSteps = file.steps.length;
  const progress = totalSteps > 0 ? (completedSteps / totalSteps) * 100 : 0;

  return (
    <button
      onClick={onSelect}
      className={`w-full text-left p-3 rounded-lg transition-colors duration-200 flex items-center space-x-4 ${
        isSelected ? 'bg-indigo-900/50' : 'bg-gray-700/50 hover:bg-gray-700'
      }`}
    >
      <div className="flex-shrink-0">{getFileIcon(file.file.name)}</div>
      <div className="flex-grow min-w-0">
        <p className="text-sm font-medium text-gray-200 truncate">{file.file.name}</p>
        <div className="w-full bg-gray-600 rounded-full h-1.5 mt-1.5">
          <div
            className={`h-1.5 rounded-full transition-all duration-500 ${
              file.status === 'completed' ? 'bg-green-500' : 'bg-indigo-500'
            }`}
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>
      <div className="flex-shrink-0">{getStatusIcon(file.status)}</div>
    </button>
  );
};
