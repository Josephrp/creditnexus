/**
 * Chatbot Panel Component
 * 
 * Provides AI-powered assistance for LMA template generation:
 * - Interactive chat interface
 * - Template suggestions based on CDM data
 * - Field filling assistance
 * - CDM data updates from chatbot
 */

import React, { useState, useCallback, useRef, useEffect } from 'react';
import {
  MessageSquare,
  Send,
  Loader2,
  AlertCircle,
  Sparkles,
  FileText,
  CheckCircle2,
  ChevronRight,
  X,
} from 'lucide-react';
import { fetchWithAuth } from '../../context/AuthContext';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  suggestions?: TemplateSuggestion[];
  fieldGuidance?: FieldGuidance;
}

interface TemplateSuggestion {
  template_id: number;
  template_code: string;
  name: string;
  category: string;
  confidence?: number;
  reasoning?: string;
}

interface FieldGuidance {
  missing_fields: string[];
  suggestions: Record<string, {
    suggested_value?: unknown;
    question?: string;
    example?: string;
  }>;
  questions: string[];
  guidance: string;
}

interface ChatbotPanelProps {
  cdmData?: Record<string, unknown>;
  onCdmDataUpdate?: (updatedCdmData: Record<string, unknown>) => void;
  onTemplateSelect?: (templateId: number) => void;
  className?: string;
}

