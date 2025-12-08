import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  FileText, 
  Search, 
  Clock, 
  ChevronRight, 
  Loader2, 
  ArrowLeft,
  History,
  User,
  Building2,
  Calendar,
  DollarSign,
  Scale,
  Leaf,
  Trash2,
  ExternalLink
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

interface DocumentSummary {
  id: number;
  title: string;
  borrower_name: string | null;
  borrower_lei: string | null;
  governing_law: string | null;
  total_commitment: number | null;
  currency: string | null;
  agreement_date: string | null;
  sustainability_linked: boolean;
  workflow_state: string | null;
  uploaded_by_name: string | null;
  created_at: string;
  updated_at: string;
}

interface DocumentVersion {
  id: number;
  document_id: number;
  version_number: number;
  extracted_data: Record<string, unknown>;
  source_filename: string | null;
  extraction_method: string;
  created_by: number | null;
  created_at: string;
}

interface DocumentDetail extends DocumentSummary {
  current_version_id: number | null;
  versions: DocumentVersion[];
  workflow: {
    id: number;
    state: string;
    priority: string;
  } | null;
}

interface DocumentHistoryProps {
  onViewData?: (data: Record<string, unknown>) => void;
}

export function DocumentHistory({ onViewData }: DocumentHistoryProps) {
  const { isAuthenticated } = useAuth();
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<DocumentDetail | null>(null);
  const [selectedVersion, setSelectedVersion] = useState<DocumentVersion | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    fetchDocuments();
  }, [searchTerm]);

  const fetchDocuments = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);
      params.append('limit', '50');
      
      const response = await fetch(`/api/documents?${params.toString()}`);
      if (!response.ok) {
        throw new Error('Failed to fetch documents');
      }
      const data = await response.json();
      setDocuments(data.documents || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error('Error fetching documents:', err);
      setError('Failed to load documents');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchDocumentDetail = async (documentId: number) => {
    setIsLoadingDetail(true);
    try {
      const response = await fetch(`/api/documents/${documentId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch document');
      }
      const data = await response.json();
      setSelectedDocument(data.document);
      if (data.document.versions?.length > 0) {
        setSelectedVersion(data.document.versions[0]);
      }
    } catch (err) {
      console.error('Error fetching document detail:', err);
      setError('Failed to load document details');
    } finally {
      setIsLoadingDetail(false);
    }
  };

  const handleDeleteDocument = async (documentId: number) => {
    if (!confirm('Are you sure you want to delete this document? This action cannot be undone.')) {
      return;
    }
    
    try {
      const response = await fetch(`/api/documents/${documentId}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail?.message || 'Failed to delete document');
      }
      setSelectedDocument(null);
      fetchDocuments();
    } catch (err) {
      console.error('Error deleting document:', err);
      setError(err instanceof Error ? err.message : 'Failed to delete document');
    }
  };

  const handleBack = () => {
    setSelectedDocument(null);
    setSelectedVersion(null);
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const formatCurrency = (amount: number | null, currency: string | null) => {
    if (amount === null) return 'N/A';
    return `${currency || 'USD'} ${amount.toLocaleString()}`;
  };

  const getWorkflowStateColor = (state: string | null) => {
    switch (state) {
      case 'draft': return 'bg-slate-500/20 text-slate-400';
      case 'under_review': return 'bg-yellow-500/20 text-yellow-400';
      case 'approved': return 'bg-emerald-500/20 text-emerald-400';
      case 'published': return 'bg-blue-500/20 text-blue-400';
      default: return 'bg-slate-500/20 text-slate-400';
    }
  };

  if (selectedDocument) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={handleBack}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Documents
          </Button>
        </div>

        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">{selectedDocument.title}</h2>
            <p className="text-muted-foreground">
              Document #{selectedDocument.id} · {selectedDocument.versions?.length || 0} versions
            </p>
          </div>
          {isAuthenticated && (
            <Button 
              variant="outline" 
              size="sm" 
              className="text-red-400 hover:bg-red-500/10"
              onClick={() => handleDeleteDocument(selectedDocument.id)}
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Delete
            </Button>
          )}
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          <div className="md:col-span-2 space-y-6">
            <Card className="border-slate-700 bg-slate-800/50">
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold mb-4">Document Details</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-start gap-3">
                    <Building2 className="h-5 w-5 text-slate-400 mt-0.5" />
                    <div>
                      <p className="text-xs text-muted-foreground">Borrower</p>
                      <p className="font-medium">{selectedDocument.borrower_name || 'N/A'}</p>
                      {selectedDocument.borrower_lei && (
                        <p className="text-xs text-slate-400 font-mono">LEI: {selectedDocument.borrower_lei}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <DollarSign className="h-5 w-5 text-emerald-400 mt-0.5" />
                    <div>
                      <p className="text-xs text-muted-foreground">Total Commitment</p>
                      <p className="font-medium text-emerald-400">
                        {formatCurrency(selectedDocument.total_commitment, selectedDocument.currency)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Calendar className="h-5 w-5 text-slate-400 mt-0.5" />
                    <div>
                      <p className="text-xs text-muted-foreground">Agreement Date</p>
                      <p className="font-medium">{formatDate(selectedDocument.agreement_date)}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Scale className="h-5 w-5 text-slate-400 mt-0.5" />
                    <div>
                      <p className="text-xs text-muted-foreground">Governing Law</p>
                      <p className="font-medium">{selectedDocument.governing_law || 'N/A'}</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <Leaf className={`h-5 w-5 mt-0.5 ${selectedDocument.sustainability_linked ? 'text-emerald-400' : 'text-slate-400'}`} />
                    <div>
                      <p className="text-xs text-muted-foreground">Sustainability Linked</p>
                      <p className="font-medium">
                        {selectedDocument.sustainability_linked ? (
                          <span className="text-emerald-400">Yes</span>
                        ) : 'No'}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <User className="h-5 w-5 text-slate-400 mt-0.5" />
                    <div>
                      <p className="text-xs text-muted-foreground">Uploaded By</p>
                      <p className="font-medium">{selectedDocument.uploaded_by_name || 'Unknown'}</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {selectedVersion && (
              <Card className="border-slate-700 bg-slate-800/50">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold">
                      Version {selectedVersion.version_number} Data
                    </h3>
                    {onViewData && (
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => onViewData(selectedVersion.extracted_data)}
                      >
                        <ExternalLink className="h-4 w-4 mr-2" />
                        Open in Digitizer
                      </Button>
                    )}
                  </div>
                  <pre className="text-xs font-mono bg-slate-900 p-4 rounded-lg overflow-auto max-h-96 text-slate-300">
                    {JSON.stringify(selectedVersion.extracted_data, null, 2)}
                  </pre>
                </CardContent>
              </Card>
            )}
          </div>

          <div className="space-y-4">
            <Card className="border-slate-700 bg-slate-800/50">
              <CardContent className="p-4">
                <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                  <History className="h-4 w-4" />
                  Version History
                </h3>
                <div className="space-y-2">
                  {selectedDocument.versions?.map((version) => (
                    <button
                      key={version.id}
                      onClick={() => setSelectedVersion(version)}
                      className={`w-full text-left p-3 rounded-lg border transition-all ${
                        selectedVersion?.id === version.id
                          ? 'border-emerald-500 bg-emerald-500/10'
                          : 'border-slate-700 bg-slate-900/50 hover:bg-slate-800'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-medium">Version {version.version_number}</span>
                        {version.id === selectedDocument.current_version_id && (
                          <span className="text-xs bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded">
                            Current
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">
                        {formatDate(version.created_at)}
                      </p>
                      {version.source_filename && (
                        <p className="text-xs text-slate-400 mt-1 truncate">
                          {version.source_filename}
                        </p>
                      )}
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>

            {selectedDocument.workflow && (
              <Card className="border-slate-700 bg-slate-800/50">
                <CardContent className="p-4">
                  <h3 className="text-sm font-semibold mb-3">Workflow Status</h3>
                  <div className={`inline-flex items-center px-3 py-1.5 rounded-full text-sm ${getWorkflowStateColor(selectedDocument.workflow.state)}`}>
                    {selectedDocument.workflow.state?.replace('_', ' ')}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Document Library</h2>
          <p className="text-muted-foreground">
            {total} saved extraction{total !== 1 ? 's' : ''}
          </p>
        </div>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search by title or borrower name..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
        />
      </div>

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm">
          {error}
        </div>
      )}

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-emerald-500" />
        </div>
      ) : documents.length === 0 ? (
        <Card className="border-slate-700 bg-slate-800/50">
          <CardContent className="p-12 text-center">
            <div className="w-16 h-16 rounded-full bg-slate-700 flex items-center justify-center mx-auto mb-4">
              <FileText className="h-8 w-8 text-slate-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">No Documents Yet</h3>
            <p className="text-muted-foreground max-w-md mx-auto">
              {searchTerm
                ? 'No documents match your search. Try a different term.'
                : 'Extract and save credit agreements to build your document library.'}
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {documents.map((doc) => (
            <Card
              key={doc.id}
              className="border-slate-700 bg-slate-800/50 hover:bg-slate-800 cursor-pointer transition-colors"
              onClick={() => fetchDocumentDetail(doc.id)}
            >
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4 flex-1 min-w-0">
                    <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
                      <FileText className="h-5 w-5 text-emerald-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3">
                        <h3 className="font-semibold truncate">{doc.title}</h3>
                        {doc.workflow_state && (
                          <span className={`text-xs px-2 py-0.5 rounded-full ${getWorkflowStateColor(doc.workflow_state)}`}>
                            {doc.workflow_state.replace('_', ' ')}
                          </span>
                        )}
                        {doc.sustainability_linked && (
                          <Leaf className="h-4 w-4 text-emerald-400 flex-shrink-0" />
                        )}
                      </div>
                      <div className="flex items-center gap-4 text-sm text-muted-foreground mt-1">
                        {doc.borrower_name && (
                          <span className="flex items-center gap-1">
                            <Building2 className="h-3 w-3" />
                            {doc.borrower_name}
                          </span>
                        )}
                        {doc.total_commitment && (
                          <span className="text-emerald-400">
                            {formatCurrency(doc.total_commitment, doc.currency)}
                          </span>
                        )}
                        <span className="flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {formatDate(doc.updated_at)}
                        </span>
                      </div>
                    </div>
                  </div>
                  <ChevronRight className="h-5 w-5 text-slate-400" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {isLoadingDetail && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-lg p-6 flex items-center gap-3">
            <Loader2 className="h-5 w-5 animate-spin text-emerald-500" />
            <span>Loading document...</span>
          </div>
        </div>
      )}
    </div>
  );
}
