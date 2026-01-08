import { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { fetchWithAuth } from '@/context/AuthContext';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  Mail, 
  Filter, 
  Search, 
  ChevronDown,
  ChevronUp,
  Loader2,
  AlertCircle,
  CheckCircle,
  Clock,
  User
} from 'lucide-react';
import { InquiryDetail } from './InquiryDetail';

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

type FilterType = 'all' | 'new' | 'in_progress' | 'resolved';
type SortField = 'created_at' | 'priority' | 'status';
type SortOrder = 'asc' | 'desc';

export function Inbox() {
  const { user } = useAuth();
  const [inquiries, setInquiries] = useState<Inquiry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filter, setFilter] = useState<FilterType>('all');
  const [sortField, setSortField] = useState<SortField>('created_at');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [page, setPage] = useState(1);
  const [limit] = useState(20);
  const [total, setTotal] = useState(0);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedInquiryId, setSelectedInquiryId] = useState<number | null>(null);

  useEffect(() => {
    if (user?.role === 'admin') {
      fetchInquiries();
    } else {
      setError('Access denied. Admin only.');
      setLoading(false);
    }
  }, [user, filter, sortField, sortOrder, page, searchTerm]);

  const fetchInquiries = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString(),
      });

      if (filter !== 'all') {
        params.append('status', filter === 'new' ? 'new' : filter === 'in_progress' ? 'in_progress' : 'resolved');
      }

      const response = await fetchWithAuth(`/api/inquiries?${params.toString()}`);
      if (!response.ok) {
        throw new Error('Failed to fetch inquiries');
      }
      const data = await response.json();
      setInquiries(data);
      setTotal(data.length); // API should return total count, but using length for now
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load inquiries');
    } finally {
      setLoading(false);
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
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs border ${config.color}`}>
        <Icon className="h-3 w-3" />
        {status.replace('_', ' ')}
      </span>
    );
  };

  const getPriorityBadge = (priority: string) => {
    const priorityConfig = {
      low: 'text-slate-400',
      normal: 'text-blue-400',
      high: 'text-yellow-400',
      urgent: 'text-red-400',
    };
    return (
      <span className={`text-xs font-semibold ${priorityConfig[priority as keyof typeof priorityConfig] || priorityConfig.normal}`}>
        {priority.toUpperCase()}
      </span>
    );
  };

  const filteredInquiries = inquiries.filter(inquiry => {
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      return (
        inquiry.subject.toLowerCase().includes(searchLower) ||
        inquiry.message.toLowerCase().includes(searchLower) ||
        inquiry.email.toLowerCase().includes(searchLower) ||
        inquiry.name.toLowerCase().includes(searchLower)
      );
    }
    return true;
  });

  const sortedInquiries = [...filteredInquiries].sort((a, b) => {
    let aVal: string | number;
    let bVal: string | number;

    switch (sortField) {
      case 'created_at':
        aVal = new Date(a.created_at).getTime();
        bVal = new Date(b.created_at).getTime();
        break;
      case 'priority':
        const priorityOrder = { urgent: 4, high: 3, normal: 2, low: 1 };
        aVal = priorityOrder[a.priority as keyof typeof priorityOrder] || 0;
        bVal = priorityOrder[b.priority as keyof typeof priorityOrder] || 0;
        break;
      case 'status':
        aVal = a.status;
        bVal = b.status;
        break;
      default:
        return 0;
    }

    if (sortOrder === 'asc') {
      return aVal > bVal ? 1 : -1;
    } else {
      return aVal < bVal ? 1 : -1;
    }
  });

  if (user?.role !== 'admin') {
    return (
      <div className="p-8">
        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-8 text-center">
            <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-2">Access Denied</h2>
            <p className="text-slate-400">This page is only accessible to administrators.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">Inbox</h1>
          <p className="text-slate-400">Manage customer inquiries and support requests</p>
        </div>
        <Button
          onClick={() => setShowFilters(!showFilters)}
          variant="outline"
          className="border-slate-600 text-slate-300 hover:bg-slate-800"
        >
          <Filter className="h-4 w-4 mr-2" />
          Filters
          {showFilters ? <ChevronUp className="h-4 w-4 ml-2" /> : <ChevronDown className="h-4 w-4 ml-2" />}
        </Button>
      </div>

      {/* Filters */}
      {showFilters && (
        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="text-sm text-slate-400 mb-2 block">Search</label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                  <Input
                    placeholder="Search inquiries..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 bg-slate-900 border-slate-700"
                  />
                </div>
              </div>
              <div>
                <label className="text-sm text-slate-400 mb-2 block">Status</label>
                <select
                  value={filter}
                  onChange={(e) => setFilter(e.target.value as FilterType)}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded text-slate-100"
                >
                  <option value="all">All</option>
                  <option value="new">New</option>
                  <option value="in_progress">In Progress</option>
                  <option value="resolved">Resolved</option>
                </select>
              </div>
              <div>
                <label className="text-sm text-slate-400 mb-2 block">Sort By</label>
                <select
                  value={sortField}
                  onChange={(e) => setSortField(e.target.value as SortField)}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded text-slate-100"
                >
                  <option value="created_at">Date</option>
                  <option value="priority">Priority</option>
                  <option value="status">Status</option>
                </select>
              </div>
              <div>
                <label className="text-sm text-slate-400 mb-2 block">Order</label>
                <select
                  value={sortOrder}
                  onChange={(e) => setSortOrder(e.target.value as SortOrder)}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded text-slate-100"
                >
                  <option value="desc">Descending</option>
                  <option value="asc">Ascending</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Inquiries List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-emerald-400" />
        </div>
      ) : error ? (
        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-8 text-center">
            <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
            <p className="text-slate-400">{error}</p>
          </CardContent>
        </Card>
      ) : sortedInquiries.length === 0 ? (
        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-8 text-center">
            <Mail className="h-12 w-12 text-slate-400 mx-auto mb-4" />
            <p className="text-slate-400">No inquiries found</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {sortedInquiries.map((inquiry) => (
            <Card key={inquiry.id} className="bg-slate-800 border-slate-700 hover:border-slate-600 transition-colors">
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold">{inquiry.subject}</h3>
                      {getStatusBadge(inquiry.status)}
                      {getPriorityBadge(inquiry.priority)}
                    </div>
                    <div className="flex items-center gap-4 text-sm text-slate-400 mb-2">
                      <span className="flex items-center gap-1">
                        <User className="h-4 w-4" />
                        {inquiry.name}
                      </span>
                      <span>{inquiry.email}</span>
                      <span>{new Date(inquiry.created_at).toLocaleDateString()}</span>
                    </div>
                    <p className="text-slate-300 line-clamp-2">{inquiry.message}</p>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSelectedInquiryId(inquiry.id)}
                    className="border-slate-600 text-slate-300 hover:bg-slate-800"
                  >
                    View
                  </Button>
                </div>
                {inquiry.application_id && (
                  <div className="mt-4 pt-4 border-t border-slate-700">
                    <span className="text-sm text-slate-400">
                      Related to Application #{inquiry.application_id}
                    </span>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Pagination */}
      {total > limit && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-slate-400">
            Showing {(page - 1) * limit + 1} to {Math.min(page * limit, total)} of {total}
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="border-slate-600 text-slate-300 hover:bg-slate-800"
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage(p => p + 1)}
              disabled={page * limit >= total}
              className="border-slate-600 text-slate-300 hover:bg-slate-800"
            >
              Next
            </Button>
          </div>
        </div>
      )}

      {/* Inquiry Detail Modal */}
      {selectedInquiryId && (
        <InquiryDetail
          inquiryId={selectedInquiryId}
          isOpen={selectedInquiryId !== null}
          onClose={() => {
            setSelectedInquiryId(null);
            fetchInquiries();
          }}
          onUpdate={fetchInquiries}
        />
      )}
    </div>
  );
}
