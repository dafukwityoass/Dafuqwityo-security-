import React from 'react';
import { Button } from './ui/button';
import { quickLinksData, footerLinks } from '../data/mockData';

const Footer = ({ onContactClick, onSupportClick }) => {
  return (
    <footer className="bg-[#1a2f4b] text-white">
      {/* Quick Links Section */}
      <div className="bg-gradient-to-r from-[#1a2f4b] to-[#2d5aa0] py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">Helpful Quick Links</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {quickLinksData.map((link, index) => (
              <div key={index} className="text-center">
                <h3 className="text-xl font-semibold mb-4">{link.title}</h3>
                <p className="text-blue-100 mb-6 leading-relaxed">
                  {link.description}
                </p>
                <Button 
                  variant="outline"
                  className="border-white text-white hover:bg-white hover:text-[#1a2f4b]"
                  onClick={() => {
                    if (link.title.includes('Partner')) onContactClick();
                    else if (link.title.includes('Team')) console.log('Careers clicked');
                    else console.log('FAQ clicked');
                  }}
                >
                  {link.ctaText}
                </Button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Footer */}
      <div className="py-12">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-3 gap-8 lg:gap-12">
            {/* Company Info */}
            <div>
              <h3 className="text-2xl font-bold mb-6">Paymentus</h3>
              <div className="space-y-3">
                {footerLinks.company.map((link) => (
                  <div key={link.name}>
                    <a 
                      href={link.href}
                      className="text-blue-200 hover:text-white transition-colors"
                    >
                      {link.name}
                    </a>
                  </div>
                ))}
              </div>
            </div>

            {/* Legal Links */}
            <div>
              <h4 className="text-lg font-semibold mb-6">Legal & Privacy</h4>
              <div className="space-y-3">
                {footerLinks.legal.map((link) => (
                  <div key={link.name}>
                    <a 
                      href={link.href}
                      className="text-blue-200 hover:text-white transition-colors"
                    >
                      {link.name}
                    </a>
                  </div>
                ))}
              </div>
            </div>

            {/* Contact Actions */}
            <div>
              <h4 className="text-lg font-semibold mb-6">Get In Touch</h4>
              <div className="space-y-4">
                <Button 
                  className="w-full bg-[#4285f4] hover:bg-[#3367d6] text-white"
                  onClick={onContactClick}
                >
                  LET'S TALK
                </Button>
                <Button 
                  variant="outline" 
                  className="w-full border-white text-white hover:bg-white hover:text-[#1a2f4b]"
                >
                  PAY YOUR BILL
                </Button>
                <Button 
                  className="w-full bg-[#e91e63] hover:bg-[#d81b60] text-white"
                  onClick={onSupportClick}
                >
                  CUSTOMER SUPPORT
                </Button>
              </div>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="border-t border-blue-700 mt-12 pt-8 text-center">
            <p className="text-blue-200">
              © 2024 Paymentus Holdings Inc. All rights reserved.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;