export function ChatbotPanel({
  cdmData = {},
  onCdmDataUpdate,
  onTemplateSelect,
  className = '',
}: ChatbotPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'m your AI assistant for LMA template generation. I can help you:\n\n• Suggest templates based on your CDM data\n• Fill missing required fields\n• Answer questions about templates and CDM structure\n\nHow can I help you today?',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [templateSuggestions, setTemplateSuggestions] = useState<TemplateSuggestion[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const addMessage = useCallback((role: 'user' | 'assistant', content: string, extras?: {
    suggestions?: TemplateSuggestion[];
    fieldGuidance?: FieldGuidance;
  }) => {
    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      role,
      content,
      timestamp: new Date(),
      ...extras,
    };
    setMessages((prev) => [...prev, newMessage]);
    return newMessage;
  }, []);

  const handleSendMessage = useCallback(async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setError(null);
    setIsLoading(true);

    // Add user message
    addMessage('user', userMessage);

    try {
      // Call chatbot chat endpoint
      const response = await fetchWithAuth('/api/chatbot/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          cdm_context: Object.keys(cdmData).length > 0 ? cdmData : undefined,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Failed to get response' }));
        throw new Error(errorData.detail?.message || errorData.message || 'Chat request failed');
      }

      const data = await response.json();

      if (data.status === 'success') {
        const reply = data.reply || 'I apologize, but I couldn\'t generate a response.';
        
        // Check if response includes template suggestions
        let suggestions: TemplateSuggestion[] | undefined;
        if (data.template_suggestions && data.template_suggestions.length > 0) {
          suggestions = data.template_suggestions;
          setTemplateSuggestions(suggestions);
          setShowSuggestions(true);
        }

        // Check if response includes field guidance
        let fieldGuidance: FieldGuidance | undefined;
        if (data.field_guidance) {
          fieldGuidance = data.field_guidance;
        }

        addMessage('assistant', reply, {
          suggestions,
          fieldGuidance,
        });
      } else {
        throw new Error(data.message || 'Chat request failed');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send message';
      setError(errorMessage);
      addMessage('assistant', `I apologize, but I encountered an error: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  }, [input, isLoading, cdmData, addMessage]);

  const handleSuggestTemplates = useCallback(async () => {
    if (Object.keys(cdmData).length === 0) {
      setError('Please provide CDM data to get template suggestions');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetchWithAuth('/api/chatbot/suggest-templates', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          cdm_data: cdmData,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Failed to get suggestions' }));
        throw new Error(errorData.detail?.message || errorData.message || 'Template suggestion failed');
      }

      const data = await response.json();

      if (data.status === 'success' && data.suggestions) {
        const suggestions: TemplateSuggestion[] = data.suggestions.map((s: any) => ({
          template_id: s.template_id,
          template_code: s.template_code || s.code,
          name: s.name || s.template_name,
          category: s.category,
          confidence: s.confidence,
          reasoning: s.reasoning,
        }));

        setTemplateSuggestions(suggestions);
        setShowSuggestions(true);

        const reasoning = data.reasoning || 'Based on your CDM data, here are some template suggestions:';
        addMessage('assistant', reasoning, { suggestions });
      } else {
        throw new Error(data.message || 'No template suggestions available');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to get template suggestions';
      setError(errorMessage);
      addMessage('assistant', `I couldn't generate template suggestions: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  }, [cdmData, addMessage]);

  const handleFillFields = useCallback(async (requiredFields: string[]) => {
    if (requiredFields.length === 0) {
      setError('No required fields specified');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetchWithAuth('/api/chatbot/fill-fields', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          cdm_data: cdmData,
          required_fields: requiredFields,
          conversation_context: 'User is filling missing fields in CDM data for template generation',
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ message: 'Failed to get field guidance' }));
        throw new Error(errorData.detail?.message || errorData.message || 'Field filling failed');
      }

      const data = await response.json();

      if (data.status === 'success') {
        const fieldGuidance: FieldGuidance = {
          missing_fields: data.missing_fields || [],
          suggestions: data.suggestions || {},
          questions: data.questions || [],
          guidance: data.guidance || '',
        };

        if (data.all_fields_present && data.filled_data) {
          // All fields are present, update CDM data
          if (onCdmDataUpdate) {
            onCdmDataUpdate(data.filled_data);
          }
          addMessage('assistant', 'Great! All required fields are now filled. Your CDM data has been updated.', {
            fieldGuidance,
          });
        } else {
          addMessage('assistant', data.guidance || 'Here\'s guidance on filling the missing fields:', {
            fieldGuidance,
          });
        }
      } else {
        throw new Error(data.message || 'Field filling failed');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to get field guidance';
      setError(errorMessage);
      addMessage('assistant', `I couldn't provide field guidance: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  }, [cdmData, onCdmDataUpdate, addMessage]);

  const handleKeyPress = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  }, [handleSendMessage]);

  const handleSelectTemplate = useCallback((templateId: number) => {
    if (onTemplateSelect) {
      onTemplateSelect(templateId);
    }
    setShowSuggestions(false);
  }, [onTemplateSelect]);

  const formatTimestamp = (date: Date): string => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <Card className={`flex flex-col h-full ${className}`}>
      <CardHeader className="border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-blue-600" />
            <CardTitle className="text-lg">AI Assistant</CardTitle>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleSuggestTemplates}
              disabled={isLoading || Object.keys(cdmData).length === 0}
              title="Get template suggestions"
            >
              <FileText className="w-4 h-4 mr-1" />
              Suggest Templates
            </Button>
          </div>
        </div>
        <CardDescription>
          Get help with template selection, field filling, and CDM structure
        </CardDescription>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <div className="whitespace-pre-wrap text-sm">{message.content}</div>
                <div
                  className={`text-xs mt-1 ${
                    message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                  }`}
                >
                  {formatTimestamp(message.timestamp)}
                </div>

                {/* Template Suggestions */}
                {message.suggestions && message.suggestions.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-300">
                    <div className="text-xs font-semibold mb-2">Template Suggestions:</div>
                    <div className="space-y-2">
                      {message.suggestions.map((suggestion) => (
                        <button
                          key={suggestion.template_id}
                          onClick={() => handleSelectTemplate(suggestion.template_id)}
                          className="w-full text-left p-2 bg-white rounded border border-gray-200 hover:border-blue-500 hover:bg-blue-50 transition-colors"
                        >
                          <div className="font-medium text-sm">{suggestion.name}</div>
                          <div className="text-xs text-gray-500 mt-1">
                            {suggestion.category} • {suggestion.template_code}
                          </div>
                          {suggestion.reasoning && (
                            <div className="text-xs text-gray-600 mt-1">{suggestion.reasoning}</div>
                          )}
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Field Guidance */}
                {message.fieldGuidance && (
                  <div className="mt-3 pt-3 border-t border-gray-300">
                    <div className="text-xs font-semibold mb-2">Field Guidance:</div>
                    {message.fieldGuidance.missing_fields.length > 0 && (
                      <div className="mb-2">
                        <div className="text-xs text-orange-600 font-medium">
                          Missing Fields: {message.fieldGuidance.missing_fields.join(', ')}
                        </div>
                      </div>
                    )}
                    {message.fieldGuidance.questions.length > 0 && (
                      <div className="mb-2">
                        <div className="text-xs font-medium mb-1">Questions:</div>
                        <ul className="text-xs space-y-1 list-disc list-inside">
                          {message.fieldGuidance.questions.map((q, idx) => (
                            <li key={idx}>{q}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {Object.keys(message.fieldGuidance.suggestions).length > 0 && (
                      <div className="mt-2">
                        <div className="text-xs font-medium mb-1">Suggestions:</div>
                        <div className="space-y-1">
                          {Object.entries(message.fieldGuidance.suggestions).map(([field, guidance]) => (
                            <div key={field} className="text-xs">
                              <span className="font-medium">{field}:</span>{' '}
                              {guidance.suggested_value !== undefined && (
                                <span className="text-blue-600">{String(guidance.suggested_value)}</span>
                              )}
                              {guidance.question && <span className="text-gray-600"> - {guidance.question}</span>}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-lg px-4 py-2">
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Thinking...
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Error Display */}
        {error && (
          <div className="mx-4 mb-2 bg-red-50 border border-red-200 rounded-lg p-3">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-red-600" />
              <p className="text-sm text-red-700">{error}</p>
              <button
                onClick={() => setError(null)}
                className="ml-auto text-red-600 hover:text-red-800"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="border-t p-4">
          <div className="flex gap-2">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question or request help..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
              rows={2}
              disabled={isLoading}
            />
            <Button
              onClick={handleSendMessage}
              disabled={isLoading || !input.trim()}
              className="px-6"
            >
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </Button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      </CardContent>
    </Card>
  );
}





