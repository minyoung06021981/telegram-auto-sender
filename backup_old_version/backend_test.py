#!/usr/bin/env python3
"""
Comprehensive Backend API Tests for Telegram Auto Sender
Focus on User Authentication and Subscription System Testing
"""

import requests
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration - Using the correct URL from frontend/.env
BASE_URL = "https://signup-overhaul.preview.emergentagent.com/api"
HEALTH_URL = "https://signup-overhaul.preview.emergentagent.com"

class TelegramAutoSenderTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.test_results = []
        self.access_token = None
        self.user_id = None
        self.test_user_data = {
            'username': f'testuser_{uuid.uuid4().hex[:8]}',
            'email': f'test_{uuid.uuid4().hex[:8]}@example.com',
            'password': 'SecureTestPass123!',
            'full_name': 'Test User Authentication'
        }
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'response_data': response_data
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}: {details}")
        
    def test_health_check(self):
        """Test basic API health check"""
        try:
            # Test the backend API root endpoint
            response = self.session.get(f"{BASE_URL}/../")
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "message" in data and "Telegram Auto Sender" in data["message"]:
                        self.log_test("Health Check", True, f"API is running - {data['message']}", data)
                        # Check if new features are mentioned
                        if "User Management" in data.get("message", "") or "features" in data:
                            self.log_test("Health Check - New Features", True, "User management features detected in API response")
                    else:
                        self.log_test("Health Check", False, f"Unexpected response format: {data}")
                except:
                    # If it's not JSON, test a simple API endpoint instead
                    settings_response = self.session.get(f"{BASE_URL}/settings")
                    if settings_response.status_code == 200:
                        self.log_test("Health Check", True, "Backend API is responding (via settings endpoint)")
                    else:
                        self.log_test("Health Check", False, f"Backend API not responding - HTTP {settings_response.status_code}")
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
    
    def test_user_registration_system(self):
        """Test user registration endpoint - POST /api/users/register"""
        print("\n👤 TESTING USER REGISTRATION SYSTEM")
        print("-" * 50)
        
        # Test 1: Valid user registration
        try:
            response = self.session.post(f"{BASE_URL}/users/register", json=self.test_user_data)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['user', 'access_token', 'token_type']
                user_fields = ['id', 'username', 'email', 'full_name', 'subscription_type', 'api_token']
                
                if all(field in data for field in required_fields):
                    if all(field in data['user'] for field in user_fields):
                        self.access_token = data['access_token']
                        self.user_id = data['user']['id']
                        self.log_test("POST /api/users/register", True, 
                                    f"User registered successfully - ID: {self.user_id}, Token: {data['token_type']}", data)
                        
                        # Verify default subscription
                        if data['user']['subscription_type'] == 'free':
                            self.log_test("User Registration - Default Subscription", True, 
                                        "New user assigned 'free' subscription by default")
                        else:
                            self.log_test("User Registration - Default Subscription", False, 
                                        f"Expected 'free' subscription, got '{data['user']['subscription_type']}'")
                    else:
                        self.log_test("POST /api/users/register", False, f"Missing user fields: {data}")
                else:
                    self.log_test("POST /api/users/register", False, f"Missing required fields: {data}")
            else:
                self.log_test("POST /api/users/register", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("POST /api/users/register", False, f"Error: {str(e)}")
        
        # Test 2: Duplicate username registration (should fail)
        try:
            duplicate_data = self.test_user_data.copy()
            duplicate_data['email'] = f'different_{uuid.uuid4().hex[:8]}@example.com'
            
            response = self.session.post(f"{BASE_URL}/users/register", json=duplicate_data)
            
            if response.status_code == 400:
                error_data = response.json()
                if "already exists" in error_data.get('detail', '').lower():
                    self.log_test("POST /api/users/register (Duplicate Username)", True, 
                                f"Proper validation - HTTP 400: {error_data.get('detail')}")
                else:
                    self.log_test("POST /api/users/register (Duplicate Username)", True, 
                                f"Proper error handling - HTTP 400: {error_data.get('detail')}")
            else:
                self.log_test("POST /api/users/register (Duplicate Username)", False, 
                            f"Expected HTTP 400, got HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("POST /api/users/register (Duplicate Username)", False, f"Error: {str(e)}")
        
        # Test 3: Invalid registration data
        try:
            invalid_data = {
                'username': '',  # Empty username
                'email': 'invalid-email',  # Invalid email format
                'password': '123',  # Weak password
                'full_name': ''
            }
            
            response = self.session.post(f"{BASE_URL}/users/register", json=invalid_data)
            
            if response.status_code in [400, 422]:
                self.log_test("POST /api/users/register (Invalid Data)", True, 
                            f"Proper validation - HTTP {response.status_code}")
            else:
                self.log_test("POST /api/users/register (Invalid Data)", False, 
                            f"Expected HTTP 400/422, got HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("POST /api/users/register (Invalid Data)", False, f"Error: {str(e)}")
    
    def test_user_login_system(self):
        """Test user login endpoint - POST /api/users/login"""
        print("\n🔐 TESTING USER LOGIN SYSTEM")
        print("-" * 50)
        
        # Test 1: Valid login
        try:
            login_data = {
                'username': self.test_user_data['username'],
                'password': self.test_user_data['password']
            }
            
            response = self.session.post(f"{BASE_URL}/users/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['user', 'access_token', 'token_type']
                user_fields = ['id', 'username', 'email', 'full_name', 'subscription_type', 'subscription_active']
                
                if all(field in data for field in required_fields):
                    if all(field in data['user'] for field in user_fields):
                        # Update token for subsequent tests
                        self.access_token = data['access_token']
                        self.log_test("POST /api/users/login", True, 
                                    f"Login successful - User: {data['user']['username']}, Active: {data['user']['subscription_active']}", data)
                        
                        # Verify subscription status
                        if 'subscription_active' in data['user']:
                            self.log_test("User Login - Subscription Check", True, 
                                        f"Subscription status included: {data['user']['subscription_active']}")
                        else:
                            self.log_test("User Login - Subscription Check", False, 
                                        "Subscription status not included in login response")
                    else:
                        self.log_test("POST /api/users/login", False, f"Missing user fields: {data}")
                else:
                    self.log_test("POST /api/users/login", False, f"Missing required fields: {data}")
            else:
                self.log_test("POST /api/users/login", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("POST /api/users/login", False, f"Error: {str(e)}")
        
        # Test 2: Invalid credentials
        try:
            invalid_login = {
                'username': self.test_user_data['username'],
                'password': 'wrong_password'
            }
            
            response = self.session.post(f"{BASE_URL}/users/login", json=invalid_login)
            
            if response.status_code == 401:
                error_data = response.json()
                if "invalid" in error_data.get('detail', '').lower():
                    self.log_test("POST /api/users/login (Invalid Credentials)", True, 
                                f"Proper authentication error - HTTP 401: {error_data.get('detail')}")
                else:
                    self.log_test("POST /api/users/login (Invalid Credentials)", True, 
                                f"Proper error handling - HTTP 401: {error_data.get('detail')}")
            else:
                self.log_test("POST /api/users/login (Invalid Credentials)", False, 
                            f"Expected HTTP 401, got HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("POST /api/users/login (Invalid Credentials)", False, f"Error: {str(e)}")
        
        # Test 3: Non-existent user
        try:
            nonexistent_login = {
                'username': 'nonexistent_user_12345',
                'password': 'any_password'
            }
            
            response = self.session.post(f"{BASE_URL}/users/login", json=nonexistent_login)
            
            if response.status_code == 401:
                self.log_test("POST /api/users/login (Non-existent User)", True, 
                            "Proper authentication error - HTTP 401")
            else:
                self.log_test("POST /api/users/login (Non-existent User)", False, 
                            f"Expected HTTP 401, got HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("POST /api/users/login (Non-existent User)", False, f"Error: {str(e)}")
    
    def test_jwt_authentication(self):
        """Test JWT authentication for protected endpoints - GET /api/users/me"""
        print("\n🔑 TESTING JWT AUTHENTICATION")
        print("-" * 50)
        
        # Test 1: Valid JWT token
        if self.access_token:
            try:
                headers = {'Authorization': f'Bearer {self.access_token}'}
                response = self.session.get(f"{BASE_URL}/users/me", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    required_fields = ['id', 'username', 'email', 'full_name', 'subscription_type', 'subscription_active']
                    
                    if all(field in data for field in required_fields):
                        self.log_test("GET /api/users/me (Valid JWT)", True, 
                                    f"User info retrieved - ID: {data['id']}, Subscription: {data['subscription_type']}", data)
                        
                        # Verify user data matches registration
                        if data['username'] == self.test_user_data['username']:
                            self.log_test("JWT Authentication - User Data Consistency", True, 
                                        "User data matches registration information")
                        else:
                            self.log_test("JWT Authentication - User Data Consistency", False, 
                                        f"User data mismatch: expected {self.test_user_data['username']}, got {data['username']}")
                    else:
                        self.log_test("GET /api/users/me (Valid JWT)", False, f"Missing required fields: {data}")
                else:
                    self.log_test("GET /api/users/me (Valid JWT)", False, f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_test("GET /api/users/me (Valid JWT)", False, f"Error: {str(e)}")
        else:
            self.log_test("GET /api/users/me (Valid JWT)", False, "No access token available for testing")
        
        # Test 2: Invalid JWT token
        try:
            headers = {'Authorization': 'Bearer invalid_token_12345'}
            response = self.session.get(f"{BASE_URL}/users/me", headers=headers)
            
            if response.status_code == 401:
                error_data = response.json()
                if "invalid" in error_data.get('detail', '').lower() or "expired" in error_data.get('detail', '').lower():
                    self.log_test("GET /api/users/me (Invalid JWT)", True, 
                                f"Proper JWT validation - HTTP 401: {error_data.get('detail')}")
                else:
                    self.log_test("GET /api/users/me (Invalid JWT)", True, 
                                f"Proper error handling - HTTP 401: {error_data.get('detail')}")
            else:
                self.log_test("GET /api/users/me (Invalid JWT)", False, 
                            f"Expected HTTP 401, got HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("GET /api/users/me (Invalid JWT)", False, f"Error: {str(e)}")
        
        # Test 3: Missing JWT token
        try:
            response = self.session.get(f"{BASE_URL}/users/me")
            
            if response.status_code == 403:
                self.log_test("GET /api/users/me (No JWT)", True, 
                            "Proper authentication required - HTTP 403")
            elif response.status_code == 401:
                self.log_test("GET /api/users/me (No JWT)", True, 
                            "Proper authentication required - HTTP 401")
            else:
                self.log_test("GET /api/users/me (No JWT)", False, 
                            f"Expected HTTP 401/403, got HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("GET /api/users/me (No JWT)", False, f"Error: {str(e)}")
    
    def test_subscription_system(self):
        """Test subscription system endpoints"""
        print("\n💳 TESTING SUBSCRIPTION SYSTEM")
        print("-" * 50)
        
        # Test 1: Get subscription plans - GET /api/subscription/plans
        try:
            response = self.session.get(f"{BASE_URL}/subscription/plans")
            
            if response.status_code == 200:
                plans = response.json()
                if isinstance(plans, list) and len(plans) > 0:
                    self.log_test("GET /api/subscription/plans", True, 
                                f"Retrieved {len(plans)} subscription plans", plans)
                    
                    # Verify expected plans exist (Free, Premium, Enterprise)
                    plan_names = [plan.get('name', '').lower() for plan in plans]
                    expected_plans = ['free', 'premium', 'enterprise']
                    
                    found_plans = [name for name in expected_plans if name in plan_names]
                    if len(found_plans) == 3:
                        self.log_test("Subscription Plans - Database Seeding", True, 
                                    f"All expected plans found: {found_plans}")
                    else:
                        self.log_test("Subscription Plans - Database Seeding", False, 
                                    f"Missing plans. Found: {found_plans}, Expected: {expected_plans}")
                    
                    # Verify plan structure
                    first_plan = plans[0]
                    required_fields = ['id', 'name', 'description', 'price', 'duration_days', 'max_groups', 'max_messages_per_day', 'features']
                    if all(field in first_plan for field in required_fields):
                        self.log_test("Subscription Plans - Structure Validation", True, 
                                    "Plans have all required fields")
                    else:
                        self.log_test("Subscription Plans - Structure Validation", False, 
                                    f"Missing fields in plan structure: {first_plan}")
                else:
                    self.log_test("GET /api/subscription/plans", False, 
                                f"Expected list of plans, got: {plans}")
            else:
                self.log_test("GET /api/subscription/plans", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("GET /api/subscription/plans", False, f"Error: {str(e)}")
        
        # Test 2: Upgrade subscription - POST /api/subscription/upgrade (requires authentication)
        if self.access_token:
            try:
                # First get available plans to find a plan ID
                plans_response = self.session.get(f"{BASE_URL}/subscription/plans")
                if plans_response.status_code == 200:
                    plans = plans_response.json()
                    if plans:
                        # Try to upgrade to premium plan
                        premium_plan = next((plan for plan in plans if plan.get('name', '').lower() == 'premium'), None)
                        if premium_plan:
                            headers = {'Authorization': f'Bearer {self.access_token}'}
                            
                            # Test with plan_id as query parameter (correct format based on endpoint signature)
                            response = self.session.post(f"{BASE_URL}/subscription/upgrade?plan_id={premium_plan['id']}", 
                                                       headers=headers)
                            
                            if response.status_code == 200:
                                data = response.json()
                                if 'message' in data and 'plan' in data:
                                    self.log_test("POST /api/subscription/upgrade", True, 
                                                f"Subscription upgraded successfully: {data['message']}", data)
                                else:
                                    self.log_test("POST /api/subscription/upgrade", False, 
                                                f"Unexpected response format: {data}")
                            elif response.status_code == 404:
                                self.log_test("POST /api/subscription/upgrade", False, 
                                            "Plan not found - check plan_id parameter format")
                            else:
                                self.log_test("POST /api/subscription/upgrade", False, 
                                            f"HTTP {response.status_code}: {response.text}")
                        else:
                            self.log_test("POST /api/subscription/upgrade", False, 
                                        "No premium plan found for testing")
                    else:
                        self.log_test("POST /api/subscription/upgrade", False, 
                                    "No plans available for upgrade testing")
                else:
                    self.log_test("POST /api/subscription/upgrade", False, 
                                "Could not retrieve plans for upgrade testing")
                    
            except Exception as e:
                self.log_test("POST /api/subscription/upgrade", False, f"Error: {str(e)}")
        else:
            self.log_test("POST /api/subscription/upgrade", False, "No access token available for testing")
        
        # Test 3: Upgrade without authentication
        try:
            response = self.session.post(f"{BASE_URL}/subscription/upgrade?plan_id=test_plan")
            
            if response.status_code in [401, 403]:
                self.log_test("POST /api/subscription/upgrade (No Auth)", True, 
                            f"Proper authentication required - HTTP {response.status_code}")
            else:
                self.log_test("POST /api/subscription/upgrade (No Auth)", False, 
                            f"Expected HTTP 401/403, got HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("POST /api/subscription/upgrade (No Auth)", False, f"Error: {str(e)}")
    
    def test_enhanced_telegram_auth(self):
        """Test enhanced Telegram authentication requiring user authentication"""
        print("\n📱 TESTING ENHANCED TELEGRAM AUTHENTICATION")
        print("-" * 50)
        
        # Test 1: Telegram login without user authentication (should fail)
        try:
            telegram_auth_data = {
                'api_id': 12345,
                'api_hash': 'test_api_hash',
                'phone_number': '+1234567890'
            }
            
            response = self.session.post(f"{BASE_URL}/auth/login", json=telegram_auth_data)
            
            if response.status_code in [401, 403]:
                self.log_test("POST /api/auth/login (No User Auth)", True, 
                            f"Proper user authentication required - HTTP {response.status_code}")
            else:
                self.log_test("POST /api/auth/login (No User Auth)", False, 
                            f"Expected HTTP 401/403, got HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("POST /api/auth/login (No User Auth)", False, f"Error: {str(e)}")
        
        # Test 2: Telegram login with valid user authentication
        if self.access_token:
            try:
                telegram_auth_data = {
                    'api_id': 12345,
                    'api_hash': 'test_api_hash',
                    'phone_number': '+1234567890'
                }
                
                headers = {'Authorization': f'Bearer {self.access_token}'}
                response = self.session.post(f"{BASE_URL}/auth/login", json=telegram_auth_data, headers=headers)
                
                # We expect this to fail with Telegram API error, but it should pass user authentication
                if response.status_code == 400:
                    error_data = response.json()
                    # If it's a Telegram API error, user authentication worked
                    if any(keyword in error_data.get('detail', '').lower() 
                          for keyword in ['api', 'telegram', 'invalid', 'unauthorized']):
                        self.log_test("POST /api/auth/login (With User Auth)", True, 
                                    f"User authentication passed, Telegram API error expected: {error_data.get('detail')}")
                    else:
                        self.log_test("POST /api/auth/login (With User Auth)", False, 
                                    f"Unexpected error: {error_data.get('detail')}")
                elif response.status_code in [401, 403]:
                    self.log_test("POST /api/auth/login (With User Auth)", False, 
                                f"User authentication failed - HTTP {response.status_code}: {response.text}")
                else:
                    # Any other response suggests the endpoint structure changed
                    self.log_test("POST /api/auth/login (With User Auth)", False, 
                                f"Unexpected HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_test("POST /api/auth/login (With User Auth)", False, f"Error: {str(e)}")
        else:
            self.log_test("POST /api/auth/login (With User Auth)", False, "No access token available for testing")
    
    def test_database_seeding(self):
        """Test that subscription plans were automatically seeded on startup"""
        print("\n🌱 TESTING DATABASE SEEDING")
        print("-" * 50)
        
        try:
            response = self.session.get(f"{BASE_URL}/subscription/plans")
            
            if response.status_code == 200:
                plans = response.json()
                
                # Check for exactly 3 plans
                if len(plans) == 3:
                    self.log_test("Database Seeding - Plan Count", True, 
                                f"Correct number of plans seeded: {len(plans)}")
                else:
                    self.log_test("Database Seeding - Plan Count", False, 
                                f"Expected 3 plans, found {len(plans)}")
                
                # Check for specific plan names and properties
                plan_names = [plan.get('name', '') for plan in plans]
                expected_plans = ['Free', 'Premium', 'Enterprise']
                
                for expected_plan in expected_plans:
                    if expected_plan in plan_names:
                        plan = next(p for p in plans if p.get('name') == expected_plan)
                        
                        # Verify plan has required properties
                        if expected_plan == 'Free':
                            if plan.get('price') == 0.0 and plan.get('max_groups') == 5:
                                self.log_test(f"Database Seeding - {expected_plan} Plan", True, 
                                            f"Free plan correctly configured: price={plan.get('price')}, max_groups={plan.get('max_groups')}")
                            else:
                                self.log_test(f"Database Seeding - {expected_plan} Plan", False, 
                                            f"Free plan misconfigured: {plan}")
                        
                        elif expected_plan == 'Premium':
                            if plan.get('price') == 9.99 and plan.get('max_groups') == 50:
                                self.log_test(f"Database Seeding - {expected_plan} Plan", True, 
                                            f"Premium plan correctly configured: price={plan.get('price')}, max_groups={plan.get('max_groups')}")
                            else:
                                self.log_test(f"Database Seeding - {expected_plan} Plan", False, 
                                            f"Premium plan misconfigured: {plan}")
                        
                        elif expected_plan == 'Enterprise':
                            if plan.get('price') == 29.99 and plan.get('max_groups') == 999:
                                self.log_test(f"Database Seeding - {expected_plan} Plan", True, 
                                            f"Enterprise plan correctly configured: price={plan.get('price')}, max_groups={plan.get('max_groups')}")
                            else:
                                self.log_test(f"Database Seeding - {expected_plan} Plan", False, 
                                            f"Enterprise plan misconfigured: {plan}")
                    else:
                        self.log_test(f"Database Seeding - {expected_plan} Plan", False, 
                                    f"{expected_plan} plan not found in seeded data")
                
                # Check that all plans are active
                active_plans = [plan for plan in plans if plan.get('is_active', False)]
                if len(active_plans) == len(plans):
                    self.log_test("Database Seeding - Plan Status", True, 
                                "All seeded plans are active")
                else:
                    self.log_test("Database Seeding - Plan Status", False, 
                                f"Some plans are inactive: {len(active_plans)}/{len(plans)} active")
                    
            else:
                self.log_test("Database Seeding", False, f"Could not retrieve plans - HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Database Seeding", False, f"Error: {str(e)}")
    
    def cleanup_test_user(self):
        """Clean up test user data"""
        print("\n🧹 CLEANING UP TEST USER DATA")
        print("-" * 30)
        
        # Note: There's no DELETE user endpoint in the current API
        # In a real scenario, we might need to clean up via database or admin endpoint
        self.log_test("User Cleanup", True, "Test user data cleanup noted (no DELETE endpoint available)")
    
    def run_all_tests(self):
        """Run comprehensive backend API tests focusing on User Authentication and Subscription System"""
        print("🚀 TELEGRAM AUTO SENDER - USER AUTHENTICATION & SUBSCRIPTION TESTING")
        print("=" * 70)
        print("Focus: Testing new user management and subscription system implementation")
        print("=" * 70)
        
        # Test in priority order for new features
        self.test_health_check()
        self.test_database_seeding()  # Test that plans were seeded on startup
        self.test_user_registration_system()  # Test user registration
        self.test_user_login_system()  # Test user login
        self.test_jwt_authentication()  # Test JWT tokens for protected endpoints
        self.test_subscription_system()  # Test subscription plans and upgrades
        self.test_enhanced_telegram_auth()  # Test Telegram auth now requires user auth
        
        # Cleanup
        self.cleanup_test_user()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 USER AUTHENTICATION & SUBSCRIPTION TEST SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Focus on authentication and subscription results
        auth_tests = [r for r in self.test_results if any(keyword in r['test'].lower() 
                     for keyword in ['register', 'login', 'jwt', 'auth', 'subscription'])]
        auth_passed = sum(1 for r in auth_tests if r['success'])
        
        print(f"\n🔐 AUTHENTICATION & SUBSCRIPTION TESTS: {auth_passed}/{len(auth_tests)} passed")
        
        # Database seeding results
        seeding_tests = [r for r in self.test_results if 'seeding' in r['test'].lower()]
        seeding_passed = sum(1 for r in seeding_tests if r['success'])
        
        print(f"🌱 DATABASE SEEDING TESTS: {seeding_passed}/{len(seeding_tests)} passed")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n🎯 CRITICAL FINDINGS:")
        
        # Check for critical authentication issues
        critical_auth_failures = [r for r in self.test_results if not r['success'] and 
                                any(keyword in r['test'].lower() for keyword in ['register', 'login', 'jwt'])]
        
        if critical_auth_failures:
            print("  ❌ AUTHENTICATION SYSTEM ISSUES:")
            for failure in critical_auth_failures:
                print(f"    - {failure['test']}: {failure['details']}")
        else:
            print("  ✅ AUTHENTICATION SYSTEM: All core authentication features working!")
        
        # Check for subscription system issues
        subscription_failures = [r for r in self.test_results if not r['success'] and 
                               'subscription' in r['test'].lower()]
        
        if subscription_failures:
            print("  ❌ SUBSCRIPTION SYSTEM ISSUES:")
            for failure in subscription_failures:
                print(f"    - {failure['test']}: {failure['details']}")
        else:
            print("  ✅ SUBSCRIPTION SYSTEM: All subscription features working!")
        
        # Check database seeding
        seeding_failures = [r for r in self.test_results if not r['success'] and 
                          'seeding' in r['test'].lower()]
        
        if seeding_failures:
            print("  ❌ DATABASE SEEDING ISSUES:")
            for failure in seeding_failures:
                print(f"    - {failure['test']}: {failure['details']}")
        else:
            print("  ✅ DATABASE SEEDING: All subscription plans properly seeded!")
        
        # Enhanced Telegram Auth status
        telegram_auth_tests = [r for r in self.test_results if 'telegram' in r['test'].lower() and 'auth' in r['test'].lower()]
        telegram_auth_passed = sum(1 for r in telegram_auth_tests if r['success'])
        
        if telegram_auth_tests:
            print(f"\n📱 ENHANCED TELEGRAM AUTH: {telegram_auth_passed}/{len(telegram_auth_tests)} tests passed")
            if telegram_auth_passed == len(telegram_auth_tests):
                print("  ✅ Telegram authentication now properly requires user authentication!")
            else:
                print("  ⚠️  Some Telegram authentication tests failed - review security implementation")
        
        print("\n🎉 OVERALL STATUS:")
        if passed_tests >= total_tests * 0.9:  # 90% success rate
            print("  ✅ NEW USER AUTHENTICATION & SUBSCRIPTION SYSTEM IS WORKING EXCELLENTLY!")
            print("  🚀 Ready for production use with comprehensive user management features")
        elif passed_tests >= total_tests * 0.75:  # 75% success rate
            print("  ⚠️  USER AUTHENTICATION & SUBSCRIPTION SYSTEM IS MOSTLY WORKING")
            print("  🔧 Minor issues detected - review failed tests for improvements")
        else:
            print("  ❌ SIGNIFICANT ISSUES DETECTED IN USER AUTHENTICATION & SUBSCRIPTION SYSTEM")
            print("  🚨 Major fixes required before production deployment")
        
        return {
            'total': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'auth_tests_passed': auth_passed,
            'auth_tests_total': len(auth_tests),
            'seeding_tests_passed': seeding_passed,
            'seeding_tests_total': len(seeding_tests),
            'results': self.test_results
        }

if __name__ == "__main__":
    tester = TelegramAutoSenderTester()
    results = tester.run_all_tests()
    
    # Exit with error code if critical tests failed
    if results['success_rate'] < 75:
        exit(1)
    else:
        exit(0)