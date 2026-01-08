import { useState } from 'react';
import { useWallet } from '@/context/WalletContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Wallet, CheckCircle, AlertCircle, Loader2, Copy, ExternalLink } from 'lucide-react';

interface MetaMaskConnectProps {
  onConnect?: (account: string) => void;
  onDisconnect?: () => void;
  showDetails?: boolean;
  className?: string;
}

export function MetaMaskConnect({
  onConnect,
  onDisconnect,
  showDetails = true,
  className = '',
}: MetaMaskConnectProps) {
  const { isConnected, account, error, connect, disconnect } = useWallet();
  const [connecting, setConnecting] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleConnect = async () => {
    setConnecting(true);
    try {
      await connect();
      if (account && onConnect) {
        onConnect(account);
      }
    } catch (err) {
      console.error('Failed to connect wallet:', err);
    } finally {
      setConnecting(false);
    }
  };

  const handleDisconnect = () => {
    disconnect();
    if (onDisconnect) {
      onDisconnect();
    }
  };

  const copyAddress = () => {
    if (account) {
      navigator.clipboard.writeText(account);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const formatAddress = (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  if (isConnected && account) {
    return (
      <div className={className}>
        {showDetails ? (
          <Card className="bg-slate-800 border-slate-700">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-emerald-500/10 rounded-full flex items-center justify-center">
                    <CheckCircle className="h-5 w-5 text-emerald-400" />
                  </div>
                  <div>
                    <p className="text-sm text-slate-400">Connected</p>
                    <div className="flex items-center gap-2">
                      <p className="font-mono text-sm">{formatAddress(account)}</p>
                      <button
                        onClick={copyAddress}
                        className="text-slate-400 hover:text-slate-200 transition-colors"
                        title="Copy address"
                      >
                        {copied ? (
                          <CheckCircle className="h-4 w-4 text-emerald-400" />
                        ) : (
                          <Copy className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleDisconnect}
                  className="border-slate-600 text-slate-300 hover:bg-slate-800"
                >
                  Disconnect
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="flex items-center gap-2">
            <CheckCircle className="h-4 w-4 text-emerald-400" />
            <span className="text-sm text-slate-300">{formatAddress(account)}</span>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleDisconnect}
              className="text-slate-400 hover:text-slate-200"
            >
              Disconnect
            </Button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={className}>
      {error && (
        <div className="mb-4 p-3 bg-red-900/20 border border-red-500/50 rounded-lg">
          <div className="flex items-center gap-2 text-red-400">
            <AlertCircle className="h-4 w-4" />
            <p className="text-sm">{error}</p>
          </div>
        </div>
      )}

      {typeof window.ethereum === 'undefined' ? (
        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-6 text-center">
            <AlertCircle className="h-12 w-12 text-yellow-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">MetaMask Not Installed</h3>
            <p className="text-sm text-slate-400 mb-4">
              Please install MetaMask to connect your wallet
            </p>
            <Button
              asChild
              className="bg-blue-600 hover:bg-blue-500 text-white"
            >
              <a
                href="https://metamask.io/download"
                target="_blank"
                rel="noopener noreferrer"
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                Install MetaMask
              </a>
            </Button>
          </CardContent>
        </Card>
      ) : (
        <Button
          onClick={handleConnect}
          disabled={connecting}
          className="bg-blue-600 hover:bg-blue-500 text-white"
        >
          {connecting ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Connecting...
            </>
          ) : (
            <>
              <Wallet className="h-4 w-4 mr-2" />
              Connect MetaMask
            </>
          )}
        </Button>
      )}
    </div>
  );
}
