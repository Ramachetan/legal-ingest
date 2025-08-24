import type { ProcessedFile, ProcessingStep, DocumentChunk } from '../types';
import { generateLegalText } from './geminiService';

const CHUNK_SIZE = 1000;
const CHUNK_OVERLAP = 200;

// Helper to simulate async operations and update state
const simulateProcessing = (duration: number) => new Promise(resolve => setTimeout(resolve, duration));

const updateStepStatus = (
  file: ProcessedFile,
  stepName: string,
  status: 'in-progress' | 'completed' | 'failed',
  details?: string
): ProcessedFile => {
  const newSteps = file.steps.map(step =>
    step.name === stepName ? { ...step, status, details } : step
  );
  return { ...file, steps: newSteps };
};

export const processFile = async (
  fileToProcess: ProcessedFile,
  onUpdate: (file: ProcessedFile) => void,
  qdrantUrl: string,
  qdrantApiKey: string
): Promise<void> => {
  let currentFileState: ProcessedFile = { ...fileToProcess, status: 'in-progress' };

  try {
    // 1. Extract Text
    currentFileState = updateStepStatus(currentFileState, 'Extract Text', 'in-progress');
    onUpdate(currentFileState);
    await simulateProcessing(1000);
    const extractedText = await generateLegalText(currentFileState.file.name);
    currentFileState = { ...currentFileState, extractedText };
    currentFileState = updateStepStatus(currentFileState, 'Extract Text', 'completed', `${extractedText.length.toLocaleString()} chars extracted.`);
    onUpdate(currentFileState);

    // 2. Clean Text
    currentFileState = updateStepStatus(currentFileState, 'Clean Text', 'in-progress');
    onUpdate(currentFileState);
    await simulateProcessing(500);
    const cleanedText = extractedText.replace(/\s+/g, ' ').trim();
    currentFileState = { ...currentFileState, cleanedText };
    currentFileState = updateStepStatus(currentFileState, 'Clean Text', 'completed');
    onUpdate(currentFileState);

    // 3. Chunk Text
    currentFileState = updateStepStatus(currentFileState, 'Chunk Text', 'in-progress');
    onUpdate(currentFileState);
    await simulateProcessing(800);
    const chunks: DocumentChunk[] = [];
    let i = 0;
    let chunkIndex = 0;
    while (i < cleanedText.length) {
      const end = i + CHUNK_SIZE;
      const chunkText = cleanedText.substring(i, end);
      chunks.push({
        id: `${currentFileState.id}-chunk-${chunkIndex}`,
        fileId: currentFileState.id,
        chunkIndex: chunkIndex + 1,
        text: chunkText,
        metadata: {
          file_name: currentFileState.file.name,
          file_path: currentFileState.file.webkitRelativePath || currentFileState.file.name,
          file_type: currentFileState.file.type,
          chunk_size: CHUNK_SIZE,
          chunk_overlap: CHUNK_OVERLAP,
        },
        embeddingStatus: 'pending',
        storageStatus: 'pending',
      });
      i += CHUNK_SIZE - CHUNK_OVERLAP;
      chunkIndex++;
    }
    currentFileState = { ...currentFileState, chunks };
    currentFileState = updateStepStatus(currentFileState, 'Chunk Text', 'completed', `${chunks.length} chunks created.`);
    onUpdate(currentFileState);

    // 4. Generate Embeddings
    currentFileState = updateStepStatus(currentFileState, 'Generate Embeddings', 'in-progress');
    onUpdate(currentFileState);
    for (let j = 0; j < currentFileState.chunks.length; j++) {
      await simulateProcessing(150); // Simulate API call per chunk
      currentFileState.chunks[j].embeddingStatus = 'completed';
      onUpdate({ ...currentFileState });
    }
    currentFileState = updateStepStatus(currentFileState, 'Generate Embeddings', 'completed', `Embeddings created for ${chunks.length} chunks.`);
    onUpdate(currentFileState);

    // 5. Store in Qdrant
    currentFileState = updateStepStatus(currentFileState, 'Store in Qdrant', 'in-progress');
    onUpdate(currentFileState);
    if (!qdrantUrl || !qdrantApiKey) {
      throw new Error("Qdrant URL and API Key must be provided.");
    }
    await simulateProcessing(500); // Simulate network latency
    currentFileState = updateStepStatus(currentFileState, 'Store in Qdrant', 'in-progress', 'Connecting to Qdrant cluster...');
    onUpdate(currentFileState);
    await simulateProcessing(1000); // Simulate connection handshake

    for (let j = 0; j < currentFileState.chunks.length; j++) {
      await simulateProcessing(50); // Simulate DB insertion per chunk
      currentFileState.chunks[j].storageStatus = 'completed';
      onUpdate({ ...currentFileState });
    }
    currentFileState = updateStepStatus(currentFileState, 'Store in Qdrant', 'completed', `${chunks.length} vectors stored.`);
    onUpdate(currentFileState);

    // Finalize
    currentFileState.status = 'completed';
    onUpdate(currentFileState);

  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred.';
    console.error(`Failed to process ${fileToProcess.file.name}:`, error);

    const inProgressStep = currentFileState.steps.find(s => s.status === 'in-progress');
    
    let finalState: ProcessedFile = { 
      ...currentFileState, 
      status: 'failed', 
      error: errorMessage 
    };

    if (inProgressStep) {
        finalState = updateStepStatus(finalState, inProgressStep.name, 'failed', errorMessage);
    }
    
    onUpdate(finalState);
  }
};