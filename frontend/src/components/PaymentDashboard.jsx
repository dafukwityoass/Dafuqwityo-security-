import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { 
  CreditCard, 
  Calendar, 
  DollarSign, 
  TrendingUp, 
  Bell, 
  Plus,
  Eye,
  Download,
  Filter,
  Loader2
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { billsAPI, paymentsAPI, paymentMethodsAPI, dashboardAPI } from '../services/api';
import { useToast } from '../hooks/use-toast';

const PaymentDashboard = ({ user }) => {
  const { logout } = useAuth();
  const { toast } = useToast();
  const [selectedBill, setSelectedBill] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [bills, setBills] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [paymentMethods, setPaymentMethods] = useState([]);
  const [dashboardMetrics, setDashboardMetrics] = useState({
    total_due: 0,
    next_due_date: null,
    monthly_total: 0,
    method_count: 0,
    recent_transactions: []
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [billsData, transactionsData, methodsData, metricsData] = await Promise.all([
        billsAPI.getBills(),
        paymentsAPI.getPaymentHistory(),
        paymentMethodsAPI.getPaymentMethods(),
        dashboardAPI.getMetrics()
      ]);
      
      setBills(billsData);
      setTransactions(transactionsData);
      setPaymentMethods(methodsData);
      setDashboardMetrics(metricsData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      toast({
        title: "Error",
        description: "Failed to load dashboard data. Please refresh the page.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const totalDue = dashboardMetrics.total_due;

  const formatCurrency = (amount) => `$${amount.toFixed(2)}`;
  const formatDate = (dateStr) => new Date(dateStr).toLocaleDateString();

  const getStatusColor = (status) => {
    switch (status) {
      case 'paid': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'overdue': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handlePayBill = async (bill) => {
    try {
      if (paymentMethods.length === 0) {
        toast({
          title: "No Payment Method",
          description: "Please add a payment method first.",
          variant: "destructive",
        });
        return;
      }

      const defaultMethod = paymentMethods.find(pm => pm.is_default) || paymentMethods[0];
      
      const transaction = await paymentsAPI.processPayment({
        bill_id: bill.id,
        payment_method_id: defaultMethod.id,
        amount: bill.amount
      });
      
      toast({
        title: "Payment Successful",
        description: `Payment of ${formatCurrency(bill.amount)} for ${bill.biller_name} has been processed successfully!`,
      });
      
      // Refresh data
      await loadDashboardData();
    } catch (error) {
      console.error('Payment processing error:', error);
      toast({
        title: "Payment Failed",
        description: "Unable to process payment. Please try again.",
        variant: "destructive",
      });
    }
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Dashboard Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-[#1a2f4b]">Payment Dashboard</h1>
              <p className="text-gray-600">Welcome back, {user?.name}</p>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="outline" size="sm">
                <Bell className="w-4 h-4 mr-2" />
                Notifications
              </Button>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                Sign Out
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid grid-cols-4 w-full max-w-2xl">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="bills">Bills</TabsTrigger>
            <TabsTrigger value="history">History</TabsTrigger>
            <TabsTrigger value="methods">Payment Methods</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            {/* Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
                    <DollarSign className="w-4 h-4 mr-2" />
                    Total Due
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-red-600">{formatCurrency(totalDue)}</div>
                  <p className="text-xs text-gray-500 mt-1">{bills.filter(b => b.status === 'pending').length} pending bills</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
                    <Calendar className="w-4 h-4 mr-2" />
                    Next Due
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-[#1a2f4b]">
                    {dashboardMetrics.next_due_date ? formatDate(dashboardMetrics.next_due_date) : 'No bills due'}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Next payment due</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
                    <TrendingUp className="w-4 h-4 mr-2" />
                    This Month
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-600">
                    {formatCurrency(dashboardMetrics.monthly_total)}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">{transactions.length} payments made</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600 flex items-center">
                    <CreditCard className="w-4 h-4 mr-2" />
                    Saved Methods
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-[#1a2f4b]">{dashboardMetrics.method_count}</div>
                  <p className="text-xs text-gray-500 mt-1">Active payment methods</p>
                </CardContent>
              </Card>
            </div>

            {/* Recent Bills */}
            <Card>
              <CardHeader>
                <CardTitle>Upcoming Bills</CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="flex justify-center items-center py-8">
                    <Loader2 className="w-8 h-8 animate-spin" />
                  </div>
                ) : (
                  <div className="space-y-4">
                    {bills.filter(bill => bill.status === 'pending').slice(0, 3).map((bill) => (
                      <div key={bill.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center space-x-4">
                          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                            <CreditCard className="w-6 h-6 text-blue-600" />
                          </div>
                          <div>
                            <h4 className="font-medium text-gray-800">{bill.biller_name}</h4>
                            <p className="text-sm text-gray-600">{bill.description}</p>
                            <p className="text-xs text-gray-500">Due: {formatDate(bill.due_date)}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-lg font-semibold text-gray-800">{formatCurrency(bill.amount)}</div>
                          <Button size="sm" className="mt-2" onClick={() => handlePayBill(bill)}>
                            Pay Now
                          </Button>
                        </div>
                      </div>
                    ))}
                    {bills.filter(bill => bill.status === 'pending').length === 0 && (
                      <div className="text-center py-8 text-gray-500">
                        No pending bills found
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Bills Tab */}
          <TabsContent value="bills" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-[#1a2f4b]">All Bills</h2>
              <div className="flex space-x-2">
                <Button variant="outline" size="sm">
                  <Filter className="w-4 h-4 mr-2" />
                  Filter
                </Button>
                <Button size="sm">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Biller
                </Button>
              </div>
            </div>

            <div className="grid gap-4">
              {loading ? (
                <div className="flex justify-center items-center py-8">
                  <Loader2 className="w-8 h-8 animate-spin" />
                </div>
              ) : (
                bills.map((bill) => (
                  <Card key={bill.id} className="hover:shadow-md transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold text-lg">
                            {bill.biller_name.charAt(0)}
                          </div>
                          <div>
                            <h3 className="text-lg font-semibold text-gray-800">{bill.biller_name}</h3>
                            <p className="text-gray-600">{bill.description}</p>
                            <p className="text-sm text-gray-500">Account: {bill.account_number}</p>
                            <p className="text-sm text-gray-500">Due: {formatDate(bill.due_date)}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-gray-800 mb-2">{formatCurrency(bill.amount)}</div>
                          <Badge className={getStatusColor(bill.status)}>
                            {bill.status.toUpperCase()}
                          </Badge>
                          {bill.status === 'pending' && (
                            <div className="mt-3 space-x-2">
                              <Button size="sm" onClick={() => handlePayBill(bill)}>
                                Pay Now
                              </Button>
                              <Button variant="outline" size="sm">
                                <Eye className="w-4 h-4" />
                              </Button>
                            </div>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
              {!loading && bills.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  No bills found. Add a biller to get started.
                </div>
              )}
            </div>
          </TabsContent>

          {/* History Tab */}
          <TabsContent value="history" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-[#1a2f4b]">Payment History</h2>
              <Button variant="outline" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
            </div>

            <Card>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b">
                      <tr>
                        <th className="text-left p-4 font-medium text-gray-600">Date</th>
                        <th className="text-left p-4 font-medium text-gray-600">Biller</th>
                        <th className="text-left p-4 font-medium text-gray-600">Amount</th>
                        <th className="text-left p-4 font-medium text-gray-600">Method</th>
                        <th className="text-left p-4 font-medium text-gray-600">Status</th>
                        <th className="text-left p-4 font-medium text-gray-600">Confirmation</th>
                      </tr>
                    </thead>
                    <tbody>
                      {loading ? (
                        <tr>
                          <td colSpan="6" className="p-8 text-center">
                            <Loader2 className="w-8 h-8 animate-spin mx-auto" />
                          </td>
                        </tr>
                      ) : (
                        transactions.map((txn) => {
                          const bill = bills.find(b => b.id === txn.bill_id);
                          const method = paymentMethods.find(pm => pm.id === txn.payment_method_id);
                          return (
                            <tr key={txn.id} className="border-b hover:bg-gray-50">
                              <td className="p-4 text-gray-800">{formatDate(txn.timestamp)}</td>
                              <td className="p-4 text-gray-800">{bill?.biller_name || 'Unknown'}</td>
                              <td className="p-4 font-semibold text-gray-800">{formatCurrency(txn.amount)}</td>
                              <td className="p-4 text-gray-600">
                                {method?.type === 'credit_card' ? `****${method.last4}` : 
                                 method?.type === 'bank_account' ? 'Bank Account' : 
                                 method?.type || 'Unknown'}
                              </td>
                              <td className="p-4">
                                <Badge className={getStatusColor(txn.status)}>
                                  {txn.status.toUpperCase()}
                                </Badge>
                              </td>
                              <td className="p-4 text-sm text-gray-500 font-mono">{txn.confirmation_number}</td>
                            </tr>
                          );
                        })
                      )}
                      {!loading && transactions.length === 0 && (
                        <tr>
                          <td colSpan="6" className="p-8 text-center text-gray-500">
                            No transactions found
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Payment Methods Tab */}
          <TabsContent value="methods" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-[#1a2f4b]">Payment Methods</h2>
              <Button size="sm">
                <Plus className="w-4 h-4 mr-2" />
                Add Method
              </Button>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              {loading ? (
                <div className="col-span-2 flex justify-center items-center py-8">
                  <Loader2 className="w-8 h-8 animate-spin" />
                </div>
              ) : (
                paymentMethods.map((method) => (
                  <Card key={method.id} className="hover:shadow-md transition-shadow">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                            <CreditCard className="w-6 h-6 text-white" />
                          </div>
                          <div>
                            <h3 className="font-semibold text-gray-800">
                              {method.type === 'credit_card' ? `${method.brand || 'Card'} ****${method.last4}` :
                               method.type === 'bank_account' ? `${method.bank_name || 'Bank'} ****${method.last4}` :
                               method.type === 'bitcoin' ? `Bitcoin: ${method.bitcoin_address?.slice(0, 12)}...` :
                               'Payment Method'}
                            </h3>
                            <p className="text-sm text-gray-600 capitalize">
                              {method.type.replace('_', ' ')}
                            </p>
                          </div>
                        </div>
                        {method.is_default && (
                          <Badge className="bg-green-100 text-green-800">Default</Badge>
                        )}
                      </div>
                      <div className="flex space-x-2">
                        <Button variant="outline" size="sm">Edit</Button>
                        <Button variant="outline" size="sm">Remove</Button>
                        {!method.is_default && (
                          <Button size="sm">Set as Default</Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
              {!loading && paymentMethods.length === 0 && (
                <div className="col-span-2 text-center py-8 text-gray-500">
                  No payment methods found. Add one to get started.
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default PaymentDashboard;