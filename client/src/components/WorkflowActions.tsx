import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { useToast } from '@/components/ui/toast';
import { 
  Send, 
  CheckCircle, 
  XCircle, 
  Globe, 
  Archive, 
  Loader2,
  AlertCircle,
  Clock,
  User,
  Calendar,
  Sparkles,
  FileText
} from 'lucide-react';
import { useAuth, fetchWithAuth } from '@/context/AuthContext';

interface WorkflowData {
  id: number;
  document_id: number;
  state: string;
  priority: string;
  assigned_to: number | null;
  assigned_to_name?: string | null;
  submitted_at: string | null;
  approved_at: string | null;
  approved_by: number | null;
  approved_by_name?: string | null;
  published_at: string | null;
  rejection_reason: string | null;
  due_date: string | null;
  available_actions?: string[];
}

interface WorkflowActionsProps {
  documentId: number;
  workflow: WorkflowData;
  onWorkflowUpdate: (workflow: WorkflowData) => void;
}

export function WorkflowActions({ documentId, workflow, onWorkflowUpdate }: WorkflowActionsProps) {
  const { user, isAuthenticated } = useAuth();
  const { addToast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [rejectReason, setRejectReason] = useState('');

  const canSubmit = user?.role === 'analyst' || user?.role === 'reviewer' || user?.role === 'admin';
  const canReview = user?.role === 'reviewer' || user?.role === 'admin';

  const actionMessages: Record<string, string> = {
    submit: 'Document submitted for review',
    approve: 'Document approved successfully',
    reject: 'Document rejected',
    publish: 'Document published successfully',
    archive: 'Document archived',
  };

  const executeWorkflowAction = async (action: string, body?: Record<string, unknown>) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetchWithAuth(`/api/documents/${documentId}/workflow/${action}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: body ? JSON.stringify(body) : undefined,
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail?.message || `Failed to ${action} document`);
      }

      const data = await response.json();
      onWorkflowUpdate(data.workflow);
      addToast(actionMessages[action] || `${action} completed`, 'success');
    } catch (err) {
      console.error(`Error executing ${action}:`, err);
      const errorMessage = err instanceof Error ? err.message : `Failed to ${action} document`;
      setError(errorMessage);
      addToast(errorMessage, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = () => executeWorkflowAction('submit');
  const handleApprove = () => executeWorkflowAction('approve');
  const handlePublish = () => executeWorkflowAction('publish');
  const handleArchive = () => executeWorkflowAction('archive');
  const handleRegenerate = () => {
    // Navigate to document generator with the document's source CDM data
    // This would require passing document data or fetching it
    window.location.href = `/document-generator?documentId=${documentId}`;
  };
  
  const handleReject = () => {
    if (!rejectReason.trim()) {
      setError('Please provide a reason for rejection');
      return;
    }
    executeWorkflowAction('reject', { reason: rejectReason });
    setShowRejectModal(false);
    setRejectReason('');
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return null;
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStateInfo = (state: string) => {
    switch (state) {
      case 'draft':
        return {
          label: 'Draft',
          color: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
          icon: <Clock className="h-4 w-4" />,
          description: 'This document is in draft state and can be submitted for review.',
        };
      case 'under_review':
        return {
          label: 'Under Review',
          color: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
          icon: <User className="h-4 w-4" />,
          description: 'This document is awaiting review and approval.',
        };
      case 'approved':
        return {
          label: 'Approved',
          color: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
          icon: <CheckCircle className="h-4 w-4" />,
          description: 'This document has been approved and can be published.',
        };
      case 'published':
        return {
          label: 'Published',
          color: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
          icon: <Globe className="h-4 w-4" />,
          description: 'This document is published and available for use.',
        };
      case 'archived':
        return {
          label: 'Archived',
          color: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
          icon: <Archive className="h-4 w-4" />,
          description: 'This document has been archived.',
        };
      case 'generated':
        return {
          label: 'Generated',
          color: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
          icon: <Sparkles className="h-4 w-4" />,
          description: 'This document was generated from an LMA template and is ready for review.',
        };
      default:
        return {
          label: state,
          color: 'bg-slate-500/20 text-slate-400 border-slate-500/30',
          icon: <Clock className="h-4 w-4" />,
          description: '',
        };
    }
  };

  const stateInfo = getStateInfo(workflow.state);

  if (!isAuthenticated) {
    return (
      <Card className="border-slate-700 bg-slate-800/50">
        <CardContent className="p-4">
          <h3 className="text-sm font-semibold mb-3">Workflow Status</h3>
          <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm border ${stateInfo.color}`}>
            {stateInfo.icon}
            {stateInfo.label}
          </div>
          <p className="text-xs text-muted-foreground mt-3">
            Log in to perform workflow actions.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-slate-700 bg-slate-800/50">
      <CardContent className="p-4 space-y-4">
        <div>
          <h3 className="text-sm font-semibold mb-2">Workflow Status</h3>
          <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm border ${stateInfo.color}`}>
            {stateInfo.icon}
            {stateInfo.label}
          </div>
          <p className="text-xs text-muted-foreground mt-2">{stateInfo.description}</p>
        </div>

        {workflow.rejection_reason && (
          <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
            <div className="flex items-center gap-2 text-red-400 text-sm font-medium mb-1">
              <AlertCircle className="h-4 w-4" />
              Rejection Reason
            </div>
            <p className="text-sm text-slate-300">{workflow.rejection_reason}</p>
          </div>
        )}

        {(workflow.submitted_at || workflow.approved_at || workflow.published_at) && (
          <div className="space-y-2 text-xs text-muted-foreground">
            {workflow.submitted_at && (
              <div className="flex items-center gap-2">
                <Send className="h-3 w-3" />
                <span>Submitted: {formatDate(workflow.submitted_at)}</span>
              </div>
            )}
            {workflow.approved_at && (
              <div className="flex items-center gap-2">
                <CheckCircle className="h-3 w-3 text-emerald-400" />
                <span>
                  Approved: {formatDate(workflow.approved_at)}
                  {workflow.approved_by_name && ` by ${workflow.approved_by_name}`}
                </span>
              </div>
            )}
            {workflow.published_at && (
              <div className="flex items-center gap-2">
                <Globe className="h-3 w-3 text-blue-400" />
                <span>Published: {formatDate(workflow.published_at)}</span>
              </div>
            )}
          </div>
        )}

        {workflow.due_date && (
          <div className="flex items-center gap-2 text-xs text-yellow-400">
            <Calendar className="h-3 w-3" />
            <span>Due: {formatDate(workflow.due_date)}</span>
          </div>
        )}

        {error && (
          <div className="p-2 bg-red-500/10 border border-red-500/20 rounded text-red-400 text-xs">
            {error}
          </div>
        )}

        <div className="space-y-2 pt-2 border-t border-slate-700">
          <p className="text-xs font-medium text-muted-foreground">Actions</p>
          
          {workflow.state === 'draft' && canSubmit && (
            <Button
              size="sm"
              className="w-full bg-emerald-600 hover:bg-emerald-500"
              onClick={handleSubmit}
              disabled={isLoading}
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <Send className="h-4 w-4 mr-2" />
              )}
              Submit for Review
            </Button>
          )}

          {workflow.state === 'under_review' && canReview && (
            <>
              <Button
                size="sm"
                className="w-full bg-emerald-600 hover:bg-emerald-500"
                onClick={handleApprove}
                disabled={isLoading}
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : (
                  <CheckCircle className="h-4 w-4 mr-2" />
                )}
                Approve
              </Button>
              <Button
                size="sm"
                variant="outline"
                className="w-full border-red-500/30 text-red-400 hover:bg-red-500/10"
                onClick={() => setShowRejectModal(true)}
                disabled={isLoading}
              >
                <XCircle className="h-4 w-4 mr-2" />
                Reject
              </Button>
            </>
          )}

          {workflow.state === 'generated' && (
            <>
              {canSubmit && (
                <Button
                  size="sm"
                  className="w-full bg-emerald-600 hover:bg-emerald-500"
                  onClick={handleSubmit}
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  ) : (
                    <FileText className="h-4 w-4 mr-2" />
                  )}
                  Review Generated Document
                </Button>
              )}
              <Button
                size="sm"
                variant="outline"
                className="w-full border-purple-500/30 text-purple-400 hover:bg-purple-500/10"
                onClick={handleRegenerate}
                disabled={isLoading}
              >
                <Sparkles className="h-4 w-4 mr-2" />
                Regenerate
              </Button>
            </>
          )}

          {workflow.state === 'approved' && canReview && (
            <Button
              size="sm"
              className="w-full bg-blue-600 hover:bg-blue-500"
              onClick={handlePublish}
              disabled={isLoading}
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <Globe className="h-4 w-4 mr-2" />
              )}
              Publish
            </Button>
          )}

          {workflow.state !== 'archived' && workflow.state !== 'generated' && canReview && (
            <Button
              size="sm"
              variant="ghost"
              className="w-full text-slate-400 hover:text-slate-300"
              onClick={handleArchive}
              disabled={isLoading}
            >
              <Archive className="h-4 w-4 mr-2" />
              Archive
            </Button>
          )}

          {workflow.state === 'archived' && (
            <p className="text-xs text-muted-foreground text-center py-2">
              No actions available for archived documents.
            </p>
          )}

          {!canSubmit && !canReview && (
            <p className="text-xs text-muted-foreground text-center py-2">
              You don't have permission to perform workflow actions.
            </p>
          )}
        </div>
      </CardContent>

      {showRejectModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Reject Document</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Please provide a reason for rejecting this document. The document will be returned to draft state.
            </p>
            <textarea
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="Enter rejection reason..."
              className="w-full h-24 px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 resize-none"
            />
            <div className="flex gap-3 mt-4">
              <Button
                variant="ghost"
                className="flex-1"
                onClick={() => {
                  setShowRejectModal(false);
                  setRejectReason('');
                }}
              >
                Cancel
              </Button>
              <Button
                className="flex-1 bg-red-600 hover:bg-red-500"
                onClick={handleReject}
                disabled={!rejectReason.trim() || isLoading}
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : (
                  <XCircle className="h-4 w-4 mr-2" />
                )}
                Reject
              </Button>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
}
