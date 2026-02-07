import React, { useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Header from "./components/Header";
import HeroSection from "./components/HeroSection";
import ServicesSection from "./components/ServicesSection";
import Footer from "./components/Footer";
import PaymentDashboard from "./components/PaymentDashboard";
import LoginModal from "./components/LoginModal";
import PayBillModal from "./components/PayBillModal";
import { Toaster } from "./components/ui/toaster";
import { AuthProvider, useAuth } from "./contexts/AuthContext";

const LandingPage = ({ 
  onLoginClick, 
  onPayBillClick, 
  onGetStartedClick, 
  onTalkClick,
  onContactClick,
  onSupportClick 
}) => {
  return (
    <>
      <Header 
        onLoginClick={onLoginClick}
        onPayBillClick={onPayBillClick}
        onTalkClick={onTalkClick}
      />
      <HeroSection onGetStartedClick={onGetStartedClick} />
      <ServicesSection />
      <Footer 
        onContactClick={onContactClick}
        onSupportClick={onSupportClick}
      />
    </>
  );
};

const AppContent = () => {
  const { user, isAuthenticated } = useAuth();
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [isPayBillModalOpen, setIsPayBillModalOpen] = useState(false);
  const [currentView, setCurrentView] = useState('landing'); // 'landing' or 'dashboard'

  // Update view based on authentication status
  React.useEffect(() => {
    if (isAuthenticated) {
      setCurrentView('dashboard');
    } else {
      setCurrentView('landing');
    }
  }, [isAuthenticated]);

  const handleGetStarted = () => {
    if (isAuthenticated) {
      setCurrentView('dashboard');
    } else {
      setIsLoginModalOpen(true);
    }
  };

  const handlePayBillClick = () => {
    setIsPayBillModalOpen(true);
  };

  const handleTalkClick = () => {
    // Mock contact form or redirect
    alert('Thanks for your interest! Our sales team will contact you soon.');
  };

  const handleContactClick = () => {
    alert('Contact form would open here. For demo purposes, please use the dashboard features.');
  };

  const handleSupportClick = () => {
    alert('Customer support chat would open here. For demo purposes, please explore the dashboard.');
  };

  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route 
            path="/" 
            element={
              currentView === 'landing' ? (
                <LandingPage
                  onLoginClick={() => setIsLoginModalOpen(true)}
                  onPayBillClick={handlePayBillClick}
                  onGetStartedClick={handleGetStarted}
                  onTalkClick={handleTalkClick}
                  onContactClick={handleContactClick}
                  onSupportClick={handleSupportClick}
                />
              ) : (
                <PaymentDashboard 
                  user={user} 
                />
              )
            } 
          />
        </Routes>
      </BrowserRouter>

      {/* Modals */}
      <LoginModal
        isOpen={isLoginModalOpen}
        onClose={() => setIsLoginModalOpen(false)}
      />

      <PayBillModal
        isOpen={isPayBillModalOpen}
        onClose={() => setIsPayBillModalOpen(false)}
      />

      <Toaster />
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;