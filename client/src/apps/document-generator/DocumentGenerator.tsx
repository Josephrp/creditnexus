/**
 * Document Generator - Main component for LMA template generation.
 * 
 * Allows users to:
 * - Select an LMA template
 * - Input or import CDM data
 * - Generate documents from templates
 * - Preview and export generated documents
 */

import { useState, useEffect, useCallback } from 'react';
import { fetchWithAuth, useAuth } from '../../context/AuthContext';
import { useFDC3 } from '../../context/FDC3Context';
import type { GeneratedDocumentContext, CreditAgreementData as FDC3CreditAgreementData } from '../../context/FDC3Context';
import { Loader2, FileText, Sparkles, AlertCircle, CheckCircle2, Merge, Info } from 'lucide-react';
import { ChatbotPanel } from './ChatbotPanel';
import { ProcessingStatus } from './ProcessingStatus';
import { DocumentCdmSelector } from './DocumentCdmSelector';
import { FloatingChatbotButton } from './FloatingChatbotButton';
import { CdmDataPreview } from './CdmDataPreview';
import { Dialog, DialogContent } from '../../components/ui/dialog';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '../../components/ui/tabs';
import { Button } from '../../components/ui/button';

// Types
interface LMATemplate {
  id: number;
  template_code: string;
  name: string;
  category: string;
  subcategory?: string;
  governing_law?: string;
  version: string;
  required_fields?: string[];
  optional_fields?: string[];
  ai_generated_sections?: string[];
}

interface GeneratedDocument {
  id: number;
  template_id: number;
  file_path: string;
  status: string;
  generation_summary?: {
    total_fields: number;
    mapped_fields_count: number;
    ai_fields_count: number;
    missing_required_fields: string[];
  };
  created_at: string;
}

// Use CreditAgreementData from FDC3Context for consistency
type CreditAgreementData = FDC3CreditAgreementData;

interface DocumentGeneratorProps {
  initialCdmData?: CreditAgreementData;
  onDocumentGenerated?: (document: GeneratedDocument) => void;
}

