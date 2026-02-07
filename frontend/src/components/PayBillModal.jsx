import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { 
  Search, 
  CreditCard, 
  Building, 
  Zap, 
  Wifi, 
  Phone,
  Car,
  Home,
  DollarSign,
  Calendar
} from 'lucide-react';

const PayBillModal = ({ isOpen, onClose, user }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedBiller, setSelectedBiller] = useState(null);
  const [paymentAmount, setPaymentAmount] = useState('');
  const [selectedPaymentMethod, setSelectedPaymentMethod] = useState('');
  const [accountNumber, setAccountNumber] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  const billerCategories = [
    {
      name: 'Utilities',
      icon: <Zap className="w-5 h-5" />,
      billers: [
        { name: 'Duke Energy', type: 'Electric', color: 'bg-yellow-500' },
        { name: 'Charlotte Water', type: 'Water & Sewer', color: 'bg-blue-500' },
        { name: 'Piedmont Natural Gas', type: 'Gas', color: 'bg-orange-500' },
        { name: 'Union Power Cooperative', type: 'Electric', color: 'bg-green-500' }
      ]
    },
    {
      name: 'Telecommunications',
      icon: <Wifi className="w-5 h-5" />,
      billers: [
        { name: 'Spectrum', type: 'Internet & TV', color: 'bg-red-500' },
        { name: 'AT&T', type: 'Phone & Internet', color: 'bg-blue-600' },
        { name: 'Verizon', type: 'Wireless', color: 'bg-red-600' },
        { name: 'T-Mobile', type: 'Wireless', color: 'bg-pink-500' }
      ]
    },
    {
      name: 'Insurance',
      icon: <Car className="w-5 h-5" />,
      billers: [
        { name: 'State Farm', type: 'Auto & Home', color: 'bg-red-700' },
        { name: 'Geico', type: 'Auto Insurance', color: 'bg-green-600' },
        { name: 'Allstate', type: 'Insurance', color: 'bg-blue-700' },
        { name: 'Progressive', type: 'Auto Insurance', color: 'bg-purple-600' }
      ]
    },
    {
      name: 'Government',
      icon: <Building className="w-5 h-5" />,
      billers: [
        { name: 'City of Charlotte', type: 'Municipal', color: 'bg-indigo-600' },
        { name: 'Mecklenburg County', type: 'County Services', color: 'bg-gray-600' },
        { name: 'NC Department of Revenue', type: 'State Taxes', color: 'bg-green-700' },
        { name: 'Charlotte Parking', type: 'Parking Citations', color: 'bg-orange-600' }
      ]
    }
  ];

  const paymentMethods = [
    { id: 'cc_1234', type: 'Credit Card', name: 'Visa ****1234', icon: <CreditCard className="w-4 h-4" /> },
    { id: 'bank_5678', type: 'Bank Account', name: 'Bank of America ****5678', icon: <Building className="w-4 h-4" /> },
    { id: 'paypal', type: 'Digital Wallet', name: 'PayPal Account', icon: <DollarSign className="w-4 h-4" /> }
  ];

  const handleProcessPayment = () => {
    if (!selectedBiller || !paymentAmount || !selectedPaymentMethod || !accountNumber) {
      alert('Please fill in all required fields');
      return;
    }

    setIsProcessing(true);
    
    // Mock payment processing
    setTimeout(() => {
      alert(`Payment of $${paymentAmount} to ${selectedBiller.name} has been processed successfully!
      
Confirmation Number: PAY${Date.now()}
Account: ****${accountNumber.slice(-4)}
Amount: $${paymentAmount}
Method: ${paymentMethods.find(m => m.id === selectedPaymentMethod)?.name}`);
      
      setIsProcessing(false);
      onClose();
      
      // Reset form
      setSelectedBiller(null);
      setPaymentAmount('');
      setSelectedPaymentMethod('');
      setAccountNumber('');
    }, 2000);
  };

  const filteredBillers = billerCategories.map(category => ({
    ...category,
    billers: category.billers.filter(biller => 
      biller.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      biller.type.toLowerCase().includes(searchTerm.toLowerCase())
    )
  })).filter(category => category.billers.length > 0);

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-[#1a2f4b]">
            Pay Your Bills
          </DialogTitle>
        </DialogHeader>

        {!user ? (
          <div className="text-center py-8">
            <p className="text-gray-600 mb-4">Please sign in to access bill pay services.</p>
            <Button onClick={onClose} className="bg-[#1a2f4b] hover:bg-[#2d5aa0]">
              Sign In Required
            </Button>
          </div>
        ) : (
          <Tabs defaultValue="select-biller" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="select-biller">1. Select Biller</TabsTrigger>
              <TabsTrigger value="enter-details" disabled={!selectedBiller}>2. Enter Details</TabsTrigger>
              <TabsTrigger value="confirm-payment" disabled={!selectedBiller || !paymentAmount}>3. Confirm Payment</TabsTrigger>
            </TabsList>

            {/* Step 1: Select Biller */}
            <TabsContent value="select-biller" className="space-y-6">
              <div className="space-y-4">
                <div className="relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search for your biller..."
                    className="pl-10"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>

                <div className="space-y-6">
                  {filteredBillers.map((category) => (
                    <div key={category.name}>
                      <div className="flex items-center space-x-2 mb-4">
                        {category.icon}
                        <h3 className="text-lg font-semibold text-gray-800">{category.name}</h3>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {category.billers.map((biller) => (
                          <Card 
                            key={biller.name} 
                            className={`cursor-pointer hover:shadow-md transition-all ${
                              selectedBiller?.name === biller.name ? 'ring-2 ring-blue-500 bg-blue-50' : ''
                            }`}
                            onClick={() => setSelectedBiller(biller)}
                          >
                            <CardContent className="p-4">
                              <div className="flex items-center space-x-3">
                                <div className={`w-12 h-12 ${biller.color} rounded-lg flex items-center justify-center text-white font-bold text-lg`}>
                                  {biller.name.charAt(0)}
                                </div>
                                <div>
                                  <h4 className="font-semibold text-gray-800">{biller.name}</h4>
                                  <p className="text-sm text-gray-600">{biller.type}</p>
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>

                {selectedBiller && (
                  <div className="flex justify-end">
                    <Button onClick={() => document.querySelector('[value="enter-details"]').click()}>
                      Continue with {selectedBiller.name}
                    </Button>
                  </div>
                )}
              </div>
            </TabsContent>

            {/* Step 2: Enter Details */}
            <TabsContent value="enter-details" className="space-y-6">
              {selectedBiller && (
                <Card className="bg-blue-50 border-blue-200">
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-3">
                      <div className={`w-12 h-12 ${selectedBiller.color} rounded-lg flex items-center justify-center text-white font-bold text-lg`}>
                        {selectedBiller.name.charAt(0)}
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-800">{selectedBiller.name}</h4>
                        <p className="text-sm text-gray-600">{selectedBiller.type}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="account-number">Account Number</Label>
                    <Input
                      id="account-number"
                      placeholder="Enter your account number"
                      value={accountNumber}
                      onChange={(e) => setAccountNumber(e.target.value)}
                      required
                    />
                  </div>

                  <div>
                    <Label htmlFor="payment-amount">Payment Amount</Label>
                    <div className="relative">
                      <DollarSign className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        id="payment-amount"
                        type="number"
                        step="0.01"
                        placeholder="0.00"
                        className="pl-10"
                        value={paymentAmount}
                        onChange={(e) => setPaymentAmount(e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <Label>Payment Date</Label>
                    <Select defaultValue="today">
                      <SelectTrigger>
                        <SelectValue placeholder="Select payment date" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="today">Today</SelectItem>
                        <SelectItem value="tomorrow">Tomorrow</SelectItem>
                        <SelectItem value="custom">Choose Date...</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-4">
                  <Label>Select Payment Method</Label>
                  <div className="space-y-3">
                    {paymentMethods.map((method) => (
                      <Card 
                        key={method.id}
                        className={`cursor-pointer hover:shadow-md transition-all ${
                          selectedPaymentMethod === method.id ? 'ring-2 ring-blue-500 bg-blue-50' : ''
                        }`}
                        onClick={() => setSelectedPaymentMethod(method.id)}
                      >
                        <CardContent className="p-4">
                          <div className="flex items-center space-x-3">
                            {method.icon}
                            <div>
                              <h4 className="font-medium text-gray-800">{method.name}</h4>
                              <p className="text-sm text-gray-600">{method.type}</p>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              </div>

              {paymentAmount && selectedPaymentMethod && accountNumber && (
                <div className="flex justify-end">
                  <Button onClick={() => document.querySelector('[value="confirm-payment"]').click()}>
                    Review Payment
                  </Button>
                </div>
              )}
            </TabsContent>

            {/* Step 3: Confirm Payment */}
            <TabsContent value="confirm-payment" className="space-y-6">
              <Card>
                <CardContent className="p-6">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Payment Summary</h3>
                  
                  <div className="space-y-4">
                    <div className="flex justify-between items-center py-2 border-b">
                      <span className="text-gray-600">Biller</span>
                      <span className="font-medium">{selectedBiller?.name}</span>
                    </div>
                    
                    <div className="flex justify-between items-center py-2 border-b">
                      <span className="text-gray-600">Account Number</span>
                      <span className="font-medium font-mono">****{accountNumber.slice(-4)}</span>
                    </div>
                    
                    <div className="flex justify-between items-center py-2 border-b">
                      <span className="text-gray-600">Payment Method</span>
                      <span className="font-medium">
                        {paymentMethods.find(m => m.id === selectedPaymentMethod)?.name}
                      </span>
                    </div>
                    
                    <div className="flex justify-between items-center py-2 border-b">
                      <span className="text-gray-600">Payment Date</span>
                      <span className="font-medium">Today</span>
                    </div>
                    
                    <div className="flex justify-between items-center py-2 text-lg">
                      <span className="font-semibold text-gray-800">Total Amount</span>
                      <span className="font-bold text-2xl text-[#1a2f4b]">${paymentAmount}</span>
                    </div>
                  </div>

                  <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <p className="text-sm text-yellow-800">
                      ⚠️ Please review your payment details carefully. This transaction cannot be undone once processed.
                    </p>
                  </div>

                  <div className="flex space-x-4 mt-6">
                    <Button 
                      variant="outline" 
                      onClick={() => document.querySelector('[value="enter-details"]').click()}
                      className="flex-1"
                    >
                      Back to Edit
                    </Button>
                    <Button 
                      onClick={handleProcessPayment}
                      disabled={isProcessing}
                      className="flex-1 bg-[#1a2f4b] hover:bg-[#2d5aa0]"
                    >
                      {isProcessing ? 'Processing...' : 'Process Payment'}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default PayBillModal;