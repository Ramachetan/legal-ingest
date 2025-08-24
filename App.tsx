
import React, { useState, useCallback } from 'react';
import { FileUpload } from './components/FileUpload';
import { FileProgressList } from './components/FileProgressList';
import { ProcessingDetailView } from './components/ProcessingDetailView';
import { DatabaseIcon, UploadCloudIcon, CogIcon, InfoIcon } from './components/Icons';
import type { ProcessedFile, DocumentChunk } from './types';
import { processFile } from './services/pipelineService';

const App: React.FC = () => {
  const [files, setFiles] = useState<ProcessedFile[]>([]);
  const [selectedFile, setSelectedFile] = useState<ProcessedFile | null>(null);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [qdrantUrl, setQdrantUrl] = useState<string>('');
  const [qdrantApiKey, setQdrantApiKey] = useState<string>('');

  const handleFileSelect = (file: ProcessedFile) => {
    setSelectedFile(file);
  };
  
  const handleFilesAdded = (newFiles: File[]) => {
    const processedFiles: ProcessedFile[] = newFiles.map((file, index) => ({
      id: `${file.name}-${Date.now()}-${index}`,
      file,
      status: 'pending',
      steps: [
        { name: 'Extract Text', status: 'pending' },
        { name: 'Clean Text', status: 'pending' },
        { name: 'Chunk Text', status: 'pending' },
        { name: 'Generate Embeddings', status: 'pending' },
        { name: 'Store in Qdrant', status: 'pending' },
      ],
      chunks: [],
      extractedText: null,
      cleanedText: null
    }));
    setFiles(prevFiles => [...prevFiles, ...processedFiles]);
  };

  const handleProcessAll = useCallback(async () => {
    if (isProcessing) return;
    setIsProcessing(true);
    setSelectedFile(null);

    const pendingFiles = files.filter(f => f.status === 'pending');
    
    for (const file of pendingFiles) {
        await processFile(file, (updatedFile) => {
            setFiles(prevFiles => prevFiles.map(f => f.id === updatedFile.id ? updatedFile : f));
            if (selectedFile?.id === updatedFile.id || !selectedFile) {
                setSelectedFile(updatedFile);
            }
        }, qdrantUrl, qdrantApiKey);
    }
    
    setIsProcessing(false);
  }, [files, isProcessing, selectedFile, qdrantUrl, qdrantApiKey]);


  const handleClearAll = () => {
    setFiles([]);
    setSelectedFile(null);
    setIsProcessing(false);
  };
  
  const pendingFileCount = files.filter(f => f.status === 'pending').length;
  const canProcess = !isProcessing && pendingFileCount > 0 && !!qdrantUrl && !!qdrantApiKey;

  return (
    <div className="min-h-screen flex flex-col">
      <header className="header">
        <div className="container flex justify-between items-center">
          <h1 className="title">Legal Document Ingestion Pipeline</h1>
          <div className="flex items-center space-x-4">
            <button
              onClick={handleProcessAll}
              disabled={!canProcess}
              className="btn btn-primary"
            >
              {isProcessing ? (
                <>
                  <div className="loading-spinner animate-spin"></div>
                  Processing...
                </>
              ) : (
                `Process ${pendingFileCount} Files`
              )}
            </button>
            <button
              onClick={handleClearAll}
              className="btn btn-danger"
            >
              Clear All
            </button>
          </div>
        </div>
      </header>
      
      <main className="flex-grow container p-6 grid grid-cols-1 lg-grid-cols-3 gap-6">
        <div className="flex flex-col space-y-6">
          <div className="modern-card h-64">
            <h2 className="section-title"><UploadCloudIcon className="w-6 h-6 mr-2" /> 1. Upload Documents</h2>
            <FileUpload onFilesAdded={handleFilesAdded} />
          </div>

          <div className="modern-card">
            <h2 className="section-title"><CogIcon className="w-6 h-6 mr-2" /> 2. Configure Database</h2>
            <div className="space-y-4">
              <div className="form-group">
                <label htmlFor="qdrant-url" className="label">Qdrant Cloud URL</label>
                <input 
                  type="text" 
                  id="qdrant-url"
                  value={qdrantUrl}
                  onChange={(e) => setQdrantUrl(e.target.value)}
                  placeholder="https://xyz.gcp.cloud.qdrant.io"
                  className="input"
                />
              </div>
              <div className="form-group">
                <label htmlFor="qdrant-key" className="label">Qdrant API Key</label>
                <input 
                  type="password"
                  id="qdrant-key"
                  value={qdrantApiKey}
                  onChange={(e) => setQdrantApiKey(e.target.value)}
                  placeholder="******************"
                  className="input"
                />
              </div>
              <div className="info-box">
                <InfoIcon className="w-4 h-4 flex-shrink-0 mt-0.5" />
                <p>In a production app, these secrets should be managed securely on a backend server, not exposed in the frontend.</p>
              </div>
            </div>
          </div>
          
          <div className="modern-card flex-grow">
            <h2 className="section-title">3. Document Queue ({files.length})</h2>
            <FileProgressList files={files} onFileSelect={handleFileSelect} selectedFileId={selectedFile?.id} />
          </div>
        </div>
        
        <div className="modern-card">
          <h2 className="section-title"><DatabaseIcon className="w-6 h-6 mr-2" /> 4. Processing & Indexing Pipeline</h2>
          <ProcessingDetailView file={selectedFile} />
        </div>
      </main>
    </div>
  );
};

export default App;
