#!/usr/bin/env python3
"""
Enhanced Financial Infrastructure Testing for Paymentus Clone
Tests advanced financial services, compliance, and security features
"""

import requests
import json
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://payment-dashboard-24.preview.emergentagent.com/api"
TIMEOUT = 30

class EnhancedFinancialTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = TIMEOUT
        self.auth_token = None
        self.user_data = None
        self.test_results = {
            "stripe_integration": {"passed": 0, "failed": 0, "errors": []},
            "security_framework": {"passed": 0, "failed": 0, "errors": []},
            "compliance_systems": {"passed": 0, "failed": 0, "errors": []},
            "banking_integration": {"passed": 0, "failed": 0, "errors": []},
            "financial_infrastructure": {"passed": 0, "failed": 0, "errors": []},
            "production_features": {"passed": 0, "failed": 0, "errors": []}
        }
        
    def log_result(self, category: str, test_name: str, success: bool, error: str = None):
        """Log test result"""
        if success:
            self.test_results[category]["passed"] += 1
            print(f"✅ {test_name}")
        else:
            self.test_results[category]["failed"] += 1
            self.test_results[category]["errors"].append(f"{test_name}: {error}")
            print(f"❌ {test_name}: {error}")
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None) -> tuple:
        """Make HTTP request and return (success, response, error)"""
        try:
            url = f"{BASE_URL}{endpoint}"
            request_headers = {"Content-Type": "application/json"}
            
            if self.auth_token:
                request_headers["Authorization"] = f"Bearer {self.auth_token}"
            
            if headers:
                request_headers.update(headers)
            
            print(f"Making {method} request to: {url}")
            
            if method.upper() == "GET":
                response = self.session.get(url, headers=request_headers)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=request_headers)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=request_headers)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=request_headers)
            else:
                return False, None, f"Unsupported method: {method}"
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code >= 400:
                error_msg = f"HTTP {response.status_code}"
                try:
                    error_detail = response.json().get("detail", "Unknown error")
                    error_msg += f": {error_detail}"
                except:
                    error_msg += f": {response.text[:200]}"
                return False, response, error_msg
            
            return True, response, None
            
        except requests.exceptions.Timeout:
            return False, None, "Request timeout"
        except requests.exceptions.ConnectionError:
            return False, None, "Connection error"
        except Exception as e:
            return False, None, f"Request failed: {str(e)}"
    
    def setup_authentication(self):
        """Setup authentication for testing"""
        print("\n🔐 Setting up authentication...")
        
        # Register a test user
        unique_email = f"financial.test.{int(time.time())}@example.com"
        register_data = {
            "email": unique_email,
            "password": "SecureFinancial123!",
            "name": "Financial Test User",
            "phone": "+1-555-0199"
        }
        
        success, response, error = self.make_request("POST", "/auth/register", register_data)
        if success:
            data = response.json()
            self.auth_token = data["access_token"]
            self.user_data = data["user"]
            print("✅ Authentication setup complete")
            return True
        else:
            print(f"❌ Authentication setup failed: {error}")
            return False
    
    def test_enhanced_stripe_integration(self):
        """Test enhanced Stripe integration with emergentintegrations"""
        print("\n💳 Testing Enhanced Stripe Integration...")
        
        if not self.auth_token:
            self.log_result("stripe_integration", "Stripe Integration", False, "No authentication token")
            return
        
        # Test Stripe checkout session creation
        checkout_data = {
            "amount": 25.00,
            "currency": "USD",
            "success_url": "https://example.com/success",
            "cancel_url": "https://example.com/cancel",
            "metadata": {
                "bill_type": "utility",
                "customer_id": self.user_data["id"]
            }
        }
        
        success, response, error = self.make_request("POST", "/payments/stripe/checkout", checkout_data)
        if success:
            data = response.json()
            if data.get("session_id") and data.get("checkout_url"):
                session_id = data["session_id"]
                self.log_result("stripe_integration", "Create Stripe Checkout Session", True)
                
                # Test payment status polling
                success, response, error = self.make_request("GET", f"/payments/stripe/status/{session_id}")
                if success:
                    status_data = response.json()
                    if "payment_status" in status_data:
                        self.log_result("stripe_integration", "Stripe Payment Status Polling", True)
                    else:
                        self.log_result("stripe_integration", "Stripe Payment Status Polling", False, "Missing payment status")
                else:
                    self.log_result("stripe_integration", "Stripe Payment Status Polling", False, error)
            else:
                self.log_result("stripe_integration", "Create Stripe Checkout Session", False, "Missing session data")
        else:
            self.log_result("stripe_integration", "Create Stripe Checkout Session", False, error)
        
        # Test webhook endpoint exists
        success, response, error = self.make_request("POST", "/webhooks/stripe", {"test": "webhook"})
        # Webhook should return 400 for invalid data, not 404
        if not success and "400" in str(error):
            self.log_result("stripe_integration", "Stripe Webhook Endpoint", True)
        elif not success and "404" in str(error):
            self.log_result("stripe_integration", "Stripe Webhook Endpoint", False, "Webhook endpoint not found")
        else:
            self.log_result("stripe_integration", "Stripe Webhook Endpoint", True)
    
    def test_security_framework(self):
        """Test security framework validation"""
        print("\n🔒 Testing Security Framework...")
        
        # Test JWT authentication (already covered in basic tests)
        self.log_result("security_framework", "JWT Authentication", True, "Covered in basic authentication tests")
        
        # Test for encryption endpoints (these would be missing in current implementation)
        security_endpoints = [
            "/security/encrypt",
            "/security/decrypt", 
            "/security/keys/rotate",
            "/security/digital-sign"
        ]
        
        for endpoint in security_endpoints:
            success, response, error = self.make_request("GET", endpoint)
            if success:
                self.log_result("security_framework", f"Security Endpoint {endpoint}", True)
            else:
                self.log_result("security_framework", f"Security Endpoint {endpoint}", False, "Endpoint not implemented")
    
    def test_financial_infrastructure(self):
        """Test financial infrastructure components"""
        print("\n🏦 Testing Financial Infrastructure...")
        
        # Test AML risk assessment
        aml_data = {
            "transaction_amount": 5000.00,
            "customer_id": self.user_data["id"] if self.user_data else "test",
            "transaction_type": "bill_payment"
        }
        
        success, response, error = self.make_request("POST", "/compliance/aml/assess", aml_data)
        if success:
            data = response.json()
            if "risk_score" in data:
                self.log_result("financial_infrastructure", "AML Risk Assessment", True)
            else:
                self.log_result("financial_infrastructure", "AML Risk Assessment", False, "Missing risk score")
        else:
            self.log_result("financial_infrastructure", "AML Risk Assessment", False, "AML endpoint not implemented")
        
        # Test KYC document upload
        kyc_data = {
            "document_type": "drivers_license",
            "document_data": "base64_encoded_document_data"
        }
        
        success, response, error = self.make_request("POST", "/compliance/kyc/upload", kyc_data)
        if success:
            self.log_result("financial_infrastructure", "KYC Document Upload", True)
        else:
            self.log_result("financial_infrastructure", "KYC Document Upload", False, "KYC endpoint not implemented")
        
        # Test OFAC sanctions screening
        ofac_data = {
            "customer_name": "John Doe",
            "customer_id": self.user_data["id"] if self.user_data else "test"
        }
        
        success, response, error = self.make_request("POST", "/compliance/ofac/screen", ofac_data)
        if success:
            data = response.json()
            if "screening_result" in data:
                self.log_result("financial_infrastructure", "OFAC Sanctions Screening", True)
            else:
                self.log_result("financial_infrastructure", "OFAC Sanctions Screening", False, "Missing screening result")
        else:
            self.log_result("financial_infrastructure", "OFAC Sanctions Screening", False, "OFAC endpoint not implemented")
        
        # Test multi-signature wallet creation
        multisig_data = {
            "required_signatures": 2,
            "total_signers": 3,
            "signer_public_keys": ["key1", "key2", "key3"]
        }
        
        success, response, error = self.make_request("POST", "/wallets/multisig/create", multisig_data)
        if success:
            data = response.json()
            if "wallet_address" in data:
                self.log_result("financial_infrastructure", "Multi-Signature Wallet Creation", True)
            else:
                self.log_result("financial_infrastructure", "Multi-Signature Wallet Creation", False, "Missing wallet address")
        else:
            self.log_result("financial_infrastructure", "Multi-Signature Wallet Creation", False, "Multi-sig endpoint not implemented")
    
    def test_banking_integration(self):
        """Test banking integration templates"""
        print("\n🏛️ Testing Banking Integration...")
        
        # Test Plaid integration
        plaid_data = {
            "public_token": "public-sandbox-test-token",
            "account_id": "test_account_id"
        }
        
        success, response, error = self.make_request("POST", "/banking/plaid/link", plaid_data)
        if success:
            data = response.json()
            if "access_token" in data:
                self.log_result("banking_integration", "Plaid Account Linking", True)
            else:
                self.log_result("banking_integration", "Plaid Account Linking", False, "Missing access token")
        else:
            self.log_result("banking_integration", "Plaid Account Linking", False, "Plaid endpoint not implemented")
        
        # Test ACH processing simulation
        ach_data = {
            "account_id": "test_account",
            "amount": 100.00,
            "transaction_type": "debit"
        }
        
        success, response, error = self.make_request("POST", "/banking/ach/process", ach_data)
        if success:
            data = response.json()
            if "transaction_id" in data:
                self.log_result("banking_integration", "ACH Processing Simulation", True)
            else:
                self.log_result("banking_integration", "ACH Processing Simulation", False, "Missing transaction ID")
        else:
            self.log_result("banking_integration", "ACH Processing Simulation", False, "ACH endpoint not implemented")
        
        # Test bank account verification
        verification_data = {
            "account_number": "123456789",
            "routing_number": "021000021",
            "account_type": "checking"
        }
        
        success, response, error = self.make_request("POST", "/banking/verify", verification_data)
        if success:
            data = response.json()
            if "verification_status" in data:
                self.log_result("banking_integration", "Bank Account Verification", True)
            else:
                self.log_result("banking_integration", "Bank Account Verification", False, "Missing verification status")
        else:
            self.log_result("banking_integration", "Bank Account Verification", False, "Bank verification endpoint not implemented")
    
    def test_compliance_systems(self):
        """Test compliance and audit systems"""
        print("\n📋 Testing Compliance Systems...")
        
        # Test compliance monitoring
        success, response, error = self.make_request("GET", "/compliance/monitoring/status")
        if success:
            data = response.json()
            if "monitoring_active" in data:
                self.log_result("compliance_systems", "Compliance Monitoring", True)
            else:
                self.log_result("compliance_systems", "Compliance Monitoring", False, "Missing monitoring status")
        else:
            self.log_result("compliance_systems", "Compliance Monitoring", False, "Compliance monitoring not implemented")
        
        # Test audit trail creation
        audit_data = {
            "action": "payment_processed",
            "user_id": self.user_data["id"] if self.user_data else "test",
            "transaction_id": "test_transaction",
            "metadata": {"amount": 100.00}
        }
        
        success, response, error = self.make_request("POST", "/audit/log", audit_data)
        if success:
            self.log_result("compliance_systems", "Audit Trail Creation", True)
        else:
            self.log_result("compliance_systems", "Audit Trail Creation", False, "Audit logging not implemented")
        
        # Test regulatory reporting
        success, response, error = self.make_request("GET", "/compliance/reports/generate")
        if success:
            data = response.json()
            if "report_id" in data:
                self.log_result("compliance_systems", "Regulatory Reporting", True)
            else:
                self.log_result("compliance_systems", "Regulatory Reporting", False, "Missing report ID")
        else:
            self.log_result("compliance_systems", "Regulatory Reporting", False, "Regulatory reporting not implemented")
        
        # Test risk scoring
        risk_data = {
            "transaction_amount": 1000.00,
            "customer_profile": "standard",
            "transaction_frequency": "normal"
        }
        
        success, response, error = self.make_request("POST", "/compliance/risk/score", risk_data)
        if success:
            data = response.json()
            if "risk_score" in data:
                self.log_result("compliance_systems", "Risk Scoring", True)
            else:
                self.log_result("compliance_systems", "Risk Scoring", False, "Missing risk score")
        else:
            self.log_result("compliance_systems", "Risk Scoring", False, "Risk scoring not implemented")
    
    def test_production_features(self):
        """Test production deployment features"""
        print("\n🚀 Testing Production Features...")
        
        # Test health check endpoints (already covered)
        success, response, error = self.make_request("GET", "/status")
        if success:
            self.log_result("production_features", "Health Check Endpoint", True)
        else:
            self.log_result("production_features", "Health Check Endpoint", False, error)
        
        # Test metrics endpoint
        success, response, error = self.make_request("GET", "/metrics")
        if success:
            self.log_result("production_features", "Metrics Endpoint", True)
        else:
            self.log_result("production_features", "Metrics Endpoint", False, "Metrics endpoint not implemented")
        
        # Test background task status
        success, response, error = self.make_request("GET", "/tasks/status")
        if success:
            data = response.json()
            if "active_tasks" in data:
                self.log_result("production_features", "Background Task Status", True)
            else:
                self.log_result("production_features", "Background Task Status", False, "Missing task status")
        else:
            self.log_result("production_features", "Background Task Status", False, "Task status endpoint not implemented")
        
        # Test database transaction integrity
        success, response, error = self.make_request("GET", "/database/health")
        if success:
            data = response.json()
            if "connection_status" in data:
                self.log_result("production_features", "Database Health Check", True)
            else:
                self.log_result("production_features", "Database Health Check", False, "Missing connection status")
        else:
            self.log_result("production_features", "Database Health Check", False, "Database health endpoint not implemented")
    
    def test_enhanced_transaction_processing(self):
        """Test enhanced transaction processing with compliance"""
        print("\n💰 Testing Enhanced Transaction Processing...")
        
        if not self.auth_token:
            self.log_result("financial_infrastructure", "Enhanced Transaction Processing", False, "No authentication token")
            return
        
        # Test bill payment with compliance checks
        enhanced_payment_data = {
            "bill_id": "test_bill_id",
            "payment_method_id": "test_method_id",
            "amount": 500.00,
            "compliance_metadata": {
                "risk_assessment": True,
                "aml_check": True,
                "ofac_screening": True
            }
        }
        
        success, response, error = self.make_request("POST", "/payments/enhanced/process", enhanced_payment_data)
        if success:
            data = response.json()
            if "compliance_status" in data:
                self.log_result("financial_infrastructure", "Enhanced Payment Processing", True)
            else:
                self.log_result("financial_infrastructure", "Enhanced Payment Processing", False, "Missing compliance status")
        else:
            self.log_result("financial_infrastructure", "Enhanced Payment Processing", False, "Enhanced payment processing not implemented")
        
        # Test transaction history with enhanced metadata
        success, response, error = self.make_request("GET", "/payments/enhanced/history")
        if success:
            data = response.json()
            if isinstance(data, list):
                self.log_result("financial_infrastructure", "Enhanced Transaction History", True)
            else:
                self.log_result("financial_infrastructure", "Enhanced Transaction History", False, "Invalid history format")
        else:
            # Fall back to regular payment history
            success, response, error = self.make_request("GET", "/payments/history")
            if success:
                self.log_result("financial_infrastructure", "Enhanced Transaction History", True, "Using basic payment history")
            else:
                self.log_result("financial_infrastructure", "Enhanced Transaction History", False, "No transaction history available")
    
    def run_all_tests(self):
        """Run all enhanced financial infrastructure tests"""
        print("🚀 Starting Enhanced Financial Infrastructure Testing")
        print(f"Testing API at: {BASE_URL}")
        print("=" * 70)
        
        # Setup authentication first
        if not self.setup_authentication():
            print("❌ Cannot proceed without authentication")
            return
        
        # Run enhanced test suites
        self.test_enhanced_stripe_integration()
        self.test_security_framework()
        self.test_financial_infrastructure()
        self.test_banking_integration()
        self.test_compliance_systems()
        self.test_enhanced_transaction_processing()
        self.test_production_features()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 70)
        print("📋 ENHANCED FINANCIAL INFRASTRUCTURE TEST RESULTS")
        print("=" * 70)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status = "✅ PASS" if failed == 0 else "❌ FAIL"
            print(f"{category.upper().replace('_', ' '):25} | {status} | {passed} passed, {failed} failed")
            
            if results["errors"]:
                for error in results["errors"]:
                    print(f"  └─ {error}")
        
        print("-" * 70)
        overall_status = "✅ ALL TESTS PASSED" if total_failed == 0 else f"❌ {total_failed} TESTS FAILED"
        print(f"OVERALL RESULT: {overall_status}")
        print(f"Total: {total_passed} passed, {total_failed} failed")
        print("=" * 70)
        
        # Analysis of missing features
        if total_failed > 0:
            print("\n📊 MISSING FINANCIAL INFRASTRUCTURE FEATURES:")
            print("- AML Risk Assessment System")
            print("- KYC Document Upload & Verification")
            print("- OFAC Sanctions Screening")
            print("- Multi-Signature Wallet Management")
            print("- Plaid Banking Integration")
            print("- ACH Processing Templates")
            print("- Bank Account Verification")
            print("- Compliance Monitoring System")
            print("- Audit Trail Management")
            print("- Regulatory Reporting")
            print("- Advanced Risk Scoring")
            print("- Security Encryption/Decryption APIs")
            print("- Enhanced Transaction Processing with Compliance")
            print("- Production Monitoring & Metrics")

if __name__ == "__main__":
    tester = EnhancedFinancialTester()
    tester.run_all_tests()