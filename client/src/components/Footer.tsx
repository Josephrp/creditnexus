import { Link } from 'react-router-dom';
import { Github, Linkedin, Mail, ExternalLink } from 'lucide-react';

interface FooterProps {
  className?: string;
}

export function Footer({ className = '' }: FooterProps) {
  const currentYear = new Date().getFullYear();

  const footerLinks = {
    product: [
      { label: 'Document Parser', path: '/app/document-parser' },
      { label: 'Document Generator', path: '/app/document-generator' },
      { label: 'Trade Blotter', path: '/app/trade-blotter' },
      { label: 'GreenLens', path: '/app/green-lens' },
    ],
    resources: [
      { label: 'Documentation', href: 'https://docs.creditnexus.com', external: true },
      { label: 'API Reference', href: 'https://docs.creditnexus.com/api-reference', external: true },
      { label: 'GitHub', href: 'https://github.com/yourusername/creditnexus', external: true },
      { label: 'Blog', href: '#', external: false },
    ],
    company: [
      { label: 'About', path: '/about' },
      { label: 'Contact', path: '/contact' },
      { label: 'Privacy Policy', path: '/privacy' },
      { label: 'Terms of Service', path: '/terms' },
    ],
    legal: [
      { label: 'Compliance', path: '/compliance' },
      { label: 'Security', path: '/security' },
      { label: 'Licenses', path: '/licenses' },
    ],
  };

  const socialLinks = [
    { icon: Github, href: 'https://github.com/yourusername/creditnexus', label: 'GitHub' },
    { icon: Linkedin, href: 'https://linkedin.com/company/creditnexus', label: 'LinkedIn' },
    { icon: Mail, href: 'mailto:contact@creditnexus.com', label: 'Email' },
  ];

  return (
    <footer className={`bg-slate-900 border-t border-slate-800 ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8">
          {/* Brand Section */}
          <div className="lg:col-span-2">
            <h3 className="text-xl font-bold text-white mb-4">CreditNexus</h3>
            <p className="text-slate-400 text-sm mb-4 max-w-md">
              A next-generation financial operating system that extracts structured data from credit agreements,
              enforces compliance via policy-as-code, and verifies sustainability-linked loans using satellite imagery.
            </p>
            <div className="flex items-center gap-4">
              {socialLinks.map((social) => {
                const Icon = social.icon;
                return (
                  <a
                    key={social.label}
                    href={social.href}
                    target={social.href.startsWith('http') ? '_blank' : undefined}
                    rel={social.href.startsWith('http') ? 'noopener noreferrer' : undefined}
                    className="w-10 h-10 rounded-lg bg-slate-800 hover:bg-slate-700 flex items-center justify-center text-slate-400 hover:text-emerald-400 transition-colors"
                    aria-label={social.label}
                  >
                    <Icon className="h-5 w-5" />
                  </a>
                );
              })}
            </div>
          </div>

          {/* Product Links */}
          <div>
            <h4 className="text-sm font-semibold text-white mb-4 uppercase tracking-wider">Product</h4>
            <ul className="space-y-2">
              {footerLinks.product.map((link) => (
                <li key={link.label}>
                  <Link
                    to={link.path}
                    className="text-sm text-slate-400 hover:text-emerald-400 transition-colors"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources Links */}
          <div>
            <h4 className="text-sm font-semibold text-white mb-4 uppercase tracking-wider">Resources</h4>
            <ul className="space-y-2">
              {footerLinks.resources.map((link) => (
                <li key={link.label}>
                  {link.external ? (
                    <a
                      href={link.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-slate-400 hover:text-emerald-400 transition-colors flex items-center gap-1"
                    >
                      {link.label}
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  ) : (
                    <Link
                      to={link.href}
                      className="text-sm text-slate-400 hover:text-emerald-400 transition-colors"
                    >
                      {link.label}
                    </Link>
                  )}
                </li>
              ))}
            </ul>
          </div>

          {/* Company Links */}
          <div>
            <h4 className="text-sm font-semibold text-white mb-4 uppercase tracking-wider">Company</h4>
            <ul className="space-y-2">
              {footerLinks.company.map((link) => (
                <li key={link.label}>
                  <Link
                    to={link.path}
                    className="text-sm text-slate-400 hover:text-emerald-400 transition-colors"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-8 pt-8 border-t border-slate-800">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-sm text-slate-500">
              © {currentYear} CreditNexus. All rights reserved.
            </p>
            <div className="flex items-center gap-6">
              {footerLinks.legal.map((link) => (
                <Link
                  key={link.label}
                  to={link.path}
                  className="text-sm text-slate-500 hover:text-slate-400 transition-colors"
                >
                  {link.label}
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