export function DocumentGenerator({ initialCdmData, onDocumentGenerated }: DocumentGeneratorProps) {
  const { broadcast } = useFDC3();
  const { isAuthenticated } = useAuth();
  
  // State
  const [templates, setTemplates] = useState<LMATemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<LMATemplate | null>(null);
  const [cdmData, setCdmData] = useState<CreditAgreementData>(initialCdmData || {});
  const [generatedDocument, setGeneratedDocument] = useState<GeneratedDocument | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loadingTemplates, setLoadingTemplates] = useState(true);
  const [showPreview, setShowPreview] = useState(false);
  const [inputMode, setInputMode] = useState<'library' | 'manual'>('library');
  const [sourceDocumentId, setSourceDocumentId] = useState<number | null>(null);
  const [selectedDocumentTitle, setSelectedDocumentTitle] = useState<string | null>(null);
  const [isChatbotOpen, setIsChatbotOpen] = useState(false);
  const [previewCdmData, setPreviewCdmData] = useState<CreditAgreementData | null>(null);
  const [previewDocumentTitle, setPreviewDocumentTitle] = useState<string | null>(null);
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);

  // Load templates on mount
  useEffect(() => {
    loadTemplates();
  }, []);

  // Update CDM data if initial data changes
  useEffect(() => {
    if (initialCdmData) {
      setCdmData(initialCdmData);
    }
  }, [initialCdmData]);

  // Handle CDM data selection from library
  const handleCdmDataSelect = useCallback((
    cdmData: CreditAgreementData,
    documentId: number
  ) => {
    // Ensure parties have 'id' field
    if (cdmData.parties) {
      cdmData.parties = cdmData.parties.map((party, idx) => ({
        ...party,
        id: party.id || `party_${idx}`,
      }));
    }
    setCdmData(cdmData);
    setSourceDocumentId(documentId);
    setError(null);
    
    // Fetch document title for display
    fetchWithAuth(`/api/documents/${documentId}`)
      .then(res => res.json())
      .then(data => {
        if (data.document) {
          setSelectedDocumentTitle(data.document.title);
        }
      })
      .catch(() => {
        // Ignore errors fetching title
      });
  }, []);

  // Handle CDM data update from chatbot
  const handleCdmDataUpdate = useCallback((updatedCdmData: Record<string, unknown>) => {
    // Ensure parties have 'id' field if missing
    const updated = updatedCdmData as CreditAgreementData;
    if (updated.parties) {
      updated.parties = updated.parties.map((party, idx) => ({
        ...party,
        id: party.id || `party_${idx}`,
      }));
    }
    setCdmData(updated);
    setError(null);
  }, []);

  const loadTemplates = useCallback(async () => {
    try {
      setLoadingTemplates(true);
      setError(null);
      const response = await fetchWithAuth('/api/templates');
      if (response.ok) {
        const data = await response.json();
        setTemplates(data.templates || []);
      } else {
        throw new Error('Failed to load templates');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load templates');
    } finally {
      setLoadingTemplates(false);
    }
  }, []);

  const handleTemplateSelect = useCallback(async (templateId: number) => {
    try {
      setError(null);
      const response = await fetchWithAuth(`/api/templates/${templateId}`);
      if (response.ok) {
        const template = await response.json();
        setSelectedTemplate(template);
        setGeneratedDocument(null);
        setShowPreview(false);
        
        // Load template requirements
        const reqResponse = await fetchWithAuth(`/api/templates/${templateId}/requirements`);
        if (reqResponse.ok) {
          const requirements = await reqResponse.json();
          // Could use this to validate or highlight required fields
          console.log('Template requirements:', requirements);
        }
      } else {
        throw new Error('Failed to load template details');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to select template');
    }
  }, []);

  // Handle template selection from chatbot
  const handleChatbotTemplateSelect = useCallback((templateId: number) => {
    handleTemplateSelect(templateId);
  }, [handleTemplateSelect]);

  // Check if CDM data is valid for generation
  const hasValidCdmData = useCallback(() => {
    if (!cdmData || Object.keys(cdmData).length === 0) {
      return false;
    }
    // Check for at least one party and one facility
    const hasParties = cdmData.parties && Array.isArray(cdmData.parties) && cdmData.parties.length > 0;
    const hasFacilities = cdmData.facilities && Array.isArray(cdmData.facilities) && cdmData.facilities.length > 0;
    return hasParties && hasFacilities;
  }, [cdmData]);

  const handleGenerate = async () => {
    if (!selectedTemplate) {
      setError('Please select a template first');
      return;
    }

    // Check authentication before generating
    if (!isAuthenticated) {
      setError('You must be logged in to generate documents. Please log in and try again.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const response = await fetchWithAuth('/api/templates/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          template_id: selectedTemplate.id,
          cdm_data: cdmData,
          source_document_id: sourceDocumentId,
        }),
      });

      if (response.status === 401) {
        // Handle authentication error
        const errorData = await response.json().catch(() => ({}));
        setError('Authentication required. Please log in and try again.');
        return;
      }

      if (response.ok) {
        const doc = await response.json();
        setGeneratedDocument(doc);
        setShowPreview(true);
        
        // Broadcast FDC3 context for generated document
        if (selectedTemplate) {
          const context: GeneratedDocumentContext = {
            type: 'finos.creditnexus.generatedDocument',
            id: {
              documentId: doc.document_id || `doc_${doc.id}`,
              templateId: selectedTemplate.id,
            },
            template: {
              id: selectedTemplate.id,
              code: selectedTemplate.template_code,
              name: selectedTemplate.name,
              category: selectedTemplate.category,
            },
            sourceCdmData: cdmData,
            generatedAt: new Date().toISOString(),
            filePath: doc.generated_file_path || doc.file_path,
            status: doc.status || 'generated',
          };
          
          try {
            // Cast to CreditNexusContext for broadcast (GeneratedDocumentContext extends Context)
            // Note: GeneratedDocumentContext should be added to CreditNexusContext union type
            await broadcast(context as any);
            console.log('Broadcasted generated document context:', context);
          } catch (err) {
            console.warn('Failed to broadcast generated document context:', err);
            // Don't fail the generation if broadcast fails
          }
        }
        
        if (onDocumentGenerated) {
          onDocumentGenerated(doc);
        }
      } else if (response.status === 401) {
        // Handle authentication error specifically
        const errorData = await response.json().catch(() => ({}));
        setError('Authentication required. Please log in to generate documents.');
      } else {
        // Handle other error responses
        const errorData = await response.json().catch(() => ({}));
        const errorMessage = errorData.detail?.message || errorData.detail || errorData.message || 'Document generation failed';
        setError(errorMessage);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Document generation failed';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: 'word' | 'pdf') => {
    if (!generatedDocument) return;

    try {
      const response = await fetchWithAuth(`/api/generated-documents/${generatedDocument.id}/export`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ format }),
      });

      if (response.ok) {
        // Download file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `generated_document.${format === 'pdf' ? 'pdf' : 'docx'}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        throw new Error('Export failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Export failed');
    }
  };

  return (
    <div className="h-full flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <Sparkles className="w-6 h-6 text-blue-600" />
              <h1 className="text-2xl font-bold text-gray-900">LMA Document Generator</h1>
            </div>
            <p className="text-sm text-gray-600 mt-1">
              Generate LMA-compliant documents from templates using CDM data
            </p>
          </div>
          <div className="flex items-center gap-2">
            <div className="relative group">
              <Button
                variant="outline"
                size="sm"
                className="text-gray-600 hover:text-gray-900"
                title="Workflow guidance"
              >
                <Info className="w-4 h-4" />
              </Button>
              <div className="absolute right-0 top-full mt-2 w-80 p-4 bg-white border border-gray-200 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50">
                <h4 className="font-semibold text-gray-900 mb-2">Workflow Guide</h4>
                <ol className="text-sm text-gray-600 space-y-2 list-decimal list-inside">
                  <li>Select a template from the sidebar</li>
                  <li>Choose CDM data from your library or enter manually</li>
                  <li>Review the data summary and completeness</li>
                  <li>Click "Generate Document" to create your document</li>
                  <li>Preview and export the generated document</li>
                </ol>
                <p className="text-xs text-gray-500 mt-3">
                  💡 Tip: Use the floating chatbot button for AI assistance with template selection and field filling.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar - Template Selection */}
        <div className="w-80 bg-white border-r border-gray-200 overflow-y-auto">
          <div className="p-4">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Select Template</h2>
            
            {loadingTemplates ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
              </div>
            ) : templates.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>No templates available</p>
              </div>
            ) : (
              <div className="space-y-2">
                {templates.map((template) => (
                  <button
                    key={template.id}
                    onClick={() => handleTemplateSelect(template.id)}
                    className={`w-full text-left p-3 rounded-lg border-2 transition-all ${
                      selectedTemplate?.id === template.id
                        ? 'border-blue-600 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    <div className="font-medium text-gray-900">{template.name}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {template.category} • v{template.version}
                    </div>
                    {template.governing_law && (
                      <div className="text-xs text-gray-400 mt-1">
                        {template.governing_law} Law
                      </div>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {error && (
            <div className="bg-red-50 border-l-4 border-red-400 p-4 m-4">
              <div className="flex items-center">
                <AlertCircle className="w-5 h-5 text-red-400 mr-2" />
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          )}

          {!selectedTemplate ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <FileText className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Select a Template
                </h3>
                <p className="text-sm text-gray-500">
                  Choose an LMA template from the sidebar to begin
                </p>
              </div>
            </div>
          ) : showPreview && generatedDocument ? (
            <div className="flex-1 flex flex-col p-6">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                <div className="flex items-center">
                  <CheckCircle2 className="w-5 h-5 text-green-600 mr-2" />
                  <span className="text-sm font-medium text-green-800">
                    Document generated successfully!
                  </span>
                </div>
                {generatedDocument.generation_summary && (
                  <div className="mt-2 text-xs text-green-700">
                    {generatedDocument.generation_summary.mapped_fields_count} mapped fields,{' '}
                    {generatedDocument.generation_summary.ai_fields_count} AI-generated sections
                  </div>
                )}
              </div>

              <div className="flex-1 bg-white rounded-lg border border-gray-200 p-4 mb-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">Document Preview</h3>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleExport('word')}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
                    >
                      Export Word
                    </button>
                    <button
                      onClick={() => setShowPreview(false)}
                      className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 text-sm font-medium"
                    >
                      Edit
                    </button>
                  </div>
                </div>
                <div className="border border-gray-200 rounded p-4 bg-gray-50">
                  <p className="text-sm text-gray-600">
                    Document preview will be available here. File saved at:{' '}
                    <code className="text-xs bg-white px-2 py-1 rounded">
                      {generatedDocument.file_path}
                    </code>
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex flex-col p-6">
              {/* Main Content */}
              <div className="flex-1 flex flex-col max-w-7xl mx-auto w-full">
                <div className="bg-white rounded-lg border border-gray-200 p-6 mb-4">
                  <h2 className="text-lg font-semibold text-gray-900 mb-4">
                    Template: {selectedTemplate.name}
                  </h2>
                  <div className="text-sm text-gray-600 space-y-1">
                    <p><span className="font-medium">Category:</span> {selectedTemplate.category}</p>
                    {selectedTemplate.subcategory && (
                      <p><span className="font-medium">Subcategory:</span> {selectedTemplate.subcategory}</p>
                    )}
                    {selectedTemplate.governing_law && (
                      <p><span className="font-medium">Governing Law:</span> {selectedTemplate.governing_law}</p>
                    )}
                    <p><span className="font-medium">Version:</span> {selectedTemplate.version}</p>
                  </div>
                </div>

                <div className="bg-white rounded-lg border border-gray-200 p-6 mb-4 flex-1 overflow-y-auto">
                <div className="mb-4">
                  <h3 className="text-md font-semibold text-gray-900 mb-2">CDM Data Input</h3>
                  <Tabs value={inputMode} onValueChange={(v) => setInputMode(v as 'multimodal' | 'manual')}>
                    <TabsList>
                      <TabsTrigger value="multimodal" className="flex items-center gap-2">
                        <Merge className="w-4 h-4" />
                        Multimodal
                      </TabsTrigger>
                      <TabsTrigger value="manual" className="flex items-center gap-2">
                        <FileText className="w-4 h-4" />
                        Manual JSON
                      </TabsTrigger>
                    </TabsList>

                    <TabsContent value="library" className="mt-4">
                      <DocumentCdmSelector
                        onCdmDataSelect={handleCdmDataSelect}
                        onPreview={(cdmData, documentId) => {
                          setPreviewCdmData(cdmData);
                          // Fetch document title for preview
                          fetchWithAuth(`/api/documents/${documentId}`)
                            .then(res => res.json())
                            .then(data => {
                              if (data.document) {
                                setPreviewDocumentTitle(data.document.title);
                              }
                            })
                            .catch(() => {});
                          setIsPreviewOpen(true);
                        }}
                      />
                    </TabsContent>

                    <TabsContent value="manual" className="mt-4">
                      <div className="space-y-2">
                        <label className="block text-sm font-medium text-gray-700">
                          CDM Data (JSON)
                        </label>
                        <textarea
                          value={JSON.stringify(cdmData, null, 2)}
                          onChange={(e) => {
                            try {
                              const parsed = JSON.parse(e.target.value);
                              setCdmData(parsed);
                              setError(null);
                            } catch (err) {
                              // Invalid JSON, show error
                              if (e.target.value.trim()) {
                                setError('Invalid JSON format');
                              }
                            }
                          }}
                          className="w-full h-96 font-mono text-sm border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                          placeholder='{"parties": [...], "facilities": [...]}'
                        />
                        <p className="text-xs text-gray-500">
                          Enter CDM data in JSON format. Use the "Select from Library" tab to choose from previously extracted documents.
                        </p>
                      </div>
                    </TabsContent>
                  </Tabs>
                </div>

                {/* Current CDM Data Summary */}
                {Object.keys(cdmData).length > 0 && (
                  <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircle2 className="w-4 h-4 text-blue-600" />
                      <span className="text-sm font-medium text-blue-900">CDM Data Ready</span>
                    </div>
                    {selectedDocumentTitle && (
                      <div className="text-xs text-blue-800 mb-2 font-medium">
                        Source: {selectedDocumentTitle}
                      </div>
                    )}
                    <div className="text-xs text-blue-700 space-y-1">
                      {cdmData.parties && (
                        <p>• {cdmData.parties.length} party(ies)</p>
                      )}
                      {cdmData.facilities && (
                        <p>• {cdmData.facilities.length} facility(ies)</p>
                      )}
                      {cdmData.agreement_date && (
                        <p>• Agreement Date: {cdmData.agreement_date}</p>
                      )}
                      {cdmData.governing_law && (
                        <p>• Governing Law: {cdmData.governing_law}</p>
                      )}
                    </div>
                  </div>
                )}
                </div>

                <div className="flex justify-end gap-3">
                <button
                  onClick={() => setSelectedTemplate(null)}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 font-medium"
                >
                  Cancel
                </button>
                <button
                  onClick={handleGenerate}
                  disabled={loading || !cdmData || !hasValidCdmData() || !isAuthenticated}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                  title={
                    !isAuthenticated
                      ? 'Please log in to generate documents'
                      : !cdmData
                      ? 'Please provide CDM data'
                      : !hasValidCdmData()
                      ? 'CDM data is incomplete. Please ensure parties and facilities are provided.'
                      : 'Generate document'
                  }
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4" />
                      Generate Document
                    </>
                  )}
                </button>
                </div>
              </div>

            </div>
          )}
        </div>
      </div>

      {/* Floating Chatbot Button */}
      <FloatingChatbotButton
        isOpen={isChatbotOpen}
        onClick={() => setIsChatbotOpen(!isChatbotOpen)}
      />

      {/* Chatbot Modal */}
      <Dialog open={isChatbotOpen} onOpenChange={setIsChatbotOpen}>
        <DialogContent className="max-w-4xl max-h-[85vh] p-0 overflow-hidden bg-slate-800 border-slate-700">
          <div className="h-[85vh]">
            <ChatbotPanel
              cdmData={cdmData as Record<string, unknown>}
              onCdmDataUpdate={handleCdmDataUpdate}
              onTemplateSelect={handleChatbotTemplateSelect}
              onClose={() => setIsChatbotOpen(false)}
              className="h-full"
            />
          </div>
        </DialogContent>
      </Dialog>

      {/* CDM Data Preview Modal */}
      <Dialog open={isPreviewOpen} onOpenChange={setIsPreviewOpen}>
        <DialogContent className="max-w-4xl max-h-[85vh] overflow-y-auto bg-slate-800 border-slate-700">
          {previewCdmData && (
            <CdmDataPreview
              cdmData={previewCdmData}
              documentTitle={previewDocumentTitle || undefined}
              onClose={() => setIsPreviewOpen(false)}
            />
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

