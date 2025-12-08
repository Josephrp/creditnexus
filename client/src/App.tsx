import { useState } from 'react';
import { DocuDigitizer } from '@/apps/docu-digitizer/DocuDigitizer';
import { TradeBlotter } from '@/apps/trade-blotter/TradeBlotter';
import { GreenLens } from '@/apps/green-lens/GreenLens';
import { FileText, ArrowLeftRight, Leaf, Sparkles, Radio } from 'lucide-react';

type AppView = 'docu-digitizer' | 'trade-blotter' | 'green-lens';

const apps: { id: AppView; name: string; icon: React.ReactNode; description: string }[] = [
  {
    id: 'docu-digitizer',
    name: 'Docu-Digitizer',
    icon: <FileText className="h-5 w-5" />,
    description: 'Extract & digitize credit agreements',
  },
  {
    id: 'trade-blotter',
    name: 'Trade Blotter',
    icon: <ArrowLeftRight className="h-5 w-5" />,
    description: 'LMA trade confirmation & settlement',
  },
  {
    id: 'green-lens',
    name: 'GreenLens',
    icon: <Leaf className="h-5 w-5" />,
    description: 'ESG performance & margin ratchet',
  },
];

function App() {
  const [activeApp, setActiveApp] = useState<AppView>('docu-digitizer');
  const [hasBroadcast, setHasBroadcast] = useState(false);

  const handleBroadcast = () => {
    setHasBroadcast(true);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <header className="sticky top-0 z-50 border-b border-slate-700 bg-slate-900/95 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-blue-600 flex items-center justify-center">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold tracking-tight">CreditNexus</h1>
              <p className="text-xs text-slate-400">FINOS CDM Compliant</p>
            </div>
          </div>

          <nav className="flex items-center gap-1 bg-slate-800 rounded-lg p-1">
            {apps.map((app) => (
              <button
                key={app.id}
                onClick={() => setActiveApp(app.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                  activeApp === app.id
                    ? 'bg-emerald-600 text-white'
                    : 'text-slate-400 hover:text-white hover:bg-slate-700'
                }`}
              >
                {app.icon}
                <span className="hidden md:inline">{app.name}</span>
                {app.id !== 'docu-digitizer' && hasBroadcast && (
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                  </span>
                )}
              </button>
            ))}
          </nav>

          <div className="flex items-center gap-2 text-sm text-slate-400">
            <Radio className="h-4 w-4 text-emerald-500" />
            <span className="hidden sm:inline">FDC3 Enabled</span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {activeApp === 'docu-digitizer' && (
          <DocuDigitizer onBroadcast={handleBroadcast} />
        )}
        {activeApp === 'trade-blotter' && <TradeBlotter />}
        {activeApp === 'green-lens' && <GreenLens />}
      </main>

      <footer className="border-t border-slate-700 mt-auto">
        <div className="max-w-7xl mx-auto px-6 py-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-slate-400">
          <p>Powered by OpenAI GPT-4o and LangChain</p>
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <Radio className="h-3 w-3 text-emerald-500" />
              FDC3 Desktop Interoperability
            </span>
            <span>FINOS CDM Compliant</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
