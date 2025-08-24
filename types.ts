
export type ProcessingStatus = 'pending' | 'in-progress' | 'completed' | 'failed';

export interface ProcessingStep {
  name: string;
  status: ProcessingStatus;
  details?: string;
}

export interface DocumentChunk {
  id: string;
  fileId: string;
  chunkIndex: number;
  text: string;
  metadata: {
    file_name: string;
    file_path: string;
    file_type: string;
    chunk_size: number;
    chunk_overlap: number;
  };
  embeddingStatus: ProcessingStatus;
  storageStatus: ProcessingStatus;
}

export interface ProcessedFile {
  id: string;
  file: File;
  status: ProcessingStatus;
  steps: ProcessingStep[];
  chunks: DocumentChunk[];
  extractedText: string | null;
  cleanedText: string | null;
  error?: string;
}
