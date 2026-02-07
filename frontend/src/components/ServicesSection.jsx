import React from 'react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { servicesData, statsData } from '../data/mockData';
import { Shield, Zap, Users, TrendingUp, CreditCard, Smartphone } from 'lucide-react';

const ServicesSection = () => {
  return (
    <section className="py-20 bg-gray-50">
      <div className="container mx-auto px-4">
        {/* Stats Section */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-20">
          {statsData.map((stat, index) => (
            <div key={index} className="text-center">
              <div className="text-3xl md:text-4xl font-bold text-[#1a2f4b] mb-2">
                {stat.number}
              </div>
              <div className="text-gray-600">{stat.label}</div>
            </div>
          ))}
        </div>

        {/* First Service Block */}
        <div className="grid lg:grid-cols-2 gap-12 items-center mb-20">
          <div>
            <h2 className="text-4xl font-bold text-[#1a2f4b] mb-6">
              More Secure Way to Pay Bills
            </h2>
            <p className="text-lg text-gray-700 mb-8 leading-relaxed">
              Paymentus' AI-powered, <span className="font-semibold">patented</span> bill pay assistant and omnichannel 
              wallet are fundamentally simplifying how bills are presented, 
              understood, and paid. See how it delivers 4x faster payments.
            </p>
            <Button 
              size="lg"
              className="bg-[#4285f4] hover:bg-[#3367d6] text-white px-8 py-3"
            >
              START NOW
            </Button>
          </div>
          <div className="relative">
            {/* Mock dashboard/interface */}
            <div className="bg-white rounded-lg shadow-xl p-6 border">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                    <CreditCard className="w-4 h-4 text-white" />
                  </div>
                  <span className="font-medium text-gray-800">Payment Assistant</span>
                </div>
                <div className="text-sm text-gray-500">AI-Powered</div>
              </div>
              
              <div className="space-y-3">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="text-sm text-blue-800 mb-1">Why is my bill higher this month?</div>
                  <div className="text-xs text-blue-600">📊 I can quickly summarize what changed since last month.</div>
                </div>
                
                <div className="bg-green-50 p-4 rounded-lg">
                  <div className="text-sm text-green-800">Would you like me to provide that?</div>
                  <div className="flex space-x-2 mt-2">
                    <button className="bg-green-500 text-white text-xs px-3 py-1 rounded">YES</button>
                    <button className="bg-gray-300 text-gray-700 text-xs px-3 py-1 rounded">NO</button>
                    <button className="bg-blue-500 text-white text-xs px-3 py-1 rounded">PAY</button>
                  </div>
                </div>
                
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="text-sm font-medium text-gray-800">$254.04 Payment Processed</div>
                  <div className="text-xs text-gray-500">⚡ Payment verified confirmed via text/email notification</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Features Grid */}
        <div className="mb-20">
          <h3 className="text-2xl font-bold text-[#1a2f4b] mb-8 text-center">
            Trusted by Industry Leaders
          </h3>
          <div className="grid md:grid-cols-3 gap-8">
            <Card className="p-6 text-center hover:shadow-lg transition-shadow">
              <CardContent className="pt-4">
                <Shield className="w-12 h-12 text-blue-500 mx-auto mb-4" />
                <h4 className="font-semibold text-gray-800 mb-2">PCI Level 1 Compliant</h4>
                <p className="text-gray-600 text-sm">Bank-grade security for all transactions</p>
              </CardContent>
            </Card>
            
            <Card className="p-6 text-center hover:shadow-lg transition-shadow">
              <CardContent className="pt-4">
                <Zap className="w-12 h-12 text-blue-500 mx-auto mb-4" />
                <h4 className="font-semibold text-gray-800 mb-2">Real-time Processing</h4>
                <p className="text-gray-600 text-sm">Instant payment confirmation and receipts</p>
              </CardContent>
            </Card>
            
            <Card className="p-6 text-center hover:shadow-lg transition-shadow">
              <CardContent className="pt-4">
                <Smartphone className="w-12 h-12 text-blue-500 mx-auto mb-4" />
                <h4 className="font-semibold text-gray-800 mb-2">Omnichannel Experience</h4>
                <p className="text-gray-600 text-sm">Web, mobile, IVR, and in-person payments</p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Second Service Block */}
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div className="order-2 lg:order-1">
            {/* Mock billing dashboard */}
            <div className="bg-white rounded-lg shadow-xl p-6 border">
              <div className="flex items-center space-x-4 mb-6">
                <img 
                  src="https://images.unsplash.com/photo-1494790108755-2616b612b786?w=60&h=60&fit=crop&crop=face" 
                  alt="User" 
                  className="w-12 h-12 rounded-full"
                />
                <div className="bg-white rounded-lg shadow-sm p-4 flex-1">
                  <div className="text-2xl font-bold text-gray-800">$311.09</div>
                  <div className="text-sm text-gray-500">Current Balance</div>
                </div>
              </div>
              
              <div className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                  <span className="text-sm font-medium">Electricity</span>
                  <span className="text-sm text-blue-600">$127.45</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                  <span className="text-sm font-medium">Water</span>
                  <span className="text-sm text-green-600">$89.32</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
                  <span className="text-sm font-medium">Internet</span>
                  <span className="text-sm text-purple-600">$74.99</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="order-1 lg:order-2">
            <div className="text-sm text-blue-600 font-medium mb-4">BILLING & PAYMENTS</div>
            <h2 className="text-4xl font-bold text-[#1a2f4b] mb-6">
              Intuitive Interactions, Bill Delivery & Payments for Billers
            </h2>
            <p className="text-lg text-gray-700 mb-8 leading-relaxed">
              Transform how your customers experience billing and payments with our intelligent platform. 
              Streamlined workflows, automated notifications, and seamless integrations.
            </p>
            <div className="flex space-x-4">
              <Button 
                size="lg"
                className="bg-[#4285f4] hover:bg-[#3367d6] text-white px-8 py-3"
              >
                Learn More
              </Button>
              <Button 
                variant="outline"
                size="lg"
                className="border-[#4285f4] text-[#4285f4] hover:bg-[#4285f4] hover:text-white px-8 py-3"
              >
                View Demo
              </Button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ServicesSection;