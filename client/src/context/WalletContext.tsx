import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface WalletState {
  isConnected: boolean;
  account: string | null;
  chainId: number | null;
  provider: any | null;
  error: string | null;
}

interface WalletContextType extends WalletState {
  connect: () => Promise<void>;
  disconnect: () => void;
  switchChain?: (chainId: number) => Promise<void>;
  signMessage: (message: string) => Promise<string>;
}

const WalletContext = createContext<WalletContextType | undefined>(undefined);

export function WalletProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<WalletState>({
    isConnected: false,
    account: null,
    chainId: null,
    provider: null,
    error: null,
  });

  // Check if wallet is already connected on mount
  useEffect(() => {
    checkConnection();
    
    // Listen for account changes
    if (typeof window.ethereum !== 'undefined') {
      window.ethereum.on('accountsChanged', handleAccountsChanged);
      window.ethereum.on('chainChanged', handleChainChanged);
      window.ethereum.on('disconnect', handleDisconnect);
    }

    return () => {
      if (typeof window.ethereum !== 'undefined') {
        window.ethereum.removeListener('accountsChanged', handleAccountsChanged);
        window.ethereum.removeListener('chainChanged', handleChainChanged);
        window.ethereum.removeListener('disconnect', handleDisconnect);
      }
    };
  }, []);

  const checkConnection = async () => {
    if (typeof window.ethereum === 'undefined') {
      setState(prev => ({ ...prev, error: 'MetaMask is not installed' }));
      return;
    }

    try {
      const accounts = await window.ethereum.request({ method: 'eth_accounts' });
      if (accounts.length > 0) {
        const chainId = await window.ethereum.request({ method: 'eth_chainId' });
        setState({
          isConnected: true,
          account: accounts[0],
          chainId: parseInt(chainId, 16),
          provider: window.ethereum,
          error: null,
        });
      }
    } catch (err) {
      setState(prev => ({
        ...prev,
        error: err instanceof Error ? err.message : 'Failed to check connection',
      }));
    }
  };

  const handleAccountsChanged = (accounts: string[]) => {
    if (accounts.length === 0) {
      setState({
        isConnected: false,
        account: null,
        chainId: null,
        provider: null,
        error: null,
      });
    } else {
      setState(prev => ({
        ...prev,
        account: accounts[0],
      }));
    }
  };

  const handleChainChanged = (chainId: string) => {
    setState(prev => ({
      ...prev,
      chainId: parseInt(chainId, 16),
    }));
  };

  const handleDisconnect = () => {
    setState({
      isConnected: false,
      account: null,
      chainId: null,
      provider: null,
      error: null,
    });
  };

  const connect = async () => {
    if (typeof window.ethereum === 'undefined') {
      setState(prev => ({ ...prev, error: 'MetaMask is not installed' }));
      throw new Error('MetaMask is not installed');
    }

    try {
      const accounts = await window.ethereum.request({
        method: 'eth_requestAccounts',
      });

      if (accounts.length === 0) {
        throw new Error('No accounts found');
      }

      const chainId = await window.ethereum.request({ method: 'eth_chainId' });

      setState({
        isConnected: true,
        account: accounts[0],
        chainId: parseInt(chainId, 16),
        provider: window.ethereum,
        error: null,
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to connect wallet';
      setState(prev => ({ ...prev, error: errorMessage }));
      throw err;
    }
  };

  const disconnect = () => {
    setState({
      isConnected: false,
      account: null,
      chainId: null,
      provider: null,
      error: null,
    });
  };

  const switchChain = async (chainId: number) => {
    if (!state.provider) {
      throw new Error('Wallet not connected');
    }

    try {
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: `0x${chainId.toString(16)}` }],
      });
    } catch (err) {
      // If chain doesn't exist, try to add it
      if ((err as { code?: number }).code === 4902) {
        // Chain not added, would need to add it here
        throw new Error('Chain not supported');
      }
      throw err;
    }
  };

  const signMessage = async (message: string): Promise<string> => {
    if (!state.account || !state.provider) {
      throw new Error('Wallet not connected');
    }

    try {
      const signature = await window.ethereum.request({
        method: 'personal_sign',
        params: [message, state.account],
      });
      return signature as string;
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to sign message');
    }
  };

  return (
    <WalletContext.Provider
      value={{
        ...state,
        connect,
        disconnect,
        switchChain,
        signMessage,
      }}
    >
      {children}
    </WalletContext.Provider>
  );
}

export function useWallet() {
  const context = useContext(WalletContext);
  if (context === undefined) {
    throw new Error('useWallet must be used within a WalletProvider');
  }
  return context;
}

// Extend Window interface for MetaMask
declare global {
  interface Window {
    ethereum?: {
      request: (args: { method: string; params?: unknown[] }) => Promise<unknown>;
      on: (event: string, handler: (...args: unknown[]) => void) => void;
      removeListener: (event: string, handler: (...args: unknown[]) => void) => void;
    };
  }
}
