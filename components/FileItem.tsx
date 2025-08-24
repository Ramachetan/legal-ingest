
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
  const iconStyle = {width: '24px', height: '24px'};
  if (fileName.endsWith('.pdf')) return <FileCodeIcon style={{...iconStyle, color: '#f87171'}} />;
  if (fileName.endsWith('.docx')) return <FileTextIcon style={{...iconStyle, color: '#60a5fa'}} />;
  if (fileName.endsWith('.txt')) return <FileTextIcon style={{...iconStyle, color: '#9ca3af'}} />;
  return <FileTextIcon style={{...iconStyle, color: '#9ca3af'}} />;
};

const getStatusIcon = (status: ProcessedFile['status']) => {
  const iconStyle = {width: '20px', height: '20px'};
  switch (status) {
    case 'completed':
      return <CheckCircleIcon style={{...iconStyle, color: '#10b981'}} />;
    case 'failed':
      return <XCircleIcon style={{...iconStyle, color: '#ef4444'}} />;
    case 'in-progress':
      return <LoaderIcon style={{...iconStyle, color: '#3b82f6'}} className="animate-spin" />;
    case 'pending':
      return <ClockIcon style={{...iconStyle, color: '#f59e0b'}} />;
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
      style={{
        width: '100%',
        textAlign: 'left',
        padding: '16px',
        borderRadius: '12px',
        transition: 'all 0.2s ease',
        display: 'flex',
        alignItems: 'center',
        gap: '16px',
        border: 'none',
        cursor: 'pointer',
        background: isSelected ? 
          'linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(99, 102, 241, 0.2) 100%)' : 
          'rgba(51, 65, 85, 0.6)',
        color: '#f1f5f9',
      }}
      onMouseEnter={(e) => {
        if (!isSelected) {
          e.currentTarget.style.background = 'rgba(51, 65, 85, 0.8)';
        }
      }}
      onMouseLeave={(e) => {
        if (!isSelected) {
          e.currentTarget.style.background = 'rgba(51, 65, 85, 0.6)';
        }
      }}
    >
      <div style={{flexShrink: 0}}>{getFileIcon(file.file.name)}</div>
      <div style={{flexGrow: 1, minWidth: 0}}>
        <p style={{
          fontSize: '14px',
          fontWeight: '500',
          color: '#f1f5f9',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap'
        }}>
          {file.file.name}
        </p>
        <div className="progress-bar">
          <div
            className={file.status === 'completed' ? 'progress-completed' : 'progress-active'}
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>
      <div style={{flexShrink: 0}}>{getStatusIcon(file.status)}</div>
    </button>
  );
};
