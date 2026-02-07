#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Paymentus Clone
Tests all API endpoints with realistic data scenarios
"""

import requests
import json
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://payment-dashboard-24.preview.emergentagent.com/api"
TIMEOUT = 30

class PaymentusAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = TIMEOUT
        self.auth_token = None
        self.user_data = None
        self.test_results = {
            "authentication": {"passed": 0, "failed": 0, "errors": []},
            "bills": {"passed": 0, "failed": 0, "errors": []},
            "payment_methods": {"passed": 0, "failed": 0, "errors": []},
            "payments": {"passed": 0, "failed": 0, "errors": []},
            "lightning": {"passed": 0, "failed": 0, "errors": []},
            "dashboard": {"passed": 0, "failed": 0, "errors": []}
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
    
    def test_api_health(self):
        """Test basic API health endpoints"""
        print("\n🔍 Testing API Health...")
        
        # Test root endpoint
        success, response, error = self.make_request("GET", "/")
        if success:
            data = response.json()
            if data.get("message") == "Paymentus Clone API":
                self.log_result("authentication", "API Root Endpoint", True)
            else:
                self.log_result("authentication", "API Root Endpoint", False, "Unexpected response format")
        else:
            self.log_result("authentication", "API Root Endpoint", False, error)
        
        # Test status endpoint
        success, response, error = self.make_request("GET", "/status")
        if success:
            data = response.json()
            if data.get("status") == "healthy":
                self.log_result("authentication", "API Status Endpoint", True)
            else:
                self.log_result("authentication", "API Status Endpoint", False, "API not healthy")
        else:
            self.log_result("authentication", "API Status Endpoint", False, error)
    
    def test_authentication(self):
        """Test authentication system"""
        print("\n🔐 Testing Authentication System...")
        
        # Test user registration with valid data
        import time
        unique_email = f"sarah.johnson.{int(time.time())}@example.com"
        register_data = {
            "email": unique_email,
            "password": "SecurePass123!",
            "name": "Sarah Johnson",
            "phone": "+1-555-0123"
        }
        
        success, response, error = self.make_request("POST", "/auth/register", register_data)
        if success:
            data = response.json()
            if data.get("access_token") and data.get("user"):
                self.auth_token = data["access_token"]
                self.user_data = data["user"]
                self.log_result("authentication", "User Registration", True)
            else:
                self.log_result("authentication", "User Registration", False, "Missing token or user data")
        else:
            self.log_result("authentication", "User Registration", False, error)
        
        # Test duplicate registration (should fail)
        success, response, error = self.make_request("POST", "/auth/register", register_data)
        if not success and "already registered" in str(error).lower():
            self.log_result("authentication", "Duplicate Registration Prevention", True)
        else:
            self.log_result("authentication", "Duplicate Registration Prevention", False, "Should prevent duplicate registration")
        
        # Test login with correct credentials
        login_data = {
            "email": unique_email,
            "password": "SecurePass123!"
        }
        
        success, response, error = self.make_request("POST", "/auth/login", login_data)
        if success:
            data = response.json()
            if data.get("access_token"):
                self.auth_token = data["access_token"]
                self.log_result("authentication", "User Login", True)
            else:
                self.log_result("authentication", "User Login", False, "Missing access token")
        else:
            self.log_result("authentication", "User Login", False, error)
        
        # Test login with incorrect credentials
        wrong_login_data = {
            "email": unique_email,
            "password": "WrongPassword"
        }
        
        success, response, error = self.make_request("POST", "/auth/login", wrong_login_data)
        if not success and "401" in str(error):
            self.log_result("authentication", "Invalid Login Prevention", True)
        else:
            self.log_result("authentication", "Invalid Login Prevention", False, "Should reject invalid credentials")
        
        # Test protected endpoint access
        success, response, error = self.make_request("GET", "/auth/me")
        if success:
            data = response.json()
            if data.get("email") == unique_email:
                self.log_result("authentication", "Protected Endpoint Access", True)
            else:
                self.log_result("authentication", "Protected Endpoint Access", False, "Incorrect user data")
        else:
            self.log_result("authentication", "Protected Endpoint Access", False, error)
        
        # Test logout
        success, response, error = self.make_request("POST", "/auth/logout")
        if success:
            self.log_result("authentication", "User Logout", True)
        else:
            self.log_result("authentication", "User Logout", False, error)
    
    def test_bills_management(self):
        """Test bills management API"""
        print("\n📄 Testing Bills Management...")
        
        if not self.auth_token:
            self.log_result("bills", "Bills Management", False, "No authentication token")
            return
        
        # Test creating bills with different types
        bill_types = [
            {
                "biller_name": "Pacific Gas & Electric",
                "account_number": "PGE-789456123",
                "amount": 145.67,
                "due_date": (datetime.now(timezone.utc) + timedelta(days=15)).isoformat(),
                "bill_type": "utility",
                "description": "Monthly electricity bill"
            },
            {
                "biller_name": "Verizon Wireless",
                "account_number": "VZW-555123789",
                "amount": 89.99,
                "due_date": (datetime.now(timezone.utc) + timedelta(days=10)).isoformat(),
                "bill_type": "telecom",
                "description": "Mobile phone service"
            },
            {
                "biller_name": "State Farm Insurance",
                "account_number": "SF-POL789123",
                "amount": 234.50,
                "due_date": (datetime.now(timezone.utc) + timedelta(days=20)).isoformat(),
                "bill_type": "insurance",
                "description": "Auto insurance premium"
            },
            {
                "biller_name": "IRS",
                "account_number": "TAX-2024-Q1",
                "amount": 1250.00,
                "due_date": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
                "bill_type": "government",
                "description": "Quarterly tax payment"
            }
        ]
        
        created_bills = []
        for bill_data in bill_types:
            success, response, error = self.make_request("POST", "/bills", bill_data)
            if success:
                data = response.json()
                if data.get("id") and data.get("status") == "pending":
                    created_bills.append(data)
                    self.log_result("bills", f"Create {bill_data['bill_type']} Bill", True)
                else:
                    self.log_result("bills", f"Create {bill_data['bill_type']} Bill", False, "Invalid response format")
            else:
                self.log_result("bills", f"Create {bill_data['bill_type']} Bill", False, error)
        
        # Test retrieving bills
        success, response, error = self.make_request("GET", "/bills")
        if success:
            data = response.json()
            if isinstance(data, list) and len(data) >= len(created_bills):
                self.log_result("bills", "Retrieve User Bills", True)
            else:
                self.log_result("bills", "Retrieve User Bills", False, "Incorrect bills count")
        else:
            self.log_result("bills", "Retrieve User Bills", False, error)
        
        # Test updating bill
        if created_bills:
            bill_id = created_bills[0]["id"]
            update_data = {"amount": 150.00, "description": "Updated amount"}
            
            success, response, error = self.make_request("PUT", f"/bills/{bill_id}", update_data)
            if success:
                data = response.json()
                if data.get("amount") == 150.00:
                    self.log_result("bills", "Update Bill", True)
                else:
                    self.log_result("bills", "Update Bill", False, "Bill not updated correctly")
            else:
                self.log_result("bills", "Update Bill", False, error)
        
        # Test deleting bill
        if len(created_bills) > 1:
            bill_id = created_bills[-1]["id"]
            success, response, error = self.make_request("DELETE", f"/bills/{bill_id}")
            if success:
                self.log_result("bills", "Delete Bill", True)
            else:
                self.log_result("bills", "Delete Bill", False, error)
    
    def test_payment_methods(self):
        """Test payment methods management"""
        print("\n💳 Testing Payment Methods...")
        
        if not self.auth_token:
            self.log_result("payment_methods", "Payment Methods", False, "No authentication token")
            return
        
        # Test adding different payment method types
        payment_methods = [
            {
                "type": "credit_card",
                "card_number": "4532123456789012",
                "expiry_month": 12,
                "expiry_year": 2027,
                "cvv": "123",
                "is_default": True
            },
            {
                "type": "bank_account",
                "bank_name": "Chase Bank",
                "account_type": "checking",
                "is_default": False
            },
            {
                "type": "bitcoin",
                "bitcoin_address": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
                "is_default": False
            }
        ]
        
        created_methods = []
        for method_data in payment_methods:
            success, response, error = self.make_request("POST", "/payment-methods", method_data)
            if success:
                data = response.json()
                if data.get("id") and data.get("type") == method_data["type"]:
                    created_methods.append(data)
                    self.log_result("payment_methods", f"Add {method_data['type']} Method", True)
                else:
                    self.log_result("payment_methods", f"Add {method_data['type']} Method", False, "Invalid response")
            else:
                self.log_result("payment_methods", f"Add {method_data['type']} Method", False, error)
        
        # Test retrieving payment methods
        success, response, error = self.make_request("GET", "/payment-methods")
        if success:
            data = response.json()
            if isinstance(data, list) and len(data) >= len(created_methods):
                self.log_result("payment_methods", "Retrieve Payment Methods", True)
            else:
                self.log_result("payment_methods", "Retrieve Payment Methods", False, "Incorrect methods count")
        else:
            self.log_result("payment_methods", "Retrieve Payment Methods", False, error)
        
        # Test deleting payment method
        if len(created_methods) > 1:
            method_id = created_methods[-1]["id"]
            success, response, error = self.make_request("DELETE", f"/payment-methods/{method_id}")
            if success:
                self.log_result("payment_methods", "Delete Payment Method", True)
            else:
                self.log_result("payment_methods", "Delete Payment Method", False, error)
    
    def test_payment_processing(self):
        """Test payment processing system"""
        print("\n💰 Testing Payment Processing...")
        
        if not self.auth_token:
            self.log_result("payments", "Payment Processing", False, "No authentication token")
            return
        
        # First get available bills and payment methods
        bills_success, bills_response, _ = self.make_request("GET", "/bills")
        methods_success, methods_response, _ = self.make_request("GET", "/payment-methods")
        
        if not (bills_success and methods_success):
            self.log_result("payments", "Payment Processing Setup", False, "Cannot get bills or payment methods")
            return
        
        bills = bills_response.json()
        methods = methods_response.json()
        
        if not bills or not methods:
            self.log_result("payments", "Payment Processing Setup", False, "No bills or payment methods available")
            return
        
        # Test processing payment
        payment_data = {
            "bill_id": bills[0]["id"],
            "payment_method_id": methods[0]["id"],
            "amount": bills[0]["amount"]
        }
        
        success, response, error = self.make_request("POST", "/payments/process", payment_data)
        if success:
            data = response.json()
            if data.get("id") and data.get("status") == "completed":
                self.log_result("payments", "Process Payment", True)
            else:
                self.log_result("payments", "Process Payment", False, "Payment not completed")
        else:
            self.log_result("payments", "Process Payment", False, error)
        
        # Test payment history
        success, response, error = self.make_request("GET", "/payments/history")
        if success:
            data = response.json()
            if isinstance(data, list):
                self.log_result("payments", "Payment History", True)
            else:
                self.log_result("payments", "Payment History", False, "Invalid history format")
        else:
            self.log_result("payments", "Payment History", False, error)
    
    def test_lightning_network(self):
        """Test Lightning Network integration"""
        print("\n⚡ Testing Lightning Network...")
        
        if not self.auth_token:
            self.log_result("lightning", "Lightning Network", False, "No authentication token")
            return
        
        # Test Lightning invoice creation
        success, response, error = self.make_request("POST", "/lightning/invoice?amount_usd=25.50&memo=Test Lightning payment for utility bill")
        if success:
            data = response.json()
            if data.get("payment_hash") and data.get("payment_request"):
                payment_hash = data["payment_hash"]
                self.log_result("lightning", "Create Lightning Invoice", True)
                
                # Test Lightning payment verification
                success, response, error = self.make_request("POST", f"/lightning/verify?payment_hash={payment_hash}")
                if success:
                    verify_data = response.json()
                    if verify_data.get("settled"):
                        self.log_result("lightning", "Verify Lightning Payment", True)
                    else:
                        self.log_result("lightning", "Verify Lightning Payment", False, "Payment not settled")
                else:
                    self.log_result("lightning", "Verify Lightning Payment", False, error)
            else:
                self.log_result("lightning", "Create Lightning Invoice", False, "Missing invoice data")
        else:
            self.log_result("lightning", "Create Lightning Invoice", False, error)
    
    def test_dashboard_analytics(self):
        """Test dashboard analytics"""
        print("\n📊 Testing Dashboard Analytics...")
        
        if not self.auth_token:
            self.log_result("dashboard", "Dashboard Analytics", False, "No authentication token")
            return
        
        # Test dashboard metrics
        success, response, error = self.make_request("GET", "/dashboard/metrics")
        if success:
            data = response.json()
            required_fields = ["total_due", "monthly_total", "method_count", "recent_transactions"]
            if all(field in data for field in required_fields):
                self.log_result("dashboard", "Dashboard Metrics", True)
            else:
                missing = [f for f in required_fields if f not in data]
                self.log_result("dashboard", "Dashboard Metrics", False, f"Missing fields: {missing}")
        else:
            self.log_result("dashboard", "Dashboard Metrics", False, error)
    
    def test_security_and_errors(self):
        """Test security and error handling"""
        print("\n🔒 Testing Security & Error Handling...")
        
        # Test unauthorized access
        old_token = self.auth_token
        self.auth_token = None
        
        success, response, error = self.make_request("GET", "/bills")
        if not success and ("403" in str(error) or "401" in str(error)):
            self.log_result("authentication", "Unauthorized Access Prevention", True)
        else:
            self.log_result("authentication", "Unauthorized Access Prevention", False, "Should block unauthorized access")
        
        self.auth_token = old_token
        
        # Test invalid data submission
        invalid_bill = {
            "biller_name": "",  # Invalid empty name
            "amount": -50,      # Invalid negative amount
            "bill_type": "invalid_type"  # Invalid type
        }
        
        success, response, error = self.make_request("POST", "/bills", invalid_bill)
        if not success:
            self.log_result("bills", "Invalid Data Rejection", True)
        else:
            self.log_result("bills", "Invalid Data Rejection", False, "Should reject invalid data")
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Comprehensive Backend Testing for Paymentus Clone")
        print(f"Testing API at: {BASE_URL}")
        print("=" * 60)
        
        # Run test suites in order
        self.test_api_health()
        self.test_authentication()
        self.test_bills_management()
        self.test_payment_methods()
        self.test_payment_processing()
        self.test_lightning_network()
        self.test_dashboard_analytics()
        self.test_security_and_errors()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("📋 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status = "✅ PASS" if failed == 0 else "❌ FAIL"
            print(f"{category.upper():20} | {status} | {passed} passed, {failed} failed")
            
            if results["errors"]:
                for error in results["errors"]:
                    print(f"  └─ {error}")
        
        print("-" * 60)
        overall_status = "✅ ALL TESTS PASSED" if total_failed == 0 else f"❌ {total_failed} TESTS FAILED"
        print(f"OVERALL RESULT: {overall_status}")
        print(f"Total: {total_passed} passed, {total_failed} failed")
        print("=" * 60)

if __name__ == "__main__":
    tester = PaymentusAPITester()
    tester.run_all_tests()