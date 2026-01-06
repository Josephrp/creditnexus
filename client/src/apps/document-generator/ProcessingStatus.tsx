/**
 * Processing Status Component
 * 
 * Shows processing progress, extracted data, conflicts, allows editing,
 * and triggers fusion for multimodal inputs.
 */

import React, { useState, useCallback } from 'react';
import {
  Loader2,
  CheckCircle2,
  AlertCircle,
  AlertTriangle,
  Edit2,
  Merge,
  X,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';

interface ExtractedData {
  source: 'audio' | 'image' | 'document' | 'text';
  sourceId?: string;
  rawText?: string;
  cdmData?: Record<string, unknown>;
  extractionStatus?: string;
  confidence?: number;
  timestamp: Date;
}

interface Conflict {
  field_path: string;
  values: Array<{
    value: string;
    source: {
      source_type: string;
      source_id?: string;
      confidence: number;
    };
  }>;
  resolution?: string;
  resolved_value?: string;
}

interface ProcessingStatusProps {
  extractedData: ExtractedData[];
  conflicts?: Conflict[];
  isProcessing?: boolean;
  processingStep?: string;
  onEdit?: (source: string, data: Record<string, unknown>) => void;
  onRemove?: (source: string) => void;
  onFuse?: () => void;
  canFuse?: boolean;
  className?: string;
}

export function ProcessingStatus({
  extractedData,
  conflicts = [],
  isProcessing = false,
  processingStep,
  onEdit,
  onRemove,
  onFuse,
  canFuse = false,
  className = '',
}: ProcessingStatusProps) {
  const [expandedSources, setExpandedSources] = useState<Set<string>>(new Set());
  const [expandedConflicts, setExpandedConflicts] = useState<Set<string>>(new Set());
  const [editingSource, setEditingSource] = useState<string | null>(null);
  const [editData, setEditData] = useState<Record<string, unknown>>({});

  const toggleSourceExpansion = useCallback((sourceId: string) => {
    setExpandedSources((prev) => {
      const next = new Set(prev);
      if (next.has(sourceId)) {
        next.delete(sourceId);
      } else {
        next.add(sourceId);
      }
      return next;
    });
  }, []);

  const toggleConflictExpansion = useCallback((fieldPath: string) => {
    setExpandedConflicts((prev) => {
      const next = new Set(prev);
      if (next.has(fieldPath)) {
        next.delete(fieldPath);
      } else {
        next.add(fieldPath);
      }
      return next;
    });
  }, []);

  const handleEdit = useCallback((source: ExtractedData) => {
    setEditingSource(source.source + (source.sourceId || ''));
    setEditData(source.cdmData || {});
  }, []);

  const handleSaveEdit = useCallback(() => {
    if (editingSource && onEdit) {
      onEdit(editingSource, editData);
      setEditingSource(null);
      setEditData({});
    }
  }, [editingSource, editData, onEdit]);

  const handleCancelEdit = useCallback(() => {
    setEditingSource(null);
    setEditData({});
  }, []);

  const getSourceIcon = (source: string) => {
    switch (source) {
      case 'audio':
        return '🎤';
      case 'image':
        return '🖼️';
      case 'document':
        return '📄';
      case 'text':
        return '📝';
      default:
        return '📋';
    }
  };

  const getSourceLabel = (source: string) => {
    switch (source) {
      case 'audio':
        return 'Audio Transcription';
      case 'image':
        return 'Image OCR';
      case 'document':
        return 'Document Retrieval';
      case 'text':
        return 'Text Input';
      default:
        return source;
    }
  };

  if (extractedData.length === 0 && !isProcessing) {
    return null;
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Processing Indicator */}
      {isProcessing && (
        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
              <div className="flex-1">
                <p className="text-sm font-medium text-blue-900">
                  {processingStep || 'Processing...'}
                </p>
                <p className="text-xs text-blue-700 mt-1">
                  Extracting and analyzing data from input sources
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Extracted Data Sources */}
      {extractedData.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-lg">Extracted Data Sources</CardTitle>
                <CardDescription>
                  {extractedData.length} source(s) processed
                </CardDescription>
              </div>
              {canFuse && onFuse && (
                <Button onClick={onFuse} className="flex items-center gap-2">
                  <Merge className="w-4 h-4" />
                  Fuse Sources
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {extractedData.map((data, idx) => {
                const sourceId = `${data.source}_${idx}`;
                const isExpanded = expandedSources.has(sourceId);
                const isEditing = editingSource === sourceId;

                return (
                  <div
                    key={sourceId}
                    className="border border-gray-200 rounded-lg p-4 bg-gray-50"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-xl">{getSourceIcon(data.source)}</span>
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            {getSourceLabel(data.source)}
                          </p>
                          <p className="text-xs text-gray-500">
                            {data.timestamp.toLocaleTimeString()}
                            {data.confidence && ` • ${Math.round(data.confidence * 100)}% confidence`}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {data.extractionStatus === 'success' && (
                          <CheckCircle2 className="w-4 h-4 text-green-600" />
                        )}
                        {data.extractionStatus === 'partial_data_missing' && (
                          <AlertTriangle className="w-4 h-4 text-yellow-600" />
                        )}
                        {onEdit && !isEditing && (
                          <button
                            onClick={() => handleEdit(data)}
                            className="p-1 text-gray-600 hover:text-blue-600"
                            title="Edit data"
                          >
                            <Edit2 className="w-4 h-4" />
                          </button>
                        )}
                        {onRemove && (
                          <button
                            onClick={() => onRemove(sourceId)}
                            className="p-1 text-gray-600 hover:text-red-600"
                            title="Remove source"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        )}
                        <button
                          onClick={() => toggleSourceExpansion(sourceId)}
                          className="p-1 text-gray-600 hover:text-gray-900"
                        >
                          {isExpanded ? (
                            <ChevronUp className="w-4 h-4" />
                          ) : (
                            <ChevronDown className="w-4 h-4" />
                          )}
                        </button>
                      </div>
                    </div>

                    {isExpanded && (
                      <div className="mt-3 space-y-3 pt-3 border-t border-gray-200">
                        {isEditing ? (
                          <div className="space-y-2">
                            <textarea
                              value={JSON.stringify(editData, null, 2)}
                              onChange={(e) => {
                                try {
                                  const parsed = JSON.parse(e.target.value);
                                  setEditData(parsed);
                                } catch {
                                  // Invalid JSON, keep as is
                                }
                              }}
                              className="w-full h-48 font-mono text-xs border border-gray-300 rounded p-2"
                            />
                            <div className="flex gap-2">
                              <Button
                                onClick={handleSaveEdit}
                                size="sm"
                                className="flex-1"
                              >
                                Save
                              </Button>
                              <Button
                                onClick={handleCancelEdit}
                                size="sm"
                                variant="outline"
                                className="flex-1"
                              >
                                Cancel
                              </Button>
                            </div>
                          </div>
                        ) : (
                          <>
                            {data.rawText && (
                              <div>
                                <p className="text-xs font-medium text-gray-700 mb-1">
                                  Raw Text:
                                </p>
                                <p className="text-xs text-gray-600 bg-white p-2 rounded border border-gray-200 max-h-32 overflow-y-auto">
                                  {data.rawText.substring(0, 500)}
                                  {data.rawText.length > 500 && '...'}
                                </p>
                              </div>
                            )}
                            {data.cdmData && (
                              <div>
                                <p className="text-xs font-medium text-gray-700 mb-1">
                                  CDM Data:
                                </p>
                                <pre className="text-xs text-gray-600 bg-white p-2 rounded border border-gray-200 max-h-48 overflow-y-auto">
                                  {JSON.stringify(data.cdmData, null, 2)}
                                </pre>
                              </div>
                            )}
                          </>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Conflicts */}
      {conflicts.length > 0 && (
        <Card className="border-yellow-200 bg-yellow-50">
          <CardHeader>
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-yellow-600" />
              <CardTitle className="text-lg text-yellow-900">
                Data Conflicts ({conflicts.length})
              </CardTitle>
            </div>
            <CardDescription className="text-yellow-700">
              Conflicting values detected across sources. Review and resolve before fusion.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {conflicts.map((conflict) => {
                const isExpanded = expandedConflicts.has(conflict.field_path);

                return (
                  <div
                    key={conflict.field_path}
                    className="border border-yellow-300 rounded-lg p-3 bg-white"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {conflict.field_path}
                        </p>
                        <p className="text-xs text-gray-600 mt-1">
                          {conflict.values.length} conflicting value(s)
                        </p>
                      </div>
                      <button
                        onClick={() => toggleConflictExpansion(conflict.field_path)}
                        className="p-1 text-gray-600 hover:text-gray-900"
                      >
                        {isExpanded ? (
                          <ChevronUp className="w-4 h-4" />
                        ) : (
                          <ChevronDown className="w-4 h-4" />
                        )}
                      </button>
                    </div>

                    {isExpanded && (
                      <div className="mt-3 pt-3 border-t border-yellow-200 space-y-2">
                        {conflict.values.map((val, idx) => (
                          <div
                            key={idx}
                            className="flex items-center justify-between p-2 bg-gray-50 rounded"
                          >
                            <div>
                              <p className="text-sm text-gray-900">{val.value}</p>
                              <p className="text-xs text-gray-500">
                                Source: {val.source.source_type}
                                {val.source.confidence && ` • ${Math.round(val.source.confidence * 100)}% confidence`}
                              </p>
                            </div>
                          </div>
                        ))}
                        {conflict.resolved_value && (
                          <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded">
                            <p className="text-xs font-medium text-green-900 mb-1">
                              Resolved Value:
                            </p>
                            <p className="text-sm text-green-800">
                              {conflict.resolved_value}
                            </p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}





