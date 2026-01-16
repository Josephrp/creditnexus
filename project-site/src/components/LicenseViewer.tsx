import { useState, useEffect } from 'react';
import { X, FileText, Loader2, ArrowLeft } from 'lucide-react';
import { markdownToHtml } from '../utils/markdown';

interface LicenseViewerProps {
  licenseType: 'license' | 'rail';
  onClose: () => void;
}

export function LicenseViewer({ licenseType, onClose }: LicenseViewerProps) {
  const [content, setContent] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLicense = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const fileName = licenseType === 'license' ? 'LICENSE.md' : 'RAIL.md';
        // Use relative pathing to ensure it works on GitHub Pages subpaths
        const response = await fetch(`./${fileName}`);
        
        if (response.ok) {
          const text = await response.text();
          setContent(text);
        } else {
          setError(`License file ${fileName} not found.`);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load license file');
      } finally {
        setLoading(false);
      }
    };

    fetchLicense();
    
    // Prevent scrolling on body when modal is open
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [licenseType]);

  const title = licenseType === 'license' ? 'License Agreement' : 'Responsible AI License (RAIL)';
  const htmlContent = content ? markdownToHtml(content) : '';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
      <div className="bg-slate-800 border border-slate-700 w-full max-w-4xl max-h-[90vh] rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-in fade-in zoom-in duration-300">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-700 flex items-center justify-between bg-slate-800/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-emerald-500/10 rounded-lg flex items-center justify-center">
              <FileText className="h-6 w-6 text-emerald-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-100">{title}</h2>
              <p className="text-xs text-slate-400 uppercase tracking-wider">CreditNexus Legal</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-slate-700 rounded-full text-slate-400 hover:text-slate-100 transition-colors"
            aria-label="Close"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 md:p-10 custom-scrollbar">
          {loading && (
            <div className="flex flex-col items-center justify-center py-20">
              <Loader2 className="h-10 w-10 animate-spin text-emerald-500 mb-4" />
              <p className="text-slate-400">Loading document...</p>
            </div>
          )}

          {error && (
            <div className="p-6 rounded-xl bg-red-500/10 border border-red-500/50 text-center">
              <p className="text-red-400 font-semibold mb-2">Error Loading Document</p>
              <p className="text-slate-300 mb-6">{error}</p>
              <button 
                onClick={onClose}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors inline-flex items-center"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Go Back
              </button>
            </div>
          )}

          {!loading && !error && (
            <div 
              className="prose prose-invert max-w-none"
              dangerouslySetInnerHTML={{ __html: htmlContent }}
            />
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-700 bg-slate-800/50 flex justify-end">
          <button 
            onClick={onClose}
            className="px-6 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg transition-colors shadow-lg shadow-emerald-900/20"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
