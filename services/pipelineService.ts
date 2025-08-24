
import { QdrantClient } from '@qdrant/js-client-rest';
import type { ProcessedFile, DocumentChunk } from '../types';
import { generateLegalText } from './geminiService';

const CHUNK_SIZE = 1000;
const CHUNK_OVERLAP = 200;
const VECTOR_DIMENSION = 768; // A common dimension for sentence-transformer models

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
  qdrantApiKey: string,
  collectionName: string
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

    // 4. Generate Embeddings (Simulated with random vectors)
    currentFileState = updateStepStatus(currentFileState, 'Generate Embeddings', 'in-progress');
    onUpdate(currentFileState);
    for (let j = 0; j < currentFileState.chunks.length; j++) {
      await simulateProcessing(50); // Simulate API call per chunk
      const fakeEmbedding = Array.from({ length: VECTOR_DIMENSION }, () => Math.random() * 2 - 1);
      currentFileState.chunks[j].embedding = fakeEmbedding;
      currentFileState.chunks[j].embeddingStatus = 'completed';
      onUpdate({ ...currentFileState });
    }
    currentFileState = updateStepStatus(currentFileState, 'Generate Embeddings', 'completed', `Embeddings created for ${currentFileState.chunks.length} chunks.`);
    onUpdate(currentFileState);

    // 5. Store in Qdrant
    currentFileState = updateStepStatus(currentFileState, 'Store in Qdrant', 'in-progress');
    onUpdate(currentFileState);
    if (!qdrantUrl || !qdrantApiKey || !collectionName) {
      throw new Error("Qdrant URL, API Key, and Collection Name must be provided.");
    }
    
    const client = new QdrantClient({ 
        url: qdrantUrl, 
        apiKey: qdrantApiKey,
        checkCompatibility: false,
    });
    
    currentFileState = updateStepStatus(currentFileState, 'Store in Qdrant', 'in-progress', 'Connecting to Qdrant cluster...');
    onUpdate(currentFileState);

    // Check if collection exists, create if not
    const collectionsResult = await client.getCollections();
    const collectionExists = collectionsResult.collections.some(c => c.name === collectionName);
    
    if (!collectionExists) {
        currentFileState = updateStepStatus(currentFileState, 'Store in Qdrant', 'in-progress', `Collection '${collectionName}' not found. Creating...`);
        onUpdate(currentFileState);
        await client.createCollection(collectionName, {
            vectors: { size: VECTOR_DIMENSION, distance: 'Cosine' },
        });
        await simulateProcessing(1000); // Give Qdrant a moment to initialize the collection
    }

    currentFileState = updateStepStatus(currentFileState, 'Store in Qdrant', 'in-progress', `Upserting ${currentFileState.chunks.length} vectors...`);
    onUpdate(currentFileState);
    
    const points = currentFileState.chunks.map(chunk => {
        if (!chunk.embedding) {
            throw new Error(`Chunk ${chunk.id} is missing an embedding.`);
        }
        return {
            id: chunk.id,
            vector: chunk.embedding,
            payload: {
                text: chunk.text,
                ...chunk.metadata
            }
        };
    });

    // Upsert in batches
    const BATCH_SIZE = 100;
    for (let i = 0; i < points.length; i += BATCH_SIZE) {
        const batch = points.slice(i, i + BATCH_SIZE);
        await client.upsert(collectionName, {
            wait: true,
            points: batch,
        });

        // Update progress for chunks in UI after each batch
        for (let j = 0; j < batch.length; j++) {
            const chunkIndex = i + j;
            if(currentFileState.chunks[chunkIndex]) {
                currentFileState.chunks[chunkIndex].storageStatus = 'completed';
            }
        }
        onUpdate({ ...currentFileState });
    }

    currentFileState = updateStepStatus(currentFileState, 'Store in Qdrant', 'completed', `${currentFileState.chunks.length} vectors stored in '${collectionName}'.`);
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