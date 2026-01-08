import { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  X,
  Calendar,
  Clock,
  Users,
  Video,
  Download,
  Save,
  Trash2,
  Plus,
  Loader2,
  AlertCircle
} from 'lucide-react';
import { fetchWithAuth } from '@/context/AuthContext';
import { downloadICSFile } from '@/utils/icsDownload';

interface Meeting {
  id: number;
  title: string;
  description: string | null;
  scheduled_at: string;
  duration_minutes: number;
  meeting_type: string;
  application_id: number | null;
  organizer_id: number | null;
  attendees: Array<{
    name: string;
    email: string;
  }> | null;
  meeting_link: string | null;
  ics_file_path: string | null;
  created_at: string;
  updated_at: string;
}

interface MeetingModalProps {
  isOpen: boolean;
  onClose: () => void;
  meeting: Meeting | null;
  selectedDate?: Date | null;
  onDownloadICS?: (meetingId: number) => void;
}

export function MeetingModal({ isOpen, onClose, meeting, selectedDate, onDownloadICS }: MeetingModalProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(!meeting);
  
  const [formData, setFormData] = useState({
    title: meeting?.title || '',
    description: meeting?.description || '',
    scheduled_at: meeting 
      ? new Date(meeting.scheduled_at).toISOString().slice(0, 16)
      : selectedDate 
        ? new Date(selectedDate).toISOString().slice(0, 16)
        : '',
    duration_minutes: meeting?.duration_minutes || 60,
    meeting_type: meeting?.meeting_type || 'consultation',
    meeting_link: meeting?.meeting_link || '',
    attendees: meeting?.attendees || [],
  });

  const [newAttendee, setNewAttendee] = useState({ name: '', email: '' });

  useEffect(() => {
    if (meeting) {
      setFormData({
        title: meeting.title,
        description: meeting.description || '',
        scheduled_at: new Date(meeting.scheduled_at).toISOString().slice(0, 16),
        duration_minutes: meeting.duration_minutes,
        meeting_type: meeting.meeting_type,
        meeting_link: meeting.meeting_link || '',
        attendees: meeting.attendees || [],
      });
      setIsEditing(false);
    } else {
      setIsEditing(true);
      setFormData({
        title: '',
        description: '',
        scheduled_at: selectedDate 
          ? new Date(selectedDate).toISOString().slice(0, 16)
          : '',
        duration_minutes: 60,
        meeting_type: 'consultation',
        meeting_link: '',
        attendees: [],
      });
    }
  }, [meeting, selectedDate]);

  const handleAddAttendee = () => {
    if (newAttendee.name && newAttendee.email) {
      setFormData(prev => ({
        ...prev,
        attendees: [...(prev.attendees || []), { ...newAttendee }],
      }));
      setNewAttendee({ name: '', email: '' });
    }
  };

  const handleRemoveAttendee = (index: number) => {
    setFormData(prev => ({
      ...prev,
      attendees: prev.attendees?.filter((_, i) => i !== index) || [],
    }));
  };

  const handleSave = async () => {
    if (!formData.title.trim() || !formData.scheduled_at) {
      setError('Title and scheduled time are required');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const scheduledAt = new Date(formData.scheduled_at).toISOString();
      
      if (meeting) {
        // Update existing meeting
        const response = await fetchWithAuth(`/api/meetings/${meeting.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            title: formData.title,
            description: formData.description || null,
            scheduled_at: scheduledAt,
            duration_minutes: formData.duration_minutes,
            meeting_type: formData.meeting_type,
            meeting_link: formData.meeting_link || null,
            attendees: formData.attendees,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to update meeting');
        }
      } else {
        // Create new meeting
        const response = await fetchWithAuth('/api/meetings', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            title: formData.title,
            description: formData.description || null,
            scheduled_at: scheduledAt,
            duration_minutes: formData.duration_minutes,
            meeting_type: formData.meeting_type,
            meeting_link: formData.meeting_link || null,
            attendees: formData.attendees,
          }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Failed to create meeting');
        }
      }

      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save meeting');
      console.error('Error saving meeting:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!meeting || !confirm('Are you sure you want to delete this meeting?')) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetchWithAuth(`/api/meetings/${meeting.id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete meeting');
      }

      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete meeting');
      console.error('Error deleting meeting:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadICS = async () => {
    if (!meeting) return;
    
    try {
      if (onDownloadICS) {
        onDownloadICS(meeting.id);
      } else {
        await downloadICSFile(meeting.id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to download ICS file');
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="bg-slate-800 border-slate-700 text-slate-100 max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl">
            {meeting ? (isEditing ? 'Edit Meeting' : 'Meeting Details') : 'Create New Meeting'}
          </DialogTitle>
          <DialogDescription className="text-slate-400">
            {meeting && !isEditing ? 'View meeting details and manage attendees' : 'Schedule a new meeting'}
          </DialogDescription>
        </DialogHeader>

        {error && (
          <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-4 flex items-center gap-2 text-red-400">
            <AlertCircle className="h-5 w-5" />
            <span>{error}</span>
          </div>
        )}

        {isEditing ? (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Title *
              </label>
              <Input
                value={formData.title}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                className="bg-slate-900 border-slate-700 text-slate-100"
                placeholder="Meeting title"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                className="w-full min-h-[100px] rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                placeholder="Meeting description..."
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Scheduled Date & Time *
                </label>
                <Input
                  type="datetime-local"
                  value={formData.scheduled_at}
                  onChange={(e) => setFormData(prev => ({ ...prev, scheduled_at: e.target.value }))}
                  className="bg-slate-900 border-slate-700 text-slate-100"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Duration (minutes) *
                </label>
                <Input
                  type="number"
                  value={formData.duration_minutes}
                  onChange={(e) => setFormData(prev => ({ ...prev, duration_minutes: Number(e.target.value) }))}
                  className="bg-slate-900 border-slate-700 text-slate-100"
                  min="15"
                  step="15"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Meeting Type
                </label>
                <select
                  value={formData.meeting_type}
                  onChange={(e) => setFormData(prev => ({ ...prev, meeting_type: e.target.value }))}
                  className="w-full h-9 rounded-md border border-slate-700 bg-slate-900 px-3 text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500"
                >
                  <option value="consultation">Consultation</option>
                  <option value="application_review">Application Review</option>
                  <option value="follow_up">Follow-up</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Meeting Link (optional)
                </label>
                <Input
                  value={formData.meeting_link}
                  onChange={(e) => setFormData(prev => ({ ...prev, meeting_link: e.target.value }))}
                  className="bg-slate-900 border-slate-700 text-slate-100"
                  placeholder="https://..."
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Attendees
              </label>
              <div className="space-y-2">
                {formData.attendees?.map((attendee, index) => (
                  <div key={index} className="flex items-center gap-2 p-2 bg-slate-900 rounded-lg">
                    <div className="flex-1">
                      <p className="text-sm text-slate-100">{attendee.name}</p>
                      <p className="text-xs text-slate-400">{attendee.email}</p>
                    </div>
                    <button
                      onClick={() => handleRemoveAttendee(index)}
                      className="text-red-400 hover:text-red-300"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                ))}
                <div className="flex gap-2">
                  <Input
                    value={newAttendee.name}
                    onChange={(e) => setNewAttendee(prev => ({ ...prev, name: e.target.value }))}
                    className="bg-slate-900 border-slate-700 text-slate-100 flex-1"
                    placeholder="Name"
                  />
                  <Input
                    type="email"
                    value={newAttendee.email}
                    onChange={(e) => setNewAttendee(prev => ({ ...prev, email: e.target.value }))}
                    className="bg-slate-900 border-slate-700 text-slate-100 flex-1"
                    placeholder="Email"
                  />
                  <Button
                    onClick={handleAddAttendee}
                    size="sm"
                    className="bg-emerald-600 hover:bg-emerald-500 text-white"
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold text-slate-100 mb-2">{meeting?.title}</h3>
              {meeting?.description && (
                <p className="text-slate-300">{meeting.description}</p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center gap-2 text-slate-300">
                <Calendar className="h-5 w-5 text-slate-400" />
                <div>
                  <p className="text-sm font-medium">Date & Time</p>
                  <p className="text-xs text-slate-400">
                    {meeting && new Date(meeting.scheduled_at).toLocaleString()}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2 text-slate-300">
                <Clock className="h-5 w-5 text-slate-400" />
                <div>
                  <p className="text-sm font-medium">Duration</p>
                  <p className="text-xs text-slate-400">{meeting?.duration_minutes} minutes</p>
                </div>
              </div>

              {meeting?.meeting_link && (
                <div className="flex items-center gap-2 text-slate-300">
                  <Video className="h-5 w-5 text-slate-400" />
                  <div>
                    <p className="text-sm font-medium">Meeting Link</p>
                    <a
                      href={meeting.meeting_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-emerald-400 hover:underline"
                    >
                      Join Meeting
                    </a>
                  </div>
                </div>
              )}

              <div className="flex items-center gap-2 text-slate-300">
                <Users className="h-5 w-5 text-slate-400" />
                <div>
                  <p className="text-sm font-medium">Attendees</p>
                  <p className="text-xs text-slate-400">
                    {meeting?.attendees?.length || 0} attendee(s)
                  </p>
                </div>
              </div>
            </div>

            {meeting?.attendees && meeting.attendees.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-slate-300 mb-2">Attendee List</h4>
                <div className="space-y-2">
                  {meeting.attendees.map((attendee, index) => (
                    <div key={index} className="p-2 bg-slate-900 rounded-lg">
                      <p className="text-sm text-slate-100">{attendee.name}</p>
                      <p className="text-xs text-slate-400">{attendee.email}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        <div className="flex items-center justify-between pt-4 border-t border-slate-700">
          <div className="flex items-center gap-2">
            {meeting && !isEditing && (
              <>
                <Button
                  onClick={handleDownloadICS}
                  variant="outline"
                  className="border-slate-700 text-slate-300 hover:bg-slate-700"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download ICS
                </Button>
                <Button
                  onClick={handleDelete}
                  variant="outline"
                  className="border-red-500/50 text-red-400 hover:bg-red-500/10"
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </Button>
              </>
            )}
          </div>
          <div className="flex items-center gap-2">
            {meeting && !isEditing && (
              <Button
                onClick={() => setIsEditing(true)}
                variant="outline"
                className="border-slate-700 text-slate-300 hover:bg-slate-700"
              >
                Edit
              </Button>
            )}
            <Button
              onClick={onClose}
              variant="outline"
              className="border-slate-700 text-slate-300 hover:bg-slate-700"
            >
              {meeting && !isEditing ? 'Close' : 'Cancel'}
            </Button>
            {isEditing && (
              <Button
                onClick={handleSave}
                disabled={loading}
                className="bg-emerald-600 hover:bg-emerald-500 text-white"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Save
                  </>
                )}
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
