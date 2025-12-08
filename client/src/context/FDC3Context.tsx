import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from 'react';
import type { Context, Listener } from '@finos/fdc3';

export interface ESGKPITarget {
  kpi_type: string;
  target_value: number;
  current_value?: number;
  unit: string;
  margin_adjustment_bps: number;
}

export interface Party {
  id: string;
  name: string;
  role: string;
  lei?: string;
}

export interface Facility {
  facility_name: string;
  commitment_amount: { amount: number; currency: string };
  interest_terms: {
    rate_option: { benchmark: string; spread_bps: number };
    payment_frequency: { period: string; period_multiplier: number };
  };
  maturity_date: string;
}

export interface CreditAgreementData {
  agreement_date?: string;
  parties?: Party[];
  facilities?: Facility[];
  governing_law?: string;
  sustainability_linked?: boolean;
  esg_kpi_targets?: ESGKPITarget[];
  deal_id?: string;
  loan_identification_number?: string;
  extraction_status?: string;
}

export interface CreditNexusLoanContext extends Context {
  type: 'fdc3.creditnexus.loan';
  id?: {
    LIN?: string;
    DealID?: string;
  };
  loan: CreditAgreementData;
}

interface FDC3ContextValue {
  isAvailable: boolean;
  context: CreditNexusLoanContext | null;
  broadcast: (ctx: CreditNexusLoanContext) => void;
  clearContext: () => void;
}

const FDC3Context = createContext<FDC3ContextValue | null>(null);

export function FDC3Provider({ children }: { children: ReactNode }) {
  const [isAvailable, setIsAvailable] = useState(false);
  const [context, setContext] = useState<CreditNexusLoanContext | null>(null);

  useEffect(() => {
    const available = typeof window !== 'undefined' && !!window.fdc3;
    setIsAvailable(available);

    if (available && window.fdc3) {
      let subscription: Listener | null = null;

      window.fdc3.addContextListener('fdc3.creditnexus.loan', (ctx: Context) => {
        setContext(ctx as CreditNexusLoanContext);
      }).then((listener: Listener) => {
        subscription = listener;
      }).catch(() => {});

      return () => {
        if (subscription) {
          subscription.unsubscribe();
        }
      };
    } else {
      console.log('[FDC3 Mock] FDC3 not available, using mock mode for inter-app communication');
    }
  }, []);

  const broadcast = useCallback((loanContext: CreditNexusLoanContext) => {
    setContext(loanContext);
    
    if (isAvailable && window.fdc3) {
      window.fdc3.broadcast(loanContext as Context)
        .then(() => {
          console.log('[FDC3] Broadcast successful:', loanContext);
        })
        .catch((error) => {
          console.error('[FDC3] Broadcast failed:', error);
        });
    } else {
      console.log('[FDC3 Mock] Broadcasting context:', loanContext);
    }
  }, [isAvailable]);

  const clearContext = useCallback(() => {
    setContext(null);
  }, []);

  return (
    <FDC3Context.Provider value={{ isAvailable, context, broadcast, clearContext }}>
      {children}
    </FDC3Context.Provider>
  );
}

export function useFDC3() {
  const ctx = useContext(FDC3Context);
  if (!ctx) {
    throw new Error('useFDC3 must be used within an FDC3Provider');
  }
  return ctx;
}
