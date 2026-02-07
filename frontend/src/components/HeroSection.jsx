import React from 'react';
import { Button } from './ui/button';
import { heroContent } from '../data/mockData';

const HeroSection = ({ onGetStartedClick }) => {
  return (
    <section className="relative min-h-screen pt-16 overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#0066cc] via-[#1a2f4b] to-[#2d5aa0]" />
      
      {/* Network pattern overlay */}
      <div className="absolute inset-0 opacity-30">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZGVmcz48cGF0dGVybiBpZD0iZ3JpZCIgd2lkdGg9IjQwIiBoZWlnaHQ9IjQwIiBwYXR0ZXJuVW5pdHM9InVzZXJTcGFjZU9uVXNlIj48cGF0aCBkPSJNIDQwIDAgTCAwIDAgMCA0MCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJyZ2JhKDI1NSwgMjU1LCAyNTUsIDAuMSkiIHN0cm9rZS13aWR0aD0iMSIvPjwvcGF0dGVybj48L2RlZnM+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0idXJsKCNncmlkKSIvPjwvc3ZnPg==')] bg-repeat" />
      </div>

      {/* Floating network nodes */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 right-1/4 w-2 h-2 bg-blue-300 rounded-full animate-pulse" />
        <div className="absolute top-1/3 right-1/3 w-1.5 h-1.5 bg-blue-400 rounded-full animate-pulse delay-1000" />
        <div className="absolute bottom-1/3 right-1/5 w-2.5 h-2.5 bg-blue-200 rounded-full animate-pulse delay-2000" />
        <div className="absolute top-2/3 right-2/3 w-1 h-1 bg-blue-500 rounded-full animate-pulse delay-500" />
        
        {/* Connection lines */}
        <svg className="absolute inset-0 w-full h-full">
          <line x1="75%" y1="25%" x2="66%" y2="33%" stroke="rgba(147, 197, 253, 0.3)" strokeWidth="1" />
          <line x1="66%" y1="33%" x2="80%" y2="66%" stroke="rgba(147, 197, 253, 0.3)" strokeWidth="1" />
          <line x1="80%" y1="66%" x2="33%" y2="66%" stroke="rgba(147, 197, 253, 0.3)" strokeWidth="1" />
        </svg>
      </div>

      <div className="relative z-10 container mx-auto px-4 h-full flex items-center">
        <div className="max-w-2xl">
          <h1 className="text-5xl md:text-6xl font-bold text-white leading-tight mb-6">
            <span className="text-cyan-300">Intelligent</span>
            <br />
            <span className="text-cyan-300">Simplified</span> Payments.
          </h1>
          
          <div className="mb-8">
            <p className="text-xl text-cyan-300 font-medium mb-4">
              {heroContent.subtitle}
            </p>
            <p className="text-lg text-blue-100 leading-relaxed max-w-xl">
              {heroContent.description}
            </p>
          </div>

          <Button 
            size="lg"
            className="bg-white text-[#1a2f4b] hover:bg-gray-100 font-semibold px-8 py-3 text-lg"
            onClick={onGetStartedClick}
          >
            {heroContent.ctaText}
          </Button>
        </div>
      </div>

      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
        <div className="w-6 h-10 border-2 border-white rounded-full flex justify-center">
          <div className="w-1 h-3 bg-white rounded-full mt-2" />
        </div>
      </div>
    </section>
  );
};

export default HeroSection;