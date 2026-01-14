import { Github, BookOpen, Rocket, Sparkles, Shield, Leaf, ArrowRight, CheckCircle, Users, Building2, FileCheck, TrendingUp, Phone, FileText, ArrowLeftRight } from 'lucide-react';

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 text-slate-100">
      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/50 rounded-full text-emerald-400 text-sm mb-6">
              <Sparkles className="h-4 w-4" />
              <span>AI-Powered Financial Compliance Platform</span>
            </div>
            <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-emerald-400 to-blue-400 bg-clip-text text-transparent">
              CreditNexus
            </h1>
            <p className="text-xl md:text-2xl text-slate-300 mb-8 max-w-3xl mx-auto">
              Streamline Credit Verification & Compliance for Financial Institutions
            </p>
            <p className="text-lg text-slate-400 mb-12 max-w-2xl mx-auto">
              Automate credit agreement processing, verify bonds and loans, and ensure regulatory compliance
              with AI-powered document extraction and satellite-based ground truth verification.
            </p>
            {/* Compliance Badges */}
            <div className="flex flex-wrap items-center justify-center gap-2 mb-6">
              <a
                href="https://tonic-ai.mintlify.app/compliance/fdc3-compliance"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-3 py-1.5 bg-blue-500/10 border border-blue-500/50 rounded text-blue-400 text-sm hover:bg-blue-500/20 transition-colors"
              >
                FDC3 2.0
              </a>
              <a
                href="https://tonic-ai.mintlify.app/compliance/openfin-compliance"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-3 py-1.5 bg-blue-500/10 border border-blue-500/50 rounded text-blue-400 text-sm hover:bg-blue-500/20 transition-colors"
              >
                OpenFin
              </a>
              <a
                href="https://tonic-ai.mintlify.app/compliance/dora-disclosure"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-3 py-1.5 bg-green-500/10 border border-green-500/50 rounded text-green-400 text-sm hover:bg-green-500/20 transition-colors"
              >
                DORA Compliant
              </a>
              <a
                href="https://tonic-ai.mintlify.app/compliance/gdpr-compliance"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-3 py-1.5 bg-green-500/10 border border-green-500/50 rounded text-green-400 text-sm hover:bg-green-500/20 transition-colors"
              >
                GDPR Compliant
              </a>
              <a
                href="https://tonic-ai.mintlify.app/compliance/cdm-compliance"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-3 py-1.5 bg-blue-500/10 border border-blue-500/50 rounded text-blue-400 text-sm hover:bg-blue-500/20 transition-colors"
              >
                FINOS CDM
              </a>
            </div>
            <div className="flex flex-wrap items-center justify-center gap-4">
              <a
                href="https://github.com/josephrp/creditnexus"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-6 py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg transition-colors"
              >
                <Github className="h-5 w-5 mr-2" />
                View on GitHub
              </a>
              <a
                href="https://tonic-ai.mintlify.app"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center px-6 py-3 border border-slate-600 text-slate-300 hover:bg-slate-800 rounded-lg transition-colors"
              >
                <BookOpen className="h-5 w-5 mr-2" />
                Documentation
              </a>
              <a
                href="/apply"
                className="inline-flex items-center px-6 py-3 border border-slate-600 text-slate-300 hover:bg-slate-800 rounded-lg transition-colors"
              >
                <Rocket className="h-5 w-5 mr-2" />
                Get Started
              </a>
            </div>
            {/* Social Links */}
            <div className="flex flex-wrap items-center justify-center gap-4 mt-4">
              <a
                href="https://x.com/josephpollack"
                target="_blank"
                rel="noopener noreferrer"
                className="text-slate-400 hover:text-slate-100 transition-colors"
                title="Twitter/X"
              >
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                </svg>
              </a>
              <a
                href="https://github.com/fintechtonic"
                target="_blank"
                rel="noopener noreferrer"
                className="text-slate-400 hover:text-slate-100 transition-colors"
                title="GitHub"
              >
                <Github className="h-5 w-5" />
              </a>
              <a
                href="https://hf.co/tonic"
                target="_blank"
                rel="noopener noreferrer"
                className="text-slate-400 hover:text-slate-100 transition-colors"
                title="HuggingFace"
              >
                <span className="text-sm font-semibold">🤗</span>
              </a>
              <a
                href="https://discord.gg/7YS4Cz2Deq"
                target="_blank"
                rel="noopener noreferrer"
                className="text-slate-400 hover:text-slate-100 transition-colors"
                title="Discord"
              >
                <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
                </svg>
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Value Proposition Section */}
      <section className="py-20 px-4 bg-slate-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Built for Financial Institutions</h2>
            <p className="text-xl text-slate-400 max-w-2xl mx-auto">
              Streamline operations, reduce risk, and ensure compliance
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg hover:border-emerald-500/50 transition-colors">
              <div className="w-12 h-12 bg-emerald-500/10 rounded-lg flex items-center justify-center mb-4">
                <Building2 className="h-6 w-6 text-emerald-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Loan Granting Companies</h3>
              <p className="text-slate-400">
                Automate credit agreement processing, extract structured data, and verify loan terms
                with AI-powered document analysis. Reduce processing time from days to minutes.
              </p>
            </div>

            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg hover:border-emerald-500/50 transition-colors">
              <div className="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center mb-4">
                <FileCheck className="h-6 w-6 text-blue-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Company Bond Verification</h3>
              <p className="text-slate-400">
                Verify corporate bonds and debt instruments with automated compliance checking.
                Ensure all bond terms meet regulatory requirements and internal policies.
              </p>
            </div>

            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg hover:border-emerald-500/50 transition-colors">
              <div className="w-12 h-12 bg-green-500/10 rounded-lg flex items-center justify-center mb-4">
                <Users className="h-6 w-6 text-green-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Individual Bond Verification</h3>
              <p className="text-slate-400">
                Process and verify individual bond applications with automated risk assessment
                and compliance validation. Accelerate approval workflows.
              </p>
            </div>

            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg hover:border-emerald-500/50 transition-colors">
              <div className="w-12 h-12 bg-yellow-500/10 rounded-lg flex items-center justify-center mb-4">
                <Shield className="h-6 w-6 text-yellow-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Regulatory Compliance</h3>
              <p className="text-slate-400">
                Real-time policy enforcement for MiCA, Basel III, and FATF regulations.
                Policy-as-code ensures consistent compliance across all transactions.
              </p>
            </div>

            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg hover:border-emerald-500/50 transition-colors">
              <div className="w-12 h-12 bg-purple-500/10 rounded-lg flex items-center justify-center mb-4">
                <Leaf className="h-6 w-6 text-purple-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Satellite Verification</h3>
              <p className="text-slate-400">
                Verify sustainability-linked loans using satellite imagery and NDVI analysis.
                Ground truth verification for ESG compliance.
              </p>
            </div>

            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg hover:border-emerald-500/50 transition-colors">
              <div className="w-12 h-12 bg-cyan-500/10 rounded-lg flex items-center justify-center mb-4">
                <TrendingUp className="h-6 w-6 text-cyan-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Access to Finance</h3>
              <p className="text-slate-400">
                Streamline application processes for individuals and businesses seeking credit.
                AI-powered assessment accelerates decision-making.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Market Opportunity Section */}
      <section className="py-20 px-4 bg-gradient-to-b from-slate-900 to-slate-800">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Market Opportunity</h2>
            <p className="text-xl text-slate-400 max-w-2xl mx-auto">
              CreditNexus addresses massive markets with significant growth potential
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg">
              <div className="text-3xl font-bold text-emerald-400 mb-2">$133T</div>
              <div className="text-sm text-slate-400 mb-2">Global Bond Market (2024)</div>
              <div className="text-xs text-emerald-300">→ $140-150T by 2026 (3-5% CAGR)</div>
              <div className="mt-4 text-sm text-slate-300">
                CreditNexus enables bond issuance and securitization for small lenders, reducing deal times from weeks to days.
              </div>
            </div>

            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg">
              <div className="text-3xl font-bold text-blue-400 mb-2">$12-15T</div>
              <div className="text-sm text-slate-400 mb-2">Global Loan Market (Annual Originations)</div>
              <div className="text-xs text-blue-300">→ $14-18T by 2026</div>
              <div className="mt-4 text-sm text-slate-300">
                AI-powered automation reduces operational costs by 30-50%, opening doors for small players.
              </div>
            </div>

            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg">
              <div className="text-3xl font-bold text-green-400 mb-2">$0.5-0.4T</div>
              <div className="text-sm text-slate-400 mb-2">Green Bonds/Lending (2024)</div>
              <div className="text-xs text-green-300">→ $1-2T by 2030 (15-20% CAGR)</div>
              <div className="mt-4 text-sm text-slate-300">
                Satellite verification reduces greenwashing risks, positioning CreditNexus for rapid growth.
              </div>
            </div>

            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg">
              <div className="text-3xl font-bold text-purple-400 mb-2">$13T</div>
              <div className="text-sm text-slate-400 mb-2">Securitization Market (Assets)</div>
              <div className="text-xs text-purple-300">→ $15-18T by 2028 (4-6% CAGR)</div>
              <div className="mt-4 text-sm text-slate-300">
                CreditNexus enables small lenders to bundle and sell loans, democratizing securitization access.
              </div>
            </div>

            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg">
              <div className="text-3xl font-bold text-yellow-400 mb-2">$0.2-0.3T</div>
              <div className="text-sm text-slate-400 mb-2">Loan Recovery Market (2024)</div>
              <div className="text-xs text-yellow-300">→ $0.3-0.4T by 2030 (5-7% CAGR)</div>
              <div className="mt-4 text-sm text-slate-300">
                Automated recovery workflows with Twilio integration target this growing market.
              </div>
            </div>

            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg">
              <div className="text-3xl font-bold text-cyan-400 mb-2">95%</div>
              <div className="text-sm text-slate-400 mb-2">Paperwork Reduction</div>
              <div className="text-xs text-cyan-300">AI-driven automation</div>
              <div className="mt-4 text-sm text-slate-300">
                CreditNexus automates 95% of paperwork, reducing processing time from weeks to days.
              </div>
            </div>
          </div>

          <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8">
            <h3 className="text-2xl font-semibold mb-4 text-center">Total Addressable Market (TAM)</h3>
            <p className="text-slate-300 text-center mb-6">
              Conservatively, 1-5% of the $200-500 billion fintech lending sub-market, yielding a <span className="text-emerald-400 font-bold">$2-25 billion opportunity</span>
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-emerald-400 mb-2">$50K-200K</div>
                <div className="text-sm text-slate-400">Per Deployment Service</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-400 mb-2">$1K-10K</div>
                <div className="text-sm text-slate-400">Monthly Subscription Tiers</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-400 mb-2">10-20%</div>
                <div className="text-sm text-slate-400">Consulting Margins</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">About CreditNexus</h2>
            <p className="text-xl text-slate-400 max-w-2xl mx-auto">
              A startup focused on democratizing access to finance and ensuring compliance
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h3 className="text-2xl font-semibold mb-4">Our Mission</h3>
              <p className="text-slate-300 mb-4">
                CreditNexus was founded by a team with over 20 years of combined experience in the financial industry.
                Our deep understanding of banking operations, payment systems, and regulatory compliance drives our
                mission to bridge the gap between complex financial regulations and accessible credit services.
                We believe that compliance shouldn't be a barrier to financial inclusion.
              </p>
              <p className="text-slate-300 mb-4">
                Our platform automates the tedious process of credit agreement verification, making it
                faster and more reliable for financial institutions to process loans while ensuring
                full regulatory compliance. By automating 95% of paperwork, we reduce processing time from weeks to days.
              </p>
              <p className="text-slate-300">
                By combining AI-powered document extraction with satellite-based verification, we help
                financial institutions reduce operational costs by 30-50%, minimize risk, and accelerate time-to-market
                for new credit products.
              </p>
            </div>
            <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-8">
              <h3 className="text-xl font-semibold mb-6">Key Focus Areas</h3>
              <ul className="space-y-4">
                <li className="flex items-start gap-3">
                  <CheckCircle className="h-6 w-6 text-emerald-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold mb-1">Compliance Automation</h4>
                    <p className="text-slate-400 text-sm">
                      Automated policy enforcement ensures every transaction meets regulatory requirements
                    </p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="h-6 w-6 text-emerald-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold mb-1">Access to Finance</h4>
                    <p className="text-slate-400 text-sm">
                      Streamlined application processes for individuals and businesses seeking credit
                    </p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="h-6 w-6 text-emerald-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold mb-1">Verification & Risk Assessment</h4>
                    <p className="text-slate-400 text-sm">
                      AI and satellite-based verification for bonds, loans, and sustainability claims
                    </p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="h-6 w-6 text-emerald-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold mb-1">CDM Standardization</h4>
                    <p className="text-slate-400 text-sm">
                      Full FINOS CDM compliance ensures interoperability with existing financial systems
                    </p>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Our Team</h2>
            <p className="text-xl text-slate-400 max-w-2xl mx-auto">
              Experienced professionals with deep financial industry expertise
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg text-center">
              <div className="w-24 h-24 bg-gradient-to-br from-emerald-500 to-blue-600 rounded-full mx-auto mb-4 flex items-center justify-center">
                <Users className="h-12 w-12 text-white" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Joseph Pollack</h3>
              <p className="text-emerald-400 mb-2">Chief Information Officer</p>
              <p className="text-sm text-slate-400">Strategic technology leadership and architecture</p>
            </div>

            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg text-center">
              <div className="w-24 h-24 bg-gradient-to-br from-emerald-500 to-blue-600 rounded-full mx-auto mb-4 flex items-center justify-center">
                <Users className="h-12 w-12 text-white" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Biniyam Ajew</h3>
              <p className="text-emerald-400 mb-2">Senior Developer</p>
              <p className="text-sm text-slate-400">Full-stack development and system architecture</p>
            </div>

            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg text-center">
              <div className="w-24 h-24 bg-gradient-to-br from-emerald-500 to-blue-600 rounded-full mx-auto mb-4 flex items-center justify-center">
                <Users className="h-12 w-12 text-white" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Boris Li</h3>
              <p className="text-emerald-400 mb-2">Junior Developer</p>
              <p className="text-sm text-slate-400">
                10 years of experience at Citibank and Mastercard in payment systems, 
                banking operations, and financial technology
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Comprehensive Features Section */}
      <section className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Comprehensive Feature Suite</h2>
            <p className="text-xl text-slate-400 max-w-2xl mx-auto">
              End-to-end loan management from extraction to recovery
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg">
              <div className="w-12 h-12 bg-red-500/10 rounded-lg flex items-center justify-center mb-4">
                <Phone className="h-6 w-6 text-red-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Loan Recovery System</h3>
              <p className="text-slate-400 text-sm mb-3">
                Automated default detection with Twilio SMS and voice communication. Manage borrower contacts and recovery workflows.
              </p>
              <div className="text-xs text-slate-500">Twilio Integration • Default Detection • CDM Events</div>
            </div>

            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg">
              <div className="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center mb-4">
                <TrendingUp className="h-6 w-6 text-blue-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Payment Systems (x402)</h3>
              <p className="text-slate-400 text-sm mb-3">
                Blockchain-based payment processing using x402 protocol and USDC stablecoin on Base network.
              </p>
              <div className="text-xs text-slate-500">x402 Protocol • USDC Payments • MetaMask Integration</div>
            </div>

            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg">
              <div className="w-12 h-12 bg-green-500/10 rounded-lg flex items-center justify-center mb-4">
                <Shield className="h-6 w-6 text-green-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Blockchain Notarization</h3>
              <p className="text-slate-400 text-sm mb-3">
                Immutable document notarization using smart contracts on Base network with MetaMask signing.
              </p>
              <div className="text-xs text-slate-500">Smart Contracts • Base Network • Multi-Party Signing</div>
            </div>

            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg">
              <div className="w-12 h-12 bg-purple-500/10 rounded-lg flex items-center justify-center mb-4">
                <FileCheck className="h-6 w-6 text-purple-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Digital Signing</h3>
              <p className="text-slate-400 text-sm mb-3">
                Professional e-signature workflows with DigiSigner integration and webhook notifications.
              </p>
              <div className="text-xs text-slate-500">DigiSigner • Webhooks • Legal Validity</div>
            </div>

            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg">
              <div className="w-12 h-12 bg-cyan-500/10 rounded-lg flex items-center justify-center mb-4">
                <Building2 className="h-6 w-6 text-cyan-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Dealflow Management</h3>
              <p className="text-slate-400 text-sm mb-3">
                Comprehensive deal tracking with timeline views, notes, and collaboration tools.
              </p>
              <div className="text-xs text-slate-500">Deal Dashboard • Timeline • Collaboration</div>
            </div>

            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg">
              <div className="w-12 h-12 bg-yellow-500/10 rounded-lg flex items-center justify-center mb-4">
                <FileText className="h-6 w-6 text-yellow-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2">One-Click Audit Reports</h3>
              <p className="text-slate-400 text-sm mb-3">
                Automated audit report generation with CDM event exploration and policy decision tracking.
              </p>
              <div className="text-xs text-slate-500">Report Generation • CDM Events • Export</div>
            </div>

            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg">
              <div className="w-12 h-12 bg-indigo-500/10 rounded-lg flex items-center justify-center mb-4">
                <Sparkles className="h-6 w-6 text-indigo-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Securitization Workflow</h3>
              <p className="text-slate-400 text-sm mb-3">
                Complete securitization from pool creation to ERC-721 tranche token minting and payment distribution.
              </p>
              <div className="text-xs text-slate-500">Pool Creation • Token Minting • Payment Waterfall</div>
            </div>

            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg">
              <div className="w-12 h-12 bg-emerald-500/10 rounded-lg flex items-center justify-center mb-4">
                <FileText className="h-6 w-6 text-emerald-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Document Extraction</h3>
              <p className="text-slate-400 text-sm mb-3">
                AI-powered extraction from PDFs using GPT-4o, vLLM, or HuggingFace with CDM compliance.
              </p>
              <div className="text-xs text-slate-500">LLM Extraction • CDM Compliance • Policy Enforcement</div>
            </div>

            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg">
              <div className="w-12 h-12 bg-pink-500/10 rounded-lg flex items-center justify-center mb-4">
                <ArrowLeftRight className="h-6 w-6 text-pink-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Trade Execution</h3>
              <p className="text-slate-400 text-sm mb-3">
                LMA trade confirmation and settlement with CDM event generation and policy enforcement.
              </p>
              <div className="text-xs text-slate-500">LMA Templates • Settlement • CDM Events</div>
            </div>
          </div>
        </div>
      </section>

      {/* Technology Stack Section */}
      <section className="py-20 px-4 bg-slate-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Technology Stack</h2>
            <p className="text-xl text-slate-400 max-w-2xl mx-auto">
              Built with modern, production-ready technologies
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg text-center">
              <h3 className="text-lg font-semibold mb-2">Backend</h3>
              <ul className="text-sm text-slate-400 space-y-1">
                <li>FastAPI</li>
                <li>SQLAlchemy 2.0</li>
                <li>PostgreSQL</li>
                <li>Pydantic 2.0</li>
              </ul>
            </div>

            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg text-center">
              <h3 className="text-lg font-semibold mb-2">Frontend</h3>
              <ul className="text-sm text-slate-400 space-y-1">
                <li>React 18</li>
                <li>TypeScript</li>
                <li>Vite</li>
                <li>Tailwind CSS</li>
              </ul>
            </div>

            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg text-center">
              <h3 className="text-lg font-semibold mb-2">AI/ML</h3>
              <ul className="text-sm text-slate-400 space-y-1">
                <li>OpenAI GPT-4o</li>
                <li>LangChain</li>
                <li>TorchGeo</li>
                <li>vLLM / HuggingFace</li>
              </ul>
            </div>

            <div className="p-6 bg-slate-800/50 border border-slate-700 rounded-lg text-center">
              <h3 className="text-lg font-semibold mb-2">Standards</h3>
              <ul className="text-sm text-slate-400 space-y-1">
                <li>FINOS CDM</li>
                <li>FDC3 2.0</li>
                <li>ISO 8601</li>
                <li>x402 Protocol</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* GitHub Integration Section */}
      <section className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="p-12 bg-slate-800 border border-slate-700 rounded-lg">
            <div className="flex flex-col md:flex-row items-center justify-between gap-8">
              <div className="flex-1">
                <h2 className="text-3xl font-bold mb-4">Open Source & Community Driven</h2>
                <p className="text-lg text-slate-400 mb-6">
                  CreditNexus is open source and welcomes contributions from the community.
                  Star us on GitHub to stay updated with the latest features and improvements.
                </p>
                <div className="flex flex-wrap gap-4">
                  <a
                    href="https://github.com/josephrp/creditnexus"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
                  >
                    <Github className="h-5 w-5 mr-2" />
                    View Repository
                  </a>
                  <a
                    href="https://tonic-ai.mintlify.app"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-6 py-3 border border-slate-600 text-slate-300 hover:bg-slate-800 rounded-lg transition-colors"
                  >
                    <BookOpen className="h-5 w-5 mr-2" />
                    Read Documentation
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </a>
                </div>
              </div>
              <div className="flex-shrink-0">
                <div className="w-32 h-32 bg-gradient-to-br from-emerald-500 to-blue-600 rounded-2xl flex items-center justify-center">
                  <Github className="h-16 w-16 text-white" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold mb-6">Ready to Get Started?</h2>
          <p className="text-xl text-slate-400 mb-8">
            Join the future of financial operations with CreditNexus
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4">
            <a
              href="/apply"
              className="inline-flex items-center px-6 py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg transition-colors"
            >
              <Rocket className="h-5 w-5 mr-2" />
              Start Application
            </a>
            <a
              href="https://tonic-ai.mintlify.app"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center px-6 py-3 border border-slate-600 text-slate-300 hover:bg-slate-800 rounded-lg transition-colors"
            >
              <BookOpen className="h-5 w-5 mr-2" />
              View Documentation
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-700 py-12 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="text-slate-400">
              <p>&copy; 2026 CreditNexus. Price & create structured financial products.</p>
            </div>
            <div className="flex items-center gap-6">
              <a
                href="/licence"
                className="text-slate-400 hover:text-slate-100 transition-colors text-sm"
              >
                License
              </a>
              <span className="text-slate-400">•</span>
              <a
                href="/rail"
                className="text-slate-400 hover:text-slate-100 transition-colors text-sm"
              >
                RAIL
              </a>
              <a
                href="https://github.com/josephrp/creditnexus"
                target="_blank"
                rel="noopener noreferrer"
                className="text-slate-400 hover:text-slate-100 transition-colors"
              >
                <Github className="h-5 w-5" />
              </a>
              <a
                href="https://tonic-ai.mintlify.app"
                target="_blank"
                rel="noopener noreferrer"
                className="text-slate-400 hover:text-slate-100 transition-colors"
              >
                <BookOpen className="h-5 w-5" />
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
