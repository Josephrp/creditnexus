import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { IndividualApplicationForm } from '@/apps/application/IndividualApplicationForm';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CheckCircle, ArrowRight } from 'lucide-react';

type FlowStep = 'intro' | 'form' | 'success';

export function IndividualApplicationFlow() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<FlowStep>('intro');
  const [applicationId, setApplicationId] = useState<number | null>(null);

  const handleFormComplete = (appId: number) => {
    setApplicationId(appId);
    setCurrentStep('success');
  };

  if (currentStep === 'intro') {
    return (
      <div className="min-h-screen surface-gradient text-[var(--color-foreground)] py-12 px-4">
        <div className="max-w-4xl mx-auto">
          <Card className="surface-panel">
            <CardContent className="p-12 text-center">
              <h1 className="text-4xl font-bold mb-4">Individual Credit Application</h1>
              <p className="text-xl text-slate-400 mb-8 max-w-2xl mx-auto">
                Complete your application in just a few simple steps. We'll guide you through the process.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                <div className="text-center">
                  <div className="w-16 h-16 bg-emerald-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl font-bold text-emerald-400">1</span>
                  </div>
                  <h3 className="text-lg font-semibold mb-2">Personal Information</h3>
                  <p className="text-sm text-slate-400">Your basic details and contact information</p>
                </div>

                <div className="text-center">
                  <div className="w-16 h-16 bg-emerald-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl font-bold text-emerald-400">2</span>
                  </div>
                  <h3 className="text-lg font-semibold mb-2">Financial Information</h3>
                  <p className="text-sm text-slate-400">Income, employment, and credit details</p>
                </div>

                <div className="text-center">
                  <div className="w-16 h-16 bg-emerald-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl font-bold text-emerald-400">3</span>
                  </div>
                  <h3 className="text-lg font-semibold mb-2">Loan Requirements</h3>
                  <p className="text-sm text-slate-400">Amount, purpose, and term preferences</p>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Button
                  onClick={() => setCurrentStep('form')}
                  className="gap-2"
                  size="lg"
                >
                  Start Application
                  <ArrowRight className="h-5 w-5" />
                </Button>
                <Button
                  variant="outline"
                  onClick={() => navigate('/individuals')}
                  size="lg"
                  className="gap-2"
                >
                  Back to Information
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (currentStep === 'success') {
    return (
      <div className="min-h-screen surface-gradient text-[var(--color-foreground)] py-12 px-4">
        <div className="max-w-4xl mx-auto">
          <Card className="surface-panel">
            <CardContent className="p-12 text-center">
              <div className="w-20 h-20 bg-emerald-500/10 rounded-full flex items-center justify-center mx-auto mb-6">
                <CheckCircle className="h-12 w-12 text-emerald-400" />
              </div>
              <h1 className="text-4xl font-bold mb-4">Application Submitted!</h1>
              <p className="text-xl text-slate-400 mb-8 max-w-2xl mx-auto">
                Thank you for your application. We've received your information and will review it shortly.
              </p>
              
              {applicationId && (
                <div className="surface-panel rounded-lg p-6 mb-8">
                  <p className="text-slate-300 mb-2">Application ID</p>
                  <p className="text-2xl font-bold text-emerald-400">#{applicationId}</p>
                </div>
              )}

              <div className="space-y-4">
                <p className="text-slate-300">What happens next?</p>
                <ul className="text-left text-slate-400 space-y-2 max-w-md mx-auto">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-5 w-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                    <span>We'll review your application within 24-48 hours</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-5 w-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                    <span>You'll receive email updates on your application status</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="h-5 w-5 text-emerald-400 flex-shrink-0 mt-0.5" />
                    <span>Check your dashboard to track progress</span>
                  </li>
                </ul>
              </div>

              <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mt-8">
                <Button
                  onClick={() => navigate('/dashboard/applications')}
                  className="gap-2"
                  size="lg"
                >
                  View My Applications
                </Button>
                <Button
                  variant="outline"
                  onClick={() => navigate('/dashboard')}
                  size="lg"
                  className="gap-2"
                >
                  Go to Dashboard
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // Form step
  return (
    <IndividualApplicationForm onComplete={handleFormComplete} />
  );
}
