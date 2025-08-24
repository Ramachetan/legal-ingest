
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
  const [qdrantCollectionName, setQdrantCollectionName] = useState<string>('legal_documents');

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
        }, qdrantUrl, qdrantApiKey, qdrantCollectionName);
    }
    
    setIsProcessing(false);
  }, [files, isProcessing, selectedFile, qdrantUrl, qdrantApiKey, qdrantCollectionName]);


  const handleClearAll = () => {
    setFiles([]);
    setSelectedFile(null);
    setIsProcessing(false);
  };
  
  const pendingFileCount = files.filter(f => f.status === 'pending').length;
  const canProcess = !isProcessing && pendingFileCount > 0 && !!qdrantUrl && !!qdrantApiKey && !!qdrantCollectionName;

  return (
    <div className="min-h-screen bg-gray-900 text-gray-200 font-sans flex flex-col">
      <header className="bg-gray-800/50 backdrop-blur-sm border-b border-gray-700 shadow-lg sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-white tracking-wider">Legal Document Ingestion Pipeline</h1>
          <div className="flex items-center space-x-4">
            <button
              onClick={handleProcessAll}
              disabled={!canProcess}
              className="px-4 py-2 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-500 disabled:bg-indigo-800 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors duration-200 flex items-center space-x-2"
            >
              {isProcessing ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Processing...
                </>
              ) : (
                `Process ${pendingFileCount} Files`
              )}
            </button>
            <button
              onClick={handleClearAll}
              className="px-4 py-2 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-500 disabled:bg-gray-600 transition-colors duration-200"
            >
              Clear All
            </button>
          </div>
        </div>
      </header>
      
      <main className="flex-grow container mx-auto p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 flex flex-col gap-6">
          <div className="bg-gray-800 rounded-lg shadow-xl p-6 h-64">
            <h2 className="text-lg font-semibold mb-4 flex items-center"><UploadCloudIcon className="w-6 h-6 mr-2" /> 1. Upload Documents</h2>
            <FileUpload onFilesAdded={handleFilesAdded} />
          </div>

          <div className="bg-gray-800 rounded-lg shadow-xl p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center"><CogIcon className="w-6 h-6 mr-2" /> 2. Configure Database</h2>
            <div className="space-y-4">
              <div>
                <label htmlFor="qdrant-url" className="block text-sm font-medium text-gray-300 mb-1">Qdrant Cloud URL</label>
                <input 
                  type="text" 
                  id="qdrant-url"
                  value={qdrantUrl}
                  onChange={(e) => setQdrantUrl(e.target.value)}
                  placeholder="https://xyz.gcp.cloud.qdrant.io"
                  className="w-full bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-sm text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div>
                <label htmlFor="qdrant-key" className="block text-sm font-medium text-gray-300 mb-1">Qdrant API Key</label>
                <input 
                  type="password"
                  id="qdrant-key"
                  value={qdrantApiKey}
                  onChange={(e) => setQdrantApiKey(e.target.value)}
                  placeholder="******************"
                  className="w-full bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-sm text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div>
                <label htmlFor="qdrant-collection" className="block text-sm font-medium text-gray-300 mb-1">Collection Name</label>
                <input 
                  type="text" 
                  id="qdrant-collection"
                  value={qdrantCollectionName}
                  onChange={(e) => setQdrantCollectionName(e.target.value)}
                  placeholder="e.g., legal_documents"
                  className="w-full bg-gray-700 border border-gray-600 rounded-md px-3 py-2 text-sm text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div className="flex items-start space-x-2 text-xs text-gray-400 pt-2">
                <InfoIcon className="w-4 h-4 flex-shrink-0 mt-0.5" />
                <p>In a production app, these secrets should be managed securely on a backend server, not exposed in the frontend.</p>
              </div>
            </div>
          </div>
          
          <div className="bg-gray-800 rounded-lg shadow-xl p-6 flex-grow">
            <h2 className="text-lg font-semibold mb-4">3. Document Queue ({files.length})</h2>
            <FileProgressList files={files} onFileSelect={handleFileSelect} selectedFileId={selectedFile?.id} />
          </div>
        </div>
        
        <div className="lg:col-span-2 bg-gray-800 rounded-lg shadow-xl p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center"><DatabaseIcon className="w-6 h-6 mr-2" /> 4. Processing & Indexing Pipeline</h2>
          <ProcessingDetailView file={selectedFile} />
        </div>
      </main>
    </div>
  );
};

export default App;