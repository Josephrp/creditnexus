import { useState, useEffect } from 'react';
import { fetchWithAuth } from '@/context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Search, FileJson, Calendar, Shield, Radio, Activity } from 'lucide-react';

interface CDMEvent {
  eventType: string;
  eventDate: string;
  meta?: {
    globalKey: string;
    sourceSystem: string;
  };
  payload: any;
}

export function CDMEventExplorer() {
  const [events, setEvents] = useState<CDMEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedEvent, setSelectedEvent] = useState<CDMEvent | null>(null);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        setLoading(true);
        // This is a new endpoint we need to support in the backend
        // For now we'll fetch from the dashboard data if possible or a dedicated endpoint
        const response = await fetchWithAuth('/api/auditor/cdm-events');
        if (response.ok) {
          const data = await response.json();
          setEvents(data.events || []);
        }
      } catch (err) {
        console.error('Failed to fetch CDM events', err);
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, []);

  const filteredEvents = events.filter(e => 
    e.eventType.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (e.meta?.globalKey && e.meta.globalKey.includes(searchTerm))
  );

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'Observation': return <Radio className="h-4 w-4 text-blue-400" />;
      case 'TradeExecution': return <Activity className="h-4 w-4 text-emerald-400" />;
      case 'TermsChange': return <Activity className="h-4 w-4 text-orange-400" />;
      case 'PolicyEvaluation': return <Shield className="h-4 w-4 text-purple-400" />;
      default: return <FileJson className="h-4 w-4 text-slate-400" />;
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-1 space-y-4">
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader>
            <CardTitle className="text-slate-100 flex items-center gap-2">
              <Search className="h-5 w-5 text-slate-400" />
              Search Events
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Input
              placeholder="Filter by event type or key..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-slate-900 border-slate-700 text-slate-100"
            />
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 border-slate-700 max-h-[600px] overflow-y-auto">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-slate-300">
              Machine-Executable Events ({filteredEvents.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-slate-700/50">
              {loading ? (
                <div className="p-8 text-center text-slate-500">Loading events...</div>
              ) : filteredEvents.length === 0 ? (
                <div className="p-8 text-center text-slate-500">No events found</div>
              ) : (
                filteredEvents.map((event, idx) => (
                  <button
                    key={idx}
                    onClick={() => setSelectedEvent(event)}
                    className={`w-full text-left p-4 hover:bg-slate-700/30 transition-colors ${
                      selectedEvent === event ? 'bg-slate-700/50 border-l-2 border-emerald-500' : ''
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="flex items-center gap-2 font-medium text-slate-100">
                        {getEventIcon(event.eventType)}
                        {event.eventType}
                      </span>
                      <span className="text-[10px] text-slate-500 flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {new Date(event.eventDate).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="text-[10px] font-mono text-slate-400 truncate">
                      {event.meta?.globalKey || 'No Global Key'}
                    </div>
                  </button>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="lg:col-span-2">
        {selectedEvent ? (
          <Card className="bg-slate-800/50 border-slate-700 h-full">
            <CardHeader className="border-b border-slate-700 pb-4">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-xl text-slate-100 flex items-center gap-2">
                    {getEventIcon(selectedEvent.eventType)}
                    {selectedEvent.eventType}
                  </CardTitle>
                  <p className="text-sm text-slate-400 mt-1">
                    Event Date: {new Date(selectedEvent.eventDate).toLocaleString()}
                  </p>
                </div>
                <Button variant="outline" size="sm" onClick={() => {
                  const blob = new Blob([JSON.stringify(selectedEvent.payload, null, 2)], { type: 'application/json' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `event_${selectedEvent.eventType}_${selectedEvent.meta?.globalKey || 'export'}.json`;
                  a.click();
                }}>
                  Download JSON
                </Button>
              </div>
            </CardHeader>
            <CardContent className="p-0">
              <div className="bg-slate-950 p-6 font-mono text-xs overflow-auto max-h-[700px]">
                <pre className="text-emerald-400">
                  {JSON.stringify(selectedEvent.payload, null, 2)}
                </pre>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-slate-500 border-2 border-dashed border-slate-700 rounded-lg p-12">
            <FileJson className="h-16 w-16 mb-4 opacity-20" />
            <p className="text-lg">Select an event to view its machine-executable structure</p>
            <p className="text-sm mt-2">All events follow the FINOS Common Domain Model (CDM) standard.</p>
          </div>
        )}
      </div>
    </div>
  );
}
