import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { fetchWithAuth } from '@/context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { 
  Mail, 
  User, 
  Calendar, 
  MessageSquare,
  CheckCircle,
  Clock,
  AlertCircle,
  Loader2,
  Send,
  UserPlus,
  X
} from 'lucide-react';

interface Inquiry {
  id: number;
  inquiry_type: string;
  status: string;
  priority: string;
  application_id: number | null;
  user_id: number | null;
  email: string;
  name: string;
  subject: string;
  message: string;
  assigned_to: number | null;
  resolved_at: string | null;
  response_message: string | null;
  created_at: string;
  updated_at: string;
}

interface InquiryDetailProps {
  inquiryId: number;
  isOpen: boolean;
  onClose: () => void;
  onUpdate?: () => void;
}

export function InquiryDetail({ inquiryId, isOpen, onClose, onUpdate }: InquiryDetailProps) {
  const { user } = useAuth();
  const [inquiry, setInquiry] = useState<Inquiry | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [responseMessage, setResponseMessage] = useState('');
  const [assignToUserId, setAssignToUserId] = useState<number | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [availableUsers, setAvailableUsers] = useState<Array<{ id: number; display_name: string; email: string }>>([]);

  useEffect(() => {
    if (isOpen && inquiryId) {
      fetchInquiry();
      if (user?.role === 'admin') {
        fetchAvailableUsers();
      }
    }
  }, [isOpen, inquiryId, user]);

  const fetchInquiry = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetchWithAuth(`/api/inquiries/${inquiryId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch inquiry');
      }
      const data = await response.json();
      setInquiry(data);
      setResponseMessage(data.response_message || '');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load inquiry');
    } finally {
      setLoading(false);
    }
  };

  const fetchAvailableUsers = async () => {
    try {
      // Assuming there's a users endpoint - if not, we'll skip this
      const response = await fetchWithAuth('/api/users');
      if (response.ok) {
        const data = await response.json();
        setAvailableUsers(data);
      }
    } catch (err) {
      console.error('Failed to fetch users:', err);
    }
  };

  const handleResolve = async () => {
    if (!responseMessage.trim()) {
      setError('Response message is required');
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        response_message: responseMessage,
      });

      const response = await fetchWithAuth(`/api/inquiries/${inquiryId}/resolve?${params.toString()}`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to resolve inquiry');
      }

      const data = await response.json();
      setInquiry(data);
      if (onUpdate) {
        onUpdate();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to resolve inquiry');
    } finally {
      setSubmitting(false);
    }
  };

  const handleAssign = async (userId: number) => {
    setSubmitting(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        user_id: userId.toString(),
      });

      const response = await fetchWithAuth(`/api/inquiries/${inquiryId}/assign?${params.toString()}`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to assign inquiry');
      }

      const data = await response.json();
      setInquiry(data);
      setAssignToUserId(null);
      if (onUpdate) {
        onUpdate();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to assign inquiry');
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      new: { color: 'bg-blue-500/10 text-blue-400 border-blue-500/50', icon: Mail },
      in_progress: { color: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/50', icon: Clock },
      resolved: { color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/50', icon: CheckCircle },
    };
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.new;
    const Icon = config.icon;
    return (
      <span className={`inline-flex items-center gap-1 px-3 py-1 rounded text-sm border ${config.color}`}>
        <Icon className="h-4 w-4" />
        {status.replace('_', ' ')}
      </span>
    );
  };

  const getPriorityBadge = (priority: string) => {
    const priorityConfig = {
      low: 'bg-slate-500/10 text-slate-400 border-slate-500/50',
      normal: 'bg-blue-500/10 text-blue-400 border-blue-500/50',
      high: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/50',
      urgent: 'bg-red-500/10 text-red-400 border-red-500/50',
    };
    return (
      <span className={`inline-flex items-center px-3 py-1 rounded text-sm border ${priorityConfig[priority as keyof typeof priorityConfig] || priorityConfig.normal}`}>
        {priority.toUpperCase()}
      </span>
    );
  };

  if (!isOpen) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto bg-slate-800 border-slate-700 text-slate-100">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>Inquiry Details</span>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="text-slate-400 hover:text-slate-100"
            >
              <X className="h-4 w-4" />
            </Button>
          </DialogTitle>
        </DialogHeader>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-emerald-400" />
          </div>
        ) : error && !inquiry ? (
          <div className="p-4 bg-red-900/20 border border-red-500/50 rounded-lg">
            <div className="flex items-center gap-2 text-red-400">
              <AlertCircle className="h-5 w-5" />
              <p>{error}</p>
            </div>
          </div>
        ) : inquiry ? (
          <div className="space-y-6">
            {/* Header Info */}
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h2 className="text-2xl font-bold mb-2">{inquiry.subject}</h2>
                <div className="flex items-center gap-3 mb-4">
                  {getStatusBadge(inquiry.status)}
                  {getPriorityBadge(inquiry.priority)}
                </div>
              </div>
            </div>

            {/* Inquiry Details */}
            <Card className="bg-slate-900 border-slate-700">
              <CardHeader>
                <CardTitle className="text-lg">Inquiry Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-slate-400 mb-1">From</p>
                    <div className="flex items-center gap-2">
                      <User className="h-4 w-4 text-slate-400" />
                      <p className="font-semibold">{inquiry.name}</p>
                    </div>
                    <p className="text-sm text-slate-400 ml-6">{inquiry.email}</p>
                  </div>
                  <div>
                    <p className="text-sm text-slate-400 mb-1">Type</p>
                    <p className="font-semibold">{inquiry.inquiry_type.replace('_', ' ')}</p>
                  </div>
                  <div>
                    <p className="text-sm text-slate-400 mb-1">Created</p>
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-slate-400" />
                      <p>{new Date(inquiry.created_at).toLocaleString()}</p>
                    </div>
                  </div>
                  {inquiry.resolved_at && (
                    <div>
                      <p className="text-sm text-slate-400 mb-1">Resolved</p>
                      <div className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-emerald-400" />
                        <p>{new Date(inquiry.resolved_at).toLocaleString()}</p>
                      </div>
                    </div>
                  )}
                </div>
                {inquiry.application_id && (
                  <div className="pt-4 border-t border-slate-700">
                    <p className="text-sm text-slate-400 mb-1">Related Application</p>
                    <p className="font-semibold">Application #{inquiry.application_id}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Message */}
            <Card className="bg-slate-900 border-slate-700">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <MessageSquare className="h-5 w-5" />
                  Message
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-slate-300 whitespace-pre-wrap">{inquiry.message}</p>
              </CardContent>
            </Card>

            {/* Response Section */}
            {inquiry.status !== 'resolved' && user?.role === 'admin' && (
              <Card className="bg-slate-900 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-lg">Response</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm text-slate-400 mb-2 block">Response Message</label>
                    <Textarea
                      value={responseMessage}
                      onChange={(e) => setResponseMessage(e.target.value)}
                      placeholder="Enter your response..."
                      className="bg-slate-800 border-slate-700 text-slate-100 min-h-[120px]"
                    />
                  </div>
                  <Button
                    onClick={handleResolve}
                    disabled={submitting || !responseMessage.trim()}
                    className="bg-emerald-600 hover:bg-emerald-500 text-white"
                  >
                    {submitting ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Resolving...
                      </>
                    ) : (
                      <>
                        <Send className="h-4 w-4 mr-2" />
                        Resolve Inquiry
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            )}

            {/* Assignment Section (Admin Only) */}
            {user?.role === 'admin' && (
              <Card className="bg-slate-900 border-slate-700">
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <UserPlus className="h-5 w-5" />
                    Assignment
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {inquiry.assigned_to ? (
                    <div>
                      <p className="text-sm text-slate-400 mb-2">Currently Assigned To</p>
                      <p className="font-semibold">User ID: {inquiry.assigned_to}</p>
                    </div>
                  ) : (
                    <div>
                      <p className="text-sm text-slate-400 mb-2">Not Assigned</p>
                    </div>
                  )}
                  {availableUsers.length > 0 && (
                    <div>
                      <label className="text-sm text-slate-400 mb-2 block">Assign To</label>
                      <select
                        value={assignToUserId || ''}
                        onChange={(e) => setAssignToUserId(e.target.value ? parseInt(e.target.value) : null)}
                        className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-slate-100"
                      >
                        <option value="">Select user...</option>
                        {availableUsers.map((u) => (
                          <option key={u.id} value={u.id}>
                            {u.display_name} ({u.email})
                          </option>
                        ))}
                      </select>
                      {assignToUserId && (
                        <Button
                          onClick={() => handleAssign(assignToUserId)}
                          disabled={submitting}
                          className="mt-2 bg-blue-600 hover:bg-blue-500 text-white"
                          size="sm"
                        >
                          {submitting ? (
                            <>
                              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                              Assigning...
                            </>
                          ) : (
                            <>
                              <UserPlus className="h-4 w-4 mr-2" />
                              Assign
                            </>
                          )}
                        </Button>
                      )}
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Response Display (if resolved) */}
            {inquiry.response_message && (
              <Card className="bg-emerald-900/20 border-emerald-500/50">
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2 text-emerald-400">
                    <CheckCircle className="h-5 w-5" />
                    Response
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-slate-300 whitespace-pre-wrap">{inquiry.response_message}</p>
                </CardContent>
              </Card>
            )}

            {/* Error Display */}
            {error && (
              <div className="p-4 bg-red-900/20 border border-red-500/50 rounded-lg">
                <div className="flex items-center gap-2 text-red-400">
                  <AlertCircle className="h-5 w-5" />
                  <p className="text-sm">{error}</p>
                </div>
              </div>
            )}
          </div>
        ) : null}
      </DialogContent>
    </Dialog>
  );
}
