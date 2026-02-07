import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Eye, EyeOff, Mail, Lock, User, Phone } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const LoginModal = ({ isOpen, onClose }) => {
  const { login, register, loading } = useAuth();
  const [activeTab, setActiveTab] = useState('login');
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    phone: ''
  });

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    const result = await login({
      email: formData.email,
      password: formData.password
    });
    
    if (result.success) {
      onClose();
      setFormData({ email: '', password: '', name: '', phone: '' });
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    const result = await register({
      email: formData.email,
      password: formData.password,
      name: formData.name,
      phone: formData.phone
    });
    
    if (result.success) {
      onClose();
      setFormData({ email: '', password: '', name: '', phone: '' });
    }
  };

  const handleQuickLogin = async (email, password) => {
    const result = await login({ email, password });
    if (result.success) {
      onClose();
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-[#1a2f4b]">
            Access Your Account
          </DialogTitle>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="login">Sign In</TabsTrigger>
            <TabsTrigger value="register">Create Account</TabsTrigger>
          </TabsList>

          {/* Login Tab */}
          <TabsContent value="login" className="space-y-4">
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email Address</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    placeholder="Enter your email"
                    className="pl-10"
                    value={formData.email}
                    onChange={handleInputChange}
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter your password"
                    className="pl-10 pr-10"
                    value={formData.password}
                    onChange={handleInputChange}
                    required
                  />
                  <button
                    type="button"
                    className="absolute right-3 top-3 h-4 w-4 text-gray-400 hover:text-gray-600"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <Button 
                type="submit" 
                className="w-full bg-[#1a2f4b] hover:bg-[#2d5aa0]"
                disabled={loading}
              >
                {loading ? 'Signing In...' : 'Sign In'}
              </Button>
            </form>

            {/* Quick Login Options */}
            <div className="space-y-2">
              <p className="text-sm text-gray-600 text-center">Demo accounts (click to test):</p>
              <div className="space-y-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full text-left justify-start"
                  onClick={() => handleQuickLogin('demo@paymentus.com', 'demo123')}
                  disabled={loading}
                >
                  <User className="w-4 h-4 mr-2" />
                  Demo User (demo@paymentus.com)
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full text-left justify-start"
                  onClick={() => handleQuickLogin('test@paymentus.com', 'test123')}
                  disabled={loading}
                >
                  <User className="w-4 h-4 mr-2" />
                  Test User (test@paymentus.com)
                </Button>
              </div>
            </div>

            <div className="text-center">
              <button 
                type="button" 
                className="text-sm text-[#4285f4] hover:underline"
              >
                Forgot your password?
              </button>
            </div>
          </TabsContent>

          {/* Register Tab */}
          <TabsContent value="register" className="space-y-4">
            <form onSubmit={handleRegister} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="register-name">Full Name</Label>
                <div className="relative">
                  <User className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="register-name"
                    name="name"
                    type="text"
                    placeholder="Enter your full name"
                    className="pl-10"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="register-email">Email Address</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="register-email"
                    name="email"
                    type="email"
                    placeholder="Enter your email"
                    className="pl-10"
                    value={formData.email}
                    onChange={handleInputChange}
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="register-phone">Phone Number</Label>
                <div className="relative">
                  <Phone className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="register-phone"
                    name="phone"
                    type="tel"
                    placeholder="Enter your phone number"
                    className="pl-10"
                    value={formData.phone}
                    onChange={handleInputChange}
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="register-password">Password</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="register-password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Create a password"
                    className="pl-10 pr-10"
                    value={formData.password}
                    onChange={handleInputChange}
                    required
                  />
                  <button
                    type="button"
                    className="absolute right-3 top-3 h-4 w-4 text-gray-400 hover:text-gray-600"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <Button 
                type="submit" 
                className="w-full bg-[#4285f4] hover:bg-[#3367d6]"
                disabled={loading}
              >
                {loading ? 'Creating Account...' : 'Create Account'}
              </Button>
            </form>

            <div className="text-center text-sm text-gray-600">
              By creating an account, you agree to our Terms of Service and Privacy Policy.
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};

export default LoginModal;