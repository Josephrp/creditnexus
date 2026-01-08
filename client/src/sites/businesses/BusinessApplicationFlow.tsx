import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BusinessApplicationForm } from '@/apps/application/BusinessApplicationForm';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CheckCircle, ArrowRight, TrendingDown, TrendingUp } from 'lucide-react';

type FlowStep = 'intro' | 'form' | 'success';

export function BusinessApplicationFlow() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<FlowStep>('intro');
  const [applicationId, setApplicationId] = useState<number | null>(null);
  const [applicationType, setApplicationType] = useState<'debt_selling' | 'loan_buying' | null>(null);

  const handleFormComplete = (appId: number) => {
    setApplicationId(appId);
    setCurrentStep('success');
  };

  if (currentStep === 'intro') {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 text-slate-100 py-12 px-4">
        <div className="max-w-4xl mx-auto">
          <Card className="bg-slate-800 border-slate-700">
            <CardContent className="p-12 text-center">
              <h1 className="text-4xl font-bold mb-4">Business Credit Application</h1>
              <p className="text-xl text-slate-400 mb-8 max-w-2xl mx-auto">
                Choose the service that fits your business needs
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
                <Card 
                  className="bg-slate-900 border-slate-700 cursor-pointer hover:border-emerald-500 transition-colors"
                  onClick={() => {
                    setApplicationType('debt_selling');
                    setCurrentStep('form');
                  }}
                >
                  <CardContent className="p-8 text-center">
                    <div className="w-16 h-16 bg-emerald-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                      <TrendingDown className="h-8 w-8 text-emerald-400" />
                    </div>
                    <h3 className="text-2xl font-semibold mb-2">Sell Debt/Bonds</h3>
                    <p className="text-slate-400 mb-4">
                      Monetize your existing debt instruments and bonds by connecting with qualified investors
                    </p>
                    <ul className="text-left text-sm text-slate-300 space-y-2 mb-6">
                      <li className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-emerald-400" />
                        <span>Competitive pricing</span>
                      </li>
                      <li className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-emerald-400" />
                        <span>Fast processing</span>
                      </li>
                      <li className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-emerald-400" />
                        <span>Full transparency</span>
                      </li>
                    </ul>
                    <Button className="w-full bg-emerald-600 hover:bg-emerald-500">
                      Start Selling
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </Button>
                  </CardContent>
                </Card>

                <Card 
                  className="bg-slate-900 border-slate-700 cursor-pointer hover:border-blue-500 transition-colors"
                  onClick={() => {
                    setApplicationType('loan_buying');
                    setCurrentStep('form');
                  }}
                >
                  <CardContent className="p-8 text-center">
                    <div className="w-16 h-16 bg-blue-500/10 rounded-full flex items-center justify-center mx-auto mb-4">
                      <TrendingUp className="h-8 w-8 text-blue-400" />
                    </div>
                    <h3 className="text-2xl font-semibold mb-2">Buy a Loan</h3>
                    <p className="text-slate-400 mb-4">
                      Access the capital you need to grow your business with competitive loan terms
                    </p>
                    <ul className="text-left text-sm text-slate-300 space-y-2 mb-6">
                      <li className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-blue-400" />
                        <span>Flexible terms</span>
                      </li>
                      <li className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-blue-400" />
                        <span>Quick approval</span>
                      </li>
                      <li className="flex items-center gap-2">
                        <CheckCircle className="h-4 w-4 text-blue-400" />
                        <span>Competitive rates</span>
                      </li>
                    </ul>
                    <Button className="w-full bg-blue-600 hover:bg-blue-500">
                      Apply for Loan
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </Button>
                  </CardContent>
                </Card>
              </div>

              <Button
                variant="outline"
                onClick={() => navigate('/businesses')}
                className="border-slate-600 text-slate-300 hover:bg-slate-800"
              >
                Back to Information
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (currentStep === 'success') {
    return (
      <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 text-slate-100 py-12 px-4">
        <div className="max-w-4xl mx-auto">
          <Card className="bg-slate-800 border-slate-700">
            <CardContent className="p-12 text-center">
              <div className="w-20 h-20 bg-emerald-500/10 rounded-full flex items-center justify-center mx-auto mb-6">
                <CheckCircle className="h-12 w-12 text-emerald-400" />
              </div>
              <h1 className="text-4xl font-bold mb-4">Application Submitted!</h1>
              <p className="text-xl text-slate-400 mb-8 max-w-2xl mx-auto">
                Thank you for your business application. We've received your information and will review it shortly.
              </p>
              
              {applicationId && (
                <div className="bg-slate-900 rounded-lg p-6 mb-8">
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
                  className="bg-emerald-600 hover:bg-emerald-500 text-white"
                >
                  View My Applications
                </Button>
                <Button
                  variant="outline"
                  onClick={() => navigate('/dashboard')}
                  className="border-slate-600 text-slate-300 hover:bg-slate-800"
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
    <BusinessApplicationForm 
      defaultApplicationType={applicationType || undefined}
      onComplete={handleFormComplete}
    />
  );
}
