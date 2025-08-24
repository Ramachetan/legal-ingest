
import React from 'react';
import type { ProcessedFile, DocumentChunk, ProcessingStep } from '../types';
import {
  CheckCircleIcon,
  XCircleIcon,
  LoaderIcon,
  ClockIcon,
  DatabaseIcon,
  CpuChipIcon
} from './Icons';

const StatusIcon: React.FC<{ status: ProcessingStep['status'] }> = ({ status }) => {
  const iconStyle = {width: '20px', height: '20px'};
  switch (status) {
    case 'completed':
      return <CheckCircleIcon style={{...iconStyle, color: '#10b981'}} />;
    case 'failed':
      return <XCircleIcon style={{...iconStyle, color: '#ef4444'}} />;
    case 'in-progress':
      return <LoaderIcon style={{...iconStyle, color: '#3b82f6'}} className="animate-spin" />;
    case 'pending':
    default:
      return <ClockIcon style={{...iconStyle, color: '#f59e0b'}} />;
  }
};

const PipelineStep: React.FC<{ step: ProcessingStep }> = ({ step }) => (
  <div style={{
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    background: 'rgba(51, 65, 85, 0.6)',
    padding: '16px',
    borderRadius: '12px',
    border: '1px solid rgba(148, 163, 184, 0.1)',
    transition: 'all 0.2s ease'
  }}>
    <StatusIcon status={step.status} />
    <div style={{flexGrow: 1}}>
      <p style={{fontWeight: '500', color: '#f1f5f9', marginBottom: '4px'}}>{step.name}</p>
      {step.details && <p style={{fontSize: '12px', color: '#94a3b8'}}>{step.details}</p>}
    </div>
  </div>
);

const ChunkItem: React.FC<{ chunk: DocumentChunk }> = ({ chunk }) => (
  <div style={{
    background: 'rgba(51, 65, 85, 0.6)',
    padding: '16px',
    borderRadius: '12px',
    border: '1px solid rgba(148, 163, 184, 0.1)',
    transition: 'all 0.2s ease'
  }}>
    <div style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: '12px'
    }}>
      <p style={{
        fontFamily: 'monospace',
        fontSize: '14px',
        color: '#6366f1',
        fontWeight: '600'
      }}>
        Chunk #{chunk.chunkIndex}
      </p>
      <div style={{display: 'flex', alignItems: 'center', gap: '16px'}}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '12px',
          color: '#94a3b8'
        }} title="Embedding Status">
          <CpuChipIcon style={{
            width: '16px',
            height: '16px',
            color: chunk.embeddingStatus === 'completed' ? '#10b981' : '#6b7280'
          }} />
          <span>Embedding</span>
        </div>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '12px',
          color: '#94a3b8'
        }} title="Storage Status">
          <DatabaseIcon style={{
            width: '16px',
            height: '16px',
            color: chunk.storageStatus === 'completed' ? '#10b981' : '#6b7280'
          }} />
          <span>Qdrant</span>
        </div>
      </div>
    </div>
    <p style={{
      fontSize: '14px',
      color: '#cbd5e1',
      lineHeight: '1.4',
      overflow: 'hidden',
      display: '-webkit-box',
      WebkitLineClamp: 3,
      WebkitBoxOrient: 'vertical',
      cursor: 'pointer',
      transition: 'all 0.2s ease'
    }}
    onClick={(e) => {
      const element = e.currentTarget;
      if (element.style.WebkitLineClamp === '3') {
        element.style.WebkitLineClamp = 'none';
      } else {
        element.style.WebkitLineClamp = '3';
      }
    }}>
      {chunk.text}
    </p>
  </div>
);


export const ProcessingDetailView: React.FC<{ file: ProcessedFile | null }> = ({ file }) => {
  if (!file) {
    return (
      <div style={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        color: '#6b7280'
      }}>
        <DatabaseIcon style={{width: '64px', height: '64px', marginBottom: '16px'}} />
        <p style={{fontSize: '18px', marginBottom: '8px'}}>Select a file to view its processing details</p>
        <p>Or click "Process Files" to start the ingestion.</p>
      </div>
    );
  }

  return (
    <div style={{
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      gap: '24px',
      overflow: 'hidden'
    }}>
      <div>
        <h3 style={{
          fontSize: '16px',
          fontWeight: '600',
          marginBottom: '8px',
          color: '#6366f1'
        }}>Processing Status for:</h3>
        <p style={{
          fontSize: '18px',
          fontWeight: '700',
          color: '#f1f5f9',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap'
        }}>{file.file.name}</p>
      </div>
      
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
        gap: '12px'
      }}>
        {file.steps.map((step, index) => (
          <PipelineStep key={index} step={step} />
        ))}
      </div>

      <div style={{
        flexGrow: 1,
        display: 'flex',
        flexDirection: 'column',
        minHeight: 0
      }}>
        <h3 style={{
          fontSize: '16px',
          fontWeight: '600',
          marginBottom: '12px',
          color: '#6366f1'
        }}>Indexed Chunks in Qdrant ({file.chunks.length})</h3>
        {file.chunks.length > 0 ? (
          <div style={{
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px',
            paddingRight: '8px',
            flexGrow: 1
          }}>
            {file.chunks.map(chunk => (
              <ChunkItem key={chunk.id} chunk={chunk} />
            ))}
          </div>
        ) : (
          <div style={{
            flexGrow: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#6b7280',
            background: 'rgba(17, 24, 39, 0.5)',
            borderRadius: '12px',
            padding: '32px'
          }}>
            <p>Chunks will appear here once the 'Chunk Text' step is complete.</p>
          </div>
        )}
      </div>
    </div>
  );
};
