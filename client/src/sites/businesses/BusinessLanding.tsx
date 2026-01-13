import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { 
  ArrowRight,
  TrendingDown,
  TrendingUp,
  Building2,
  Shield,
  CheckCircle,
  BarChart3
} from 'lucide-react';

export function BusinessLanding() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 text-slate-100">
      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-emerald-400 to-blue-400 bg-clip-text text-transparent">
              CreditNexus for Businesses
            </h1>
            <p className="text-xl md:text-2xl text-slate-300 mb-8 max-w-3xl mx-auto">
              Sell your debt, buy loans, manage your credit portfolio
            </p>
            <p className="text-lg text-slate-400 mb-12 max-w-2xl mx-auto">
              Streamline your financial operations with our AI-powered platform designed for businesses
              looking to optimize their credit portfolio and access capital efficiently.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-4">
              <Button
                asChild
                size="lg"
                className="bg-emerald-600 hover:bg-emerald-500 text-white"
              >
                <Link to="/apply/business">
                  <TrendingDown className="h-5 w-5 mr-2" />
                  Sell Debt/Bonds
                </Link>
              </Button>
              <Button
                asChild
                size="lg"
                variant="outline"
                className="border-slate-600 text-slate-300 hover:bg-slate-800"
              >
                <Link to="/apply/business">
                  <TrendingUp className="h-5 w-5 mr-2" />
                  Buy Loan
                </Link>
              </Button>
              <Button
                asChild
                size="lg"
                variant="outline"
                className="border-slate-600 text-slate-300 hover:bg-slate-800"
              >
                <Link to="/dashboard">
                  Learn More
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Sell Debt Section */}
      <section className="py-20 px-4 bg-slate-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/50 rounded-full text-emerald-400 text-sm mb-6">
                <TrendingDown className="h-4 w-4" />
                <span>Debt Selling</span>
              </div>
              <h2 className="text-4xl font-bold mb-6">Sell Your Debt/Bonds</h2>
              <p className="text-xl text-slate-300 mb-6">
                Monetize your existing debt instruments and bonds by connecting with qualified investors
                through our transparent marketplace.
              </p>
              <ul className="space-y-4 mb-8">
                <li className="flex items-start gap-3">
                  <CheckCircle className="h-6 w-6 text-emerald-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="font-semibold mb-1">Competitive Pricing</h3>
                    <p className="text-slate-400">Get the best market rates for your debt instruments</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="h-6 w-6 text-emerald-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="font-semibold mb-1">Fast Processing</h3>
                    <p className="text-slate-400">Complete transactions quickly with AI-powered verification</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="h-6 w-6 text-emerald-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="font-semibold mb-1">Full Transparency</h3>
                    <p className="text-slate-400">Track every step of the process in real-time</p>
                  </div>
                </li>
              </ul>
              <Button
                asChild
                size="lg"
                className="bg-emerald-600 hover:bg-emerald-500 text-white"
              >
                <Link to="/apply/business">
                  Start Selling Debt
                  <ArrowRight className="h-5 w-5 ml-2" />
                </Link>
              </Button>
            </div>
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8">
              <h3 className="text-xl font-semibold mb-4">Requirements</h3>
              <ul className="space-y-3 text-slate-300">
                <li className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-emerald-400" />
                  <span>Valid bond/debt instrument</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-emerald-400" />
                  <span>Credit rating documentation</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-emerald-400" />
                  <span>Outstanding amount details</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-emerald-400" />
                  <span>Collateral information (if applicable)</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Buy Loan Section */}
      <section className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="order-2 lg:order-1 bg-slate-800/50 border border-slate-700 rounded-lg p-8">
              <h3 className="text-xl font-semibold mb-4">Loan Details</h3>
              <ul className="space-y-3 text-slate-300">
                <li className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-emerald-400" />
                  <span>Business financial statements</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-emerald-400" />
                  <span>Legal documentation</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-emerald-400" />
                  <span>Loan purpose and terms</span>
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-emerald-400" />
                  <span>Collateral information</span>
                </li>
              </ul>
            </div>
            <div className="order-1 lg:order-2">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/10 border border-blue-500/50 rounded-full text-blue-400 text-sm mb-6">
                <TrendingUp className="h-4 w-4" />
                <span>Loan Buying</span>
              </div>
              <h2 className="text-4xl font-bold mb-6">Buy a Loan</h2>
              <p className="text-xl text-slate-300 mb-6">
                Access the capital you need to grow your business with competitive loan terms
                and streamlined application process.
              </p>
              <ul className="space-y-4 mb-8">
                <li className="flex items-start gap-3">
                  <CheckCircle className="h-6 w-6 text-blue-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="font-semibold mb-1">Flexible Terms</h3>
                    <p className="text-slate-400">Choose loan terms that fit your business needs</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="h-6 w-6 text-blue-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="font-semibold mb-1">Quick Approval</h3>
                    <p className="text-slate-400">Fast decision-making with AI-powered assessment</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="h-6 w-6 text-blue-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="font-semibold mb-1">Competitive Rates</h3>
                    <p className="text-slate-400">Best rates based on your business profile</p>
                  </div>
                </li>
              </ul>
              <Button
                asChild
                size="lg"
                className="bg-blue-600 hover:bg-blue-500 text-white"
              >
                <Link to="/apply/business">
                  Apply for Loan
                  <ArrowRight className="h-5 w-5 ml-2" />
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Enterprise Features Section */}
      <section className="py-20 px-4 bg-slate-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Enterprise Features</h2>
            <p className="text-xl text-slate-400 max-w-2xl mx-auto">
              Powerful tools for managing your credit portfolio
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardContent className="p-6">
                <div className="w-12 h-12 bg-emerald-500/10 rounded-lg flex items-center justify-center mb-4">
                  <BarChart3 className="h-6 w-6 text-emerald-400" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Portfolio Management</h3>
                <p className="text-slate-400">
                  Track and manage all your credit instruments in one centralized dashboard
                </p>
              </CardContent>
            </Card>

            <Card className="bg-slate-800/50 border-slate-700">
              <CardContent className="p-6">
                <div className="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center mb-4">
                  <Shield className="h-6 w-6 text-blue-400" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Compliance & Risk</h3>
                <p className="text-slate-400">
                  Automated compliance checking and risk assessment for all transactions
                </p>
              </CardContent>
            </Card>

            <Card className="bg-slate-800/50 border-slate-700">
              <CardContent className="p-6">
                <div className="w-12 h-12 bg-purple-500/10 rounded-lg flex items-center justify-center mb-4">
                  <Building2 className="h-6 w-6 text-purple-400" />
                </div>
                <h3 className="text-xl font-semibold mb-2">API Integration</h3>
                <p className="text-slate-400">
                  Integrate with your existing systems via our comprehensive API
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold mb-6">Ready to Get Started?</h2>
          <p className="text-xl text-slate-400 mb-8">
            Choose the service that fits your business needs
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4">
            <Button
              asChild
              size="lg"
              className="bg-emerald-600 hover:bg-emerald-500 text-white"
            >
              <Link to="/apply/business">
                <TrendingDown className="h-5 w-5 mr-2" />
                Sell Debt/Bonds
              </Link>
            </Button>
            <Button
              asChild
              size="lg"
              className="bg-blue-600 hover:bg-blue-500 text-white"
            >
              <Link to="/apply/business">
                <TrendingUp className="h-5 w-5 mr-2" />
                Apply for Loan
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
}
