/**
 * @deprecated This hook is deprecated. Use FDC3Context and useFDC3 from FDC3Context.tsx instead.
 * This file will be removed in a future version.
 * 
 * Migration guide:
 * - Replace `import { useFDC3 } from '@/hooks/useFDC3'`
 * - With `import { useFDC3 } from '@/context/FDC3Context'`
 * 
 * The FDC3Context provides the same API with additional features:
 * - Intent handling (raiseIntent, addIntentListener)
 * - App channel support
 * - Better error handling
 * - Context type validation
 */

import { useEffect, useState, useCallback, useRef } from 'react';
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
  type: 'finos.creditnexus.loan';
  id?: {
    LIN?: string;
    DealID?: string;
  };
  loan: CreditAgreementData;
}

type ContextHandler = (context: CreditNexusLoanContext) => void;

const contextListeners = new Set<ContextHandler>();
let lastBroadcastedContext: CreditNexusLoanContext | null = null;

export function useFDC3() {
  const [isAvailable, setIsAvailable] = useState(false);
  const [context, setContext] = useState<CreditNexusLoanContext | null>(null);
  const handlerRef = useRef<ContextHandler | null>(null);

  useEffect(() => {
    const available = typeof window !== 'undefined' && !!window.fdc3;
    setIsAvailable(available);

    const handler: ContextHandler = (ctx) => {
      setContext(ctx);
    };
    handlerRef.current = handler;
    contextListeners.add(handler);

    if (lastBroadcastedContext) {
      setContext(lastBroadcastedContext);
    }

    if (available && window.fdc3) {
      let subscription: Listener | null = null;

      window.fdc3.addContextListener('finos.creditnexus.loan', (ctx: Context) => {
        const loanContext = ctx as CreditNexusLoanContext;
        contextListeners.forEach(h => h(loanContext));
      }).then((listener: Listener) => {
        subscription = listener;
      }).catch(() => {});

      return () => {
        if (subscription) {
          subscription.unsubscribe();
        }
        if (handlerRef.current) {
          contextListeners.delete(handlerRef.current);
        }
      };
    } else {
      console.log('[FDC3 Mock] FDC3 not available, using mock mode for inter-app communication');
      return () => {
        if (handlerRef.current) {
          contextListeners.delete(handlerRef.current);
        }
      };
    }
  }, []);

  const broadcast = useCallback((loanContext: CreditNexusLoanContext) => {
    lastBroadcastedContext = loanContext;
    
    if (isAvailable && window.fdc3) {
      window.fdc3.broadcast(loanContext as Context)
        .then(() => {
          console.log('[FDC3] Broadcast successful:', loanContext);
        })
        .catch((error) => {
          console.error('[FDC3] Broadcast failed:', error);
        });
    } else {
      console.log('[FDC3 Mock] Broadcasting to all listeners:', loanContext);
      contextListeners.forEach(handler => handler(loanContext));
    }
  }, [isAvailable]);

  const clearContext = useCallback(() => {
    setContext(null);
  }, []);

  return {
    isAvailable,
    context,
    broadcast,
    clearContext,
  };
}

