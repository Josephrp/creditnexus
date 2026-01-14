import { Link } from 'react-router-dom';
import { Github, Linkedin, Mail, ExternalLink } from 'lucide-react';
import { useThemeClasses } from '@/utils/themeUtils';

interface FooterProps {
  className?: string;
}

export function Footer({ className = '' }: FooterProps) {
  const currentYear = new Date().getFullYear();
  const classes = useThemeClasses();

  const footerLinks = {
    product: [
      { label: 'Document Parser', path: '/app/document-parser' },
      { label: 'Document Generator', path: '/app/document-generator' },
      { label: 'Trade Blotter', path: '/app/trade-blotter' },
      { label: 'GreenLens', path: '/app/green-lens' },
    ],
    resources: [
      { label: 'Documentation', href: 'https://tonic-ai.mintlify.app', external: true },
      { label: 'API Reference', href: 'https://tonic-ai.mintlify.app/api-reference', external: true },
      { label: 'GitHub', href: 'https://github.com/josephrp/creditnexus', external: true },
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
      { label: 'License', path: '/licence' },
      { label: 'RAIL', path: '/rail' },
    ],
  };

  const socialLinks = [
    { icon: Github, href: 'https://github.com/josephrp/creditnexus', label: 'GitHub' },
    { icon: Linkedin, href: 'https://linkedin.com/company/creditnexus', label: 'LinkedIn' },
    { icon: Mail, href: 'mailto:contact@creditnexus.com', label: 'Email' },
  ];

  return (
    <footer className={`${classes.background.primary} border-t ${classes.border.light} ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8">
          {/* Brand Section */}
          <div className="lg:col-span-2">
            <h3 className={`text-xl font-bold ${classes.text.white} mb-4`}>CreditNexus</h3>
            <p className={`${classes.text.secondary} text-sm mb-4 max-w-md`}>
              Price & create structured financial products
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
                    className={`w-10 h-10 rounded-lg ${classes.background.secondary} ${classes.interactive.hover.background} flex items-center justify-center ${classes.text.secondary} hover:text-emerald-400 transition-colors`}
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
            <h4 className={`text-sm font-semibold ${classes.text.white} mb-4 uppercase tracking-wider`}>Product</h4>
            <ul className="space-y-2">
              {footerLinks.product.map((link) => (
                <li key={link.label}>
                  <Link
                    to={link.path}
                    className={`text-sm ${classes.text.secondary} hover:text-emerald-400 transition-colors`}
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources Links */}
          <div>
            <h4 className={`text-sm font-semibold ${classes.text.white} mb-4 uppercase tracking-wider`}>Resources</h4>
            <ul className="space-y-2">
              {footerLinks.resources.map((link) => (
                <li key={link.label}>
                  {link.external ? (
                    <a
                      href={link.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={`text-sm ${classes.text.secondary} hover:text-emerald-400 transition-colors flex items-center gap-1`}
                    >
                      {link.label}
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  ) : (
                    <Link
                      to={link.href}
                      className={`text-sm ${classes.text.secondary} hover:text-emerald-400 transition-colors`}
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
            <h4 className={`text-sm font-semibold ${classes.text.white} mb-4 uppercase tracking-wider`}>Company</h4>
            <ul className="space-y-2">
              {footerLinks.company.map((link) => (
                <li key={link.label}>
                  <Link
                    to={link.path}
                    className={`text-sm ${classes.text.secondary} hover:text-emerald-400 transition-colors`}
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className={`mt-8 pt-8 border-t ${classes.border.light}`}>
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className={`text-sm ${classes.text.muted}`}>
              © {currentYear} CreditNexus. All rights reserved.
            </p>
            <div className="flex items-center gap-6">
              {footerLinks.legal.map((link) => (
                <Link
                  key={link.label}
                  to={link.path}
                  className={`text-sm ${classes.text.muted} ${classes.interactive.hover.text} transition-colors`}
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
