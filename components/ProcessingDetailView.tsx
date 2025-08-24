
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
  switch (status) {
    case 'completed':
      return <CheckCircleIcon className="w-5 h-5 text-green-400" />;
    case 'failed':
      return <XCircleIcon className="w-5 h-5 text-red-400" />;
    case 'in-progress':
      return <LoaderIcon className="w-5 h-5 text-blue-400 animate-spin" />;
    case 'pending':
    default:
      return <ClockIcon className="w-5 h-5 text-yellow-400" />;
  }
};

const PipelineStep: React.FC<{ step: ProcessingStep }> = ({ step }) => (
  <div className="flex items-center space-x-3 bg-gray-700/50 p-3 rounded-lg">
    <StatusIcon status={step.status} />
    <div className="flex-grow">
      <p className="font-medium text-gray-200">{step.name}</p>
      {step.details && <p className="text-xs text-gray-400">{step.details}</p>}
    </div>
  </div>
);

const ChunkItem: React.FC<{ chunk: DocumentChunk }> = ({ chunk }) => (
  <div className="bg-gray-700/50 p-3 rounded-lg">
    <div className="flex justify-between items-center mb-2">
      <p className="font-mono text-sm text-indigo-400">Chunk #{chunk.chunkIndex}</p>
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-1.5 text-xs text-gray-400" title="Embedding Status">
            <CpuChipIcon className={`w-4 h-4 ${chunk.embeddingStatus === 'completed' ? 'text-green-400' : 'text-gray-500'}`} />
            <span>Embedding</span>
        </div>
        <div className="flex items-center space-x-1.5 text-xs text-gray-400" title="Storage Status">
            <DatabaseIcon className={`w-4 h-4 ${chunk.storageStatus === 'completed' ? 'text-green-400' : 'text-gray-500'}`} />
            <span>Qdrant</span>
        </div>
      </div>
    </div>
    <p className="text-sm text-gray-300 line-clamp-3 hover:line-clamp-none transition-all">
      {chunk.text}
    </p>
  </div>
);


export const ProcessingDetailView: React.FC<{ file: ProcessedFile | null }> = ({ file }) => {
  if (!file) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-center text-gray-500">
        <DatabaseIcon className="w-16 h-16 mb-4" />
        <p className="text-lg">Select a file to view its processing details</p>
        <p>Or click "Process Files" to start the ingestion.</p>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col space-y-6 overflow-hidden">
      <div>
        <h3 className="text-base font-semibold mb-2 text-indigo-400">Processing Status for:</h3>
        <p className="text-lg font-bold text-gray-100 truncate">{file.file.name}</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {file.steps.map((step, index) => (
          <PipelineStep key={index} step={step} />
        ))}
      </div>

      <div className="flex-grow flex flex-col min-h-0">
        <h3 className="text-base font-semibold mb-3 text-indigo-400">Indexed Chunks in Qdrant ({file.chunks.length})</h3>
        {file.chunks.length > 0 ? (
          <div className="overflow-y-auto space-y-3 pr-2 flex-grow">
            {file.chunks.map(chunk => (
              <ChunkItem key={chunk.id} chunk={chunk} />
            ))}
          </div>
        ) : (
          <div className="flex-grow flex items-center justify-center text-gray-500 bg-gray-900/50 rounded-lg">
            <p>Chunks will appear here once the 'Chunk Text' step is complete.</p>
          </div>
        )}
      </div>
    </div>
  );
};
