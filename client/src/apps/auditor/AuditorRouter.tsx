import { useLocation } from 'react-router-dom';
import { AuditorLayout } from './AuditorLayout';
import { AuditDashboard } from './AuditDashboard';
import { AuditDetail } from './AuditDetail';
import { DealAuditView } from './DealAuditView';
import { LoanAuditView } from './LoanAuditView';
import { FilingAuditView } from './FilingAuditView';
import { AuditReportGenerator } from './AuditReportGenerator';
import { CDMEventExplorer } from './CDMEventExplorer';
import { PolicyDecisionsExplorer } from './PolicyDecisionsExplorer';

export function AuditorRouter() {
  const location = useLocation();
  const pathname = location.pathname;

  const renderContent = () => {
    // ... same as before but using PolicyDecisionsExplorer
    if (pathname.startsWith('/auditor/logs/')) {
      const match = pathname.match(/\/auditor\/logs\/(\d+)/);
      if (match) {
        return <AuditDetail />;
      }
    }

    if (pathname.startsWith('/auditor/deals/')) {
      const match = pathname.match(/\/auditor\/deals\/(\d+)/);
      if (match) {
        return <DealAuditView />;
      }
    }

    if (pathname.startsWith('/auditor/loans/')) {
      const match = pathname.match(/\/auditor\/loans\/([^/]+)/);
      if (match) {
        return <LoanAuditView />;
      }
    }

    if (pathname.startsWith('/auditor/filings/')) {
      const match = pathname.match(/\/auditor\/filings\/(\d+)/);
      if (match) {
        return <FilingAuditView />;
      }
    }

    if (pathname.startsWith('/auditor/reports')) {
      return <AuditReportGenerator />;
    }

    if (pathname.startsWith('/auditor/policy')) {
      return <PolicyDecisionsExplorer />;
    }

    if (pathname.startsWith('/auditor/cdm-events')) {
      return <CDMEventExplorer />;
    }

    if (pathname === '/auditor/logs') {
      return <AuditDashboard showLogsOnly={true} />;
    }

    return <AuditDashboard />;
  };

  return (
    <AuditorLayout>
      {renderContent()}
    </AuditorLayout>
  );
}
