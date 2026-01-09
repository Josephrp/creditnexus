/**
 * Template Grid Component
 * 
 * Displays LMA templates in a scrollable grid layout (2 rows × 3 columns).
 * Shows template preview with category, governing law, version, and requirements.
 */

import { FileText, Scale, Tag, Sparkles, ChevronLeft, ChevronRight } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

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

interface TemplateGridProps {
  templates: LMATemplate[];
  selectedTemplateId: number | null;
  onSelect: (templateId: number) => void;
  onPreview?: (template: LMATemplate) => void;
  className?: string;
}

export function TemplateGrid({
  templates,
  selectedTemplateId,
  onSelect,
  onPreview,
  className = '',
}: TemplateGridProps) {
  const getCategoryColor = (category: string): string => {
    const colors: Record<string, string> = {
      'Sustainable Finance': 'bg-emerald-900/30 border-emerald-700 text-emerald-300',
      'Regulatory': 'bg-blue-900/30 border-blue-700 text-blue-300',
      'Secondary Trading': 'bg-purple-900/30 border-purple-700 text-purple-300',
      'Security & Intercreditor': 'bg-orange-900/30 border-orange-700 text-orange-300',
      'Origination': 'bg-indigo-900/30 border-indigo-700 text-indigo-300',
      'Default': 'bg-slate-700 border-slate-600 text-slate-300',
    };
    return colors[category] || colors['Default'];
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'Sustainable Finance':
        return '🌱';
      case 'Regulatory':
        return '📋';
      case 'Secondary Trading':
        return '📊';
      case 'Security & Intercreditor':
        return '🔒';
      case 'Origination':
        return '📝';
      default:
        return '📄';
    }
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Grid Container with Horizontal Scroll */}
      <div className="relative">
        {/* Scrollable Grid: 2 rows × 3 columns (6 visible templates) */}
        <div className="overflow-x-auto overflow-y-hidden pb-4 scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-800">
          <div 
            className="inline-grid gap-4"
            style={{ 
              gridTemplateColumns: 'repeat(3, minmax(280px, 320px))',
              gridTemplateRows: 'repeat(2, auto)',
              gridAutoFlow: 'column',
              minWidth: 'max-content'
            }}
          >
            {templates.map((template) => {
              const isSelected = selectedTemplateId === template.id;
              const requiredFieldsCount = template.required_fields?.length || 0;
              const optionalFieldsCount = template.optional_fields?.length || 0;
              const aiSectionsCount = template.ai_generated_sections?.length || 0;
              
              return (
                <Card
                  key={template.id}
                  className={`cursor-pointer transition-all hover:shadow-lg ${
                    isSelected
                      ? 'ring-2 ring-emerald-500 border-emerald-500 bg-slate-800'
                      : 'border-slate-700 hover:border-slate-600 bg-slate-800/50'
                  }`}
                  onClick={() => onSelect(template.id)}
                >
                  <CardContent className="p-4">
                    {/* Header */}
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <FileText className="w-4 h-4 text-slate-400 flex-shrink-0" />
                          <h4 className="font-medium text-sm text-slate-100 truncate">{template.name}</h4>
                        </div>
                        <div className="flex items-center gap-2 flex-wrap mt-1">
                          <span className={`inline-flex items-center gap-1 px-2 py-0.5 text-xs rounded border ${getCategoryColor(template.category)}`}>
                            <span>{getCategoryIcon(template.category)}</span>
                            <span>{template.category}</span>
                          </span>
                          {template.subcategory && (
                            <span className="text-xs text-slate-400">
                              {template.subcategory}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Template Code */}
                    <div className="mb-3">
                      <div className="flex items-center gap-1 text-xs text-slate-400">
                        <Tag className="w-3 h-3" />
                        <span className="font-mono">{template.template_code}</span>
                        <span className="text-slate-500">v{template.version}</span>
                      </div>
                    </div>

                    {/* Governing Law */}
                    {template.governing_law && (
                      <div className="flex items-center gap-2 mb-3 text-xs text-slate-300">
                        <Scale className="w-3 h-3 text-slate-400 flex-shrink-0" />
                        <span className="truncate">{template.governing_law} Law</span>
                      </div>
                    )}

                    {/* Requirements Summary */}
                    <div className="space-y-2 text-xs mb-3">
                      {requiredFieldsCount > 0 && (
                        <div className="flex items-center justify-between">
                          <span className="text-slate-400">Required Fields</span>
                          <span className="font-medium text-slate-200">{requiredFieldsCount}</span>
                        </div>
                      )}
                      {optionalFieldsCount > 0 && (
                        <div className="flex items-center justify-between">
                          <span className="text-slate-400">Optional Fields</span>
                          <span className="font-medium text-slate-200">{optionalFieldsCount}</span>
                        </div>
                      )}
                      {aiSectionsCount > 0 && (
                        <div className="flex items-center justify-between">
                          <span className="text-slate-400 flex items-center gap-1">
                            <Sparkles className="w-3 h-3" />
                            AI Sections
                          </span>
                          <span className="font-medium text-slate-200">{aiSectionsCount}</span>
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2 mt-4">
                      <Button
                        size="sm"
                        variant={isSelected ? "default" : "outline"}
                        className={`flex-1 text-xs h-7 ${
                          isSelected
                            ? 'bg-emerald-600 text-white hover:bg-emerald-500'
                            : 'bg-slate-700 text-slate-200 hover:bg-slate-600 border-slate-600'
                        }`}
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelect(template.id);
                        }}
                      >
                        {isSelected ? 'Selected' : 'Select'}
                      </Button>
                      {onPreview && (
                        <Button
                          size="sm"
                          variant="ghost"
                          className="text-xs h-7 px-2 text-slate-300 hover:text-slate-100 hover:bg-slate-700"
                          onClick={(e) => {
                            e.stopPropagation();
                            onPreview(template);
                          }}
                        >
                          View
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
        
        {/* Scroll Indicators */}
        {templates.length > 6 && (
          <div className="flex items-center justify-center gap-2 mt-2 text-xs text-slate-400">
            <ChevronLeft className="w-4 h-4" />
            <span>Scroll horizontally to see more templates ({templates.length} total)</span>
            <ChevronRight className="w-4 h-4" />
          </div>
        )}
      </div>
    </div>
  );
}
