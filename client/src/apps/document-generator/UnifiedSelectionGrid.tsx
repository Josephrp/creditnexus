/**
 * Unified Selection Grid Component
 * 
 * Displays CDM documents in the first row and templates in the second row.
 * Both are selectable and work together for document generation.
 */

import { FileText, ChevronLeft, ChevronRight } from 'lucide-react';
import { CdmPreviewCard } from './CdmPreviewCard';

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

interface DocumentWithCdm {
  id: number;
  title: string;
  borrower_name?: string | null;
  borrower_lei?: string | null;
  governing_law?: string | null;
  total_commitment?: number | null;
  currency?: string | null;
  agreement_date?: string | null;
  completenessScore?: number;
  cdmData?: any;
}

interface UnifiedSelectionGridProps {
  // CDM Documents (Row 1)
  documents: DocumentWithCdm[];
  selectedDocumentId: number | null;
  onDocumentSelect: (documentId: number) => void;
  onDocumentPreview?: (documentId: number) => void;
  
  // Templates (Row 2)
  templates: LMATemplate[];
  selectedTemplateId: number | null;
  onTemplateSelect: (templateId: number) => void;
  onTemplatePreview?: (template: LMATemplate) => void;
  
  className?: string;
}

export function UnifiedSelectionGrid({
  documents,
  selectedDocumentId,
  onDocumentSelect,
  onDocumentPreview,
  templates,
  selectedTemplateId,
  onTemplateSelect,
  className = '',
}: UnifiedSelectionGridProps) {
  return (
    <div className={`space-y-6 ${className}`}>
      {/* Row 1: CDM Documents */}
      <div className="space-y-2">
        <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
          <FileText className="w-4 h-4 text-slate-400" />
          Select CDM Document (Row 1)
        </h3>
        {documents.length === 0 ? (
          <div className="text-center py-8 text-slate-400">
            <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>No CDM documents available in library</p>
          </div>
        ) : (
          <div className="relative">
            <div className="overflow-x-auto overflow-y-hidden pb-4" style={{ WebkitOverflowScrolling: 'touch' }}>
              <div 
                className="flex gap-4"
                style={{ 
                  minWidth: 'max-content',
                  width: 'max-content'
                }}
              >
                {documents.map((doc) => (
                    <div key={doc.id} style={{ minWidth: '280px', maxWidth: '320px', flexShrink: 0 }}>
                      <CdmPreviewCard
                        documentId={doc.id}
                        title={doc.title}
                        borrowerName={doc.borrower_name}
                        borrowerLei={doc.borrower_lei}
                        governingLaw={doc.governing_law}
                        totalCommitment={doc.total_commitment}
                        currency={doc.currency}
                        agreementDate={doc.agreement_date}
                        completenessScore={doc.completenessScore}
                        isSelected={selectedDocumentId === doc.id}
                        onSelect={onDocumentSelect}
                        onPreview={onDocumentPreview}
                      />
                    </div>
                ))}
              </div>
            </div>
            {documents.length > 3 && (
              <div className="flex items-center justify-center gap-2 mt-2 text-xs text-slate-400">
                <ChevronLeft className="w-4 h-4" />
                <span>Scroll horizontally to see more documents ({documents.length} total)</span>
                <ChevronRight className="w-4 h-4" />
              </div>
            )}
          </div>
        )}
      </div>

      {/* Row 2: Templates */}
      <div className="space-y-2">
        <h3 className="text-sm font-semibold text-slate-100 flex items-center gap-2">
          <FileText className="w-4 h-4 text-slate-400" />
          Select Template (Row 2)
        </h3>
        <div className="relative">
          <div className="overflow-x-auto overflow-y-hidden pb-4 scrollbar-thin scrollbar-thumb-slate-600 scrollbar-track-slate-800">
              <div 
                className="flex gap-4"
                style={{ 
                  minWidth: 'max-content',
                  width: 'max-content'
                }}
              >
                {templates.map((template) => {
                const isSelected = selectedTemplateId === template.id;
                const requiredFieldsCount = template.required_fields?.length || 0;
                const aiSectionsCount = template.ai_generated_sections?.length || 0;
                
                return (
                  <div
                    key={template.id}
                    className={`cursor-pointer transition-all hover:shadow-lg border-2 rounded-lg p-4 flex-shrink-0 ${
                      isSelected
                        ? 'ring-2 ring-emerald-500 border-emerald-500 bg-slate-800'
                        : 'border-slate-700 hover:border-slate-600 bg-slate-800/50'
                    }`}
                    style={{ minWidth: '280px', maxWidth: '320px' }}
                    onClick={() => onTemplateSelect(template.id)}
                  >
                    {/* Template Card Content - Simplified version */}
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <FileText className="w-4 h-4 text-slate-400 flex-shrink-0" />
                          <h4 className="font-medium text-sm text-slate-100 truncate">{template.name}</h4>
                        </div>
                        <div className="text-xs text-slate-400">
                          {template.category} • v{template.version}
                        </div>
                      </div>
                    </div>

                    {template.governing_law && (
                      <div className="text-xs text-slate-300 mb-2">
                        {template.governing_law} Law
                      </div>
                    )}

                    <div className="flex items-center justify-between text-xs text-slate-400 mb-3">
                      <span>Required: {requiredFieldsCount}</span>
                      <span>AI Sections: {aiSectionsCount}</span>
                    </div>

                    <button
                      className={`w-full text-xs py-1.5 px-3 rounded transition-colors ${
                        isSelected
                          ? 'bg-emerald-600 text-white hover:bg-emerald-500'
                          : 'bg-slate-700 text-slate-200 hover:bg-slate-600'
                      }`}
                      onClick={(e) => {
                        e.stopPropagation();
                        onTemplateSelect(template.id);
                      }}
                    >
                      {isSelected ? 'Selected' : 'Select'}
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
          {templates.length > 3 && (
            <div className="flex items-center justify-center gap-2 mt-2 text-xs text-slate-400">
              <ChevronLeft className="w-4 h-4" />
              <span>Scroll horizontally to see more templates ({templates.length} total)</span>
              <ChevronRight className="w-4 h-4" />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
