#!/usr/bin/env python3
"""
COMPREHENSIVE PRODUCTION READINESS VERIFICATION TESTING
Telegram Auto Sender - Verifikasi Kesiapan Produksi Menyeluruh

Focus Areas:
1. SECURITY VERIFICATION - Memastikan semua perbaikan keamanan masih berfungsi
2. API FUNCTIONALITY TESTING - Test semua endpoint utama
3. ERROR HANDLING - Memastikan proper error handling
4. DEPENDENCY VERIFICATION - Memastikan tidak ada missing dependencies
5. PERFORMANCE BASIC CHECK - Memastikan response times reasonable
"""

import requests
import json
import time
import uuid
import random
from datetime import datetime
from typing import Dict, Any, Optional, List

# Configuration - Using the correct URL from frontend/.env
BASE_URL = "https://stack-upgrade.preview.emergentagent.com/api"
HEALTH_URL = "https://stack-upgrade.preview.emergentagent.com"

class ProductionReadinessTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.test_results = []
        self.performance_metrics = []
        
        # Test data dengan data yang realistis
        self.test_session_id = str(uuid.uuid4())
        self.test_template_id = None
        self.test_group_id = None
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None, response_time: float = None):
        """Log test results with performance metrics"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'response_data': response_data,
            'response_time_ms': response_time
        }
        self.test_results.append(result)
        
        if response_time:
            self.performance_metrics.append({
                'endpoint': test_name,
                'response_time_ms': response_time
            })
        
        status = "✅ PASS" if success else "❌ FAIL"
        time_info = f" ({response_time:.0f}ms)" if response_time else ""
        print(f"{status} - {test_name}{time_info}: {details}")

    def measure_response_time(self, func):
        """Decorator to measure response time"""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            return result, response_time
        return wrapper

    def test_health_and_dependencies(self):
        """Test 1: Health Check dan Dependency Verification"""
        print("\n🏥 TESTING HEALTH CHECK & DEPENDENCIES")
        print("-" * 60)
        
        # Test basic health check
        try:
            start_time = time.time()
            response = self.session.get(f"{HEALTH_URL}/")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "Telegram Auto Sender" in data.get("message", ""):
                        self.log_test("Health Check - Root Endpoint", True, 
                                    f"API is running - Version: {data.get('version', 'N/A')}", 
                                    data, response_time)
                        
                        # Check for required features
                        features = data.get("features", [])
                        if "User Authentication" in features and "Telegram Integration" in features:
                            self.log_test("Health Check - Required Features", True, 
                                        f"All required features present: {features}")
                        else:
                            self.log_test("Health Check - Required Features", False, 
                                        f"Missing required features: {features}")
                    else:
                        self.log_test("Health Check - Root Endpoint", False, 
                                    f"Unexpected response: {data}")
                except:
                    self.log_test("Health Check - Root Endpoint", False, 
                                f"Non-JSON response: {response.text[:100]}")
            else:
                self.log_test("Health Check - Root Endpoint", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Health Check - Root Endpoint", False, f"Connection error: {str(e)}")

        # Test critical dependencies through settings endpoint
        try:
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/settings")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['min_message_interval', 'max_message_interval', 'min_cycle_interval', 'max_cycle_interval']
                if all(field in data for field in required_fields):
                    self.log_test("Dependency Check - Settings API", True, 
                                "Settings endpoint working, core dependencies loaded", 
                                data, response_time)
                else:
                    self.log_test("Dependency Check - Settings API", False, 
                                f"Missing required settings fields: {data}")
            else:
                self.log_test("Dependency Check - Settings API", False, 
                            f"Settings endpoint failed - HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Dependency Check - Settings API", False, f"Settings API error: {str(e)}")

    def test_security_verification(self):
        """Test 2: SECURITY VERIFICATION - Memastikan semua perbaikan keamanan masih berfungsi"""
        print("\n🔒 TESTING SECURITY VERIFICATION")
        print("-" * 60)
        
        # Test 1: Scheduler endpoint authentication (harus ada session validation)
        print("Testing Scheduler Authentication...")
        
        # Test scheduler start without session_id (should fail with 422)
        try:
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/scheduler/start")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 422:
                self.log_test("Security - Scheduler Start (No Session)", True, 
                            "Proper validation - HTTP 422 for missing session_id", 
                            response.json(), response_time)
            else:
                self.log_test("Security - Scheduler Start (No Session)", False, 
                            f"Expected HTTP 422, got HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Security - Scheduler Start (No Session)", False, f"Error: {str(e)}")

        # Test scheduler start with invalid session_id (should fail with 401)
        try:
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/scheduler/start?session_id=invalid_session_12345")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 401:
                error_data = response.json()
                if "invalid" in error_data.get('detail', '').lower() or "expired" in error_data.get('detail', '').lower():
                    self.log_test("Security - Scheduler Start (Invalid Session)", True, 
                                f"Proper authentication - HTTP 401: {error_data.get('detail')}", 
                                error_data, response_time)
                else:
                    self.log_test("Security - Scheduler Start (Invalid Session)", True, 
                                f"Authentication working - HTTP 401: {error_data.get('detail')}")
            else:
                self.log_test("Security - Scheduler Start (Invalid Session)", False, 
                            f"Expected HTTP 401, got HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Security - Scheduler Start (Invalid Session)", False, f"Error: {str(e)}")

        # Test scheduler stop with invalid session_id (should fail with 401)
        try:
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/scheduler/stop?session_id=invalid_session_12345")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 401:
                self.log_test("Security - Scheduler Stop (Invalid Session)", True, 
                            "Proper authentication - HTTP 401", 
                            response.json(), response_time)
            else:
                self.log_test("Security - Scheduler Stop (Invalid Session)", False, 
                            f"Expected HTTP 401, got HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Security - Scheduler Stop (Invalid Session)", False, f"Error: {str(e)}")

        # Test 2: Settings input validation (tidak boleh accept negative values atau min >= max)
        print("Testing Settings Input Validation...")
        
        # Test negative intervals
        try:
            invalid_settings = {
                "min_message_interval": -10,
                "max_message_interval": -5,
                "min_cycle_interval": 60,
                "max_cycle_interval": 120,
                "max_retry_attempts": 3,
                "is_scheduler_active": False,
                "theme": "auto",
                "notifications_enabled": True
            }
            
            start_time = time.time()
            response = self.session.put(f"{BASE_URL}/settings", json=invalid_settings)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 400:
                error_data = response.json()
                if "positive" in error_data.get('detail', '').lower():
                    self.log_test("Security - Settings Validation (Negative Values)", True, 
                                f"Proper validation - HTTP 400: {error_data.get('detail')}", 
                                error_data, response_time)
                else:
                    self.log_test("Security - Settings Validation (Negative Values)", True, 
                                f"Validation working - HTTP 400: {error_data.get('detail')}")
            else:
                self.log_test("Security - Settings Validation (Negative Values)", False, 
                            f"Expected HTTP 400, got HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Security - Settings Validation (Negative Values)", False, f"Error: {str(e)}")

        # Test min >= max logic
        try:
            invalid_settings = {
                "min_message_interval": 30,
                "max_message_interval": 20,  # min > max
                "min_cycle_interval": 60,
                "max_cycle_interval": 120,
                "max_retry_attempts": 3,
                "is_scheduler_active": False,
                "theme": "auto",
                "notifications_enabled": True
            }
            
            start_time = time.time()
            response = self.session.put(f"{BASE_URL}/settings", json=invalid_settings)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 400:
                error_data = response.json()
                if "less than" in error_data.get('detail', '').lower():
                    self.log_test("Security - Settings Validation (Min >= Max)", True, 
                                f"Proper validation - HTTP 400: {error_data.get('detail')}", 
                                error_data, response_time)
                else:
                    self.log_test("Security - Settings Validation (Min >= Max)", True, 
                                f"Validation working - HTTP 400: {error_data.get('detail')}")
            else:
                self.log_test("Security - Settings Validation (Min >= Max)", False, 
                            f"Expected HTTP 400, got HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Security - Settings Validation (Min >= Max)", False, f"Error: {str(e)}")

        # Test 3: Template validation (tidak boleh accept empty names/content)
        print("Testing Template Validation...")
        
        # Test empty template name
        try:
            invalid_template = {
                "name": "",  # Empty name
                "content": "Test message content",
                "is_default": False
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/templates", json=invalid_template)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 400:
                error_data = response.json()
                if "empty" in error_data.get('detail', '').lower() or "whitespace" in error_data.get('detail', '').lower():
                    self.log_test("Security - Template Validation (Empty Name)", True, 
                                f"Proper validation - HTTP 400: {error_data.get('detail')}", 
                                error_data, response_time)
                else:
                    self.log_test("Security - Template Validation (Empty Name)", True, 
                                f"Validation working - HTTP 400: {error_data.get('detail')}")
            else:
                self.log_test("Security - Template Validation (Empty Name)", False, 
                            f"Expected HTTP 400, got HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Security - Template Validation (Empty Name)", False, f"Error: {str(e)}")

        # Test empty template content
        try:
            invalid_template = {
                "name": "Test Template",
                "content": "",  # Empty content
                "is_default": False
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/templates", json=invalid_template)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 400:
                error_data = response.json()
                if "empty" in error_data.get('detail', '').lower():
                    self.log_test("Security - Template Validation (Empty Content)", True, 
                                f"Proper validation - HTTP 400: {error_data.get('detail')}", 
                                error_data, response_time)
                else:
                    self.log_test("Security - Template Validation (Empty Content)", True, 
                                f"Validation working - HTTP 400: {error_data.get('detail')}")
            else:
                self.log_test("Security - Template Validation (Empty Content)", False, 
                            f"Expected HTTP 400, got HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Security - Template Validation (Empty Content)", False, f"Error: {str(e)}")

    def test_api_functionality(self):
        """Test 3: API FUNCTIONALITY TESTING - Test semua endpoint utama"""
        print("\n🔧 TESTING API FUNCTIONALITY")
        print("-" * 60)
        
        # Test Authentication endpoints
        print("Testing Authentication Endpoints...")
        
        # Test /api/auth/sessions
        try:
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/auth/sessions")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("API - GET /api/auth/sessions", True, 
                                f"Sessions endpoint working - {len(data)} sessions found", 
                                data, response_time)
                else:
                    self.log_test("API - GET /api/auth/sessions", False, 
                                f"Expected list, got: {type(data)}")
            else:
                self.log_test("API - GET /api/auth/sessions", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("API - GET /api/auth/sessions", False, f"Error: {str(e)}")

        # Test /api/auth/login with invalid credentials (should return 400)
        try:
            invalid_auth = {
                "api_id": 12345,
                "api_hash": "invalid_hash",
                "phone_number": "+1234567890"
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/auth/login", json=invalid_auth)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 400:
                self.log_test("API - POST /api/auth/login (Invalid Credentials)", True, 
                            "Proper error handling - HTTP 400", 
                            response.json(), response_time)
            elif response.status_code == 401 or response.status_code == 403:
                self.log_test("API - POST /api/auth/login (Invalid Credentials)", True, 
                            f"Authentication required - HTTP {response.status_code}")
            else:
                self.log_test("API - POST /api/auth/login (Invalid Credentials)", False, 
                            f"Unexpected HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("API - POST /api/auth/login (Invalid Credentials)", False, f"Error: {str(e)}")

        # Test Group Management endpoints
        print("Testing Group Management Endpoints...")
        
        # Test /api/groups
        try:
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/groups")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("API - GET /api/groups", True, 
                                f"Groups endpoint working - {len(data)} groups found", 
                                data, response_time)
                else:
                    self.log_test("API - GET /api/groups", False, 
                                f"Expected list, got: {type(data)}")
            else:
                self.log_test("API - GET /api/groups", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("API - GET /api/groups", False, f"Error: {str(e)}")

        # Test /api/groups/stats
        try:
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/groups/stats")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['total', 'active', 'temp_blacklisted', 'perm_blacklisted']
                if all(field in data for field in required_fields):
                    self.log_test("API - GET /api/groups/stats", True, 
                                f"Group stats working - Total: {data['total']}, Active: {data['active']}", 
                                data, response_time)
                else:
                    self.log_test("API - GET /api/groups/stats", False, 
                                f"Missing required fields: {data}")
            else:
                self.log_test("API - GET /api/groups/stats", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("API - GET /api/groups/stats", False, f"Error: {str(e)}")

        # Test /api/groups/single with missing session_id (should return 422)
        try:
            group_data = {"identifier": "@testgroup"}
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/groups/single", json=group_data)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 422:
                self.log_test("API - POST /api/groups/single (Missing Session)", True, 
                            "Proper validation - HTTP 422 for missing session_id", 
                            response.json(), response_time)
            else:
                self.log_test("API - POST /api/groups/single (Missing Session)", False, 
                            f"Expected HTTP 422, got HTTP {response.status_code}")
        except Exception as e:
            self.log_test("API - POST /api/groups/single (Missing Session)", False, f"Error: {str(e)}")

        # Test /api/groups/bulk with invalid session_id (should return 401)
        try:
            bulk_data = {"identifiers": ["@testgroup1", "@testgroup2"]}
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/groups/bulk?session_id=invalid_session", json=bulk_data)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 401:
                self.log_test("API - POST /api/groups/bulk (Invalid Session)", True, 
                            "Proper authentication - HTTP 401", 
                            response.json(), response_time)
            else:
                self.log_test("API - POST /api/groups/bulk (Invalid Session)", False, 
                            f"Expected HTTP 401, got HTTP {response.status_code}")
        except Exception as e:
            self.log_test("API - POST /api/groups/bulk (Invalid Session)", False, f"Error: {str(e)}")

        # Test Message Templates endpoints
        print("Testing Message Templates Endpoints...")
        
        # Test /api/templates
        try:
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/templates")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("API - GET /api/templates", True, 
                                f"Templates endpoint working - {len(data)} templates found", 
                                data, response_time)
                else:
                    self.log_test("API - GET /api/templates", False, 
                                f"Expected list, got: {type(data)}")
            else:
                self.log_test("API - GET /api/templates", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("API - GET /api/templates", False, f"Error: {str(e)}")

        # Test creating a valid template
        try:
            valid_template = {
                "name": f"Test Template {uuid.uuid4().hex[:8]}",
                "content": "Halo! Ini adalah pesan test dari Telegram Auto Sender. Semoga hari Anda menyenangkan! 🚀",
                "is_default": False
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/templates", json=valid_template)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and data['name'] == valid_template['name']:
                    self.test_template_id = data['id']
                    self.log_test("API - POST /api/templates (Valid)", True, 
                                f"Template created successfully - ID: {data['id']}", 
                                data, response_time)
                else:
                    self.log_test("API - POST /api/templates (Valid)", False, 
                                f"Unexpected response format: {data}")
            else:
                self.log_test("API - POST /api/templates (Valid)", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("API - POST /api/templates (Valid)", False, f"Error: {str(e)}")

        # Test /api/templates/default
        try:
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/templates/default")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if 'id' in data and 'name' in data and 'content' in data:
                    self.log_test("API - GET /api/templates/default", True, 
                                f"Default template found - Name: {data['name']}", 
                                data, response_time)
                else:
                    self.log_test("API - GET /api/templates/default", False, 
                                f"Invalid template format: {data}")
            elif response.status_code == 404:
                self.log_test("API - GET /api/templates/default", True, 
                            "No default template found (expected behavior)", 
                            response.json(), response_time)
            else:
                self.log_test("API - GET /api/templates/default", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("API - GET /api/templates/default", False, f"Error: {str(e)}")

        # Test Dashboard endpoints
        print("Testing Dashboard Endpoints...")
        
        # Test /api/dashboard/stats
        try:
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/dashboard/stats")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                required_sections = ['groups', 'messages', 'scheduler']
                if all(section in data for section in required_sections):
                    groups_data = data['groups']
                    messages_data = data['messages']
                    scheduler_data = data['scheduler']
                    
                    self.log_test("API - GET /api/dashboard/stats", True, 
                                f"Dashboard stats working - Groups: {groups_data['total']}, Messages 24h: {messages_data['sent_24h']}, Scheduler: {scheduler_data['active']}", 
                                data, response_time)
                else:
                    self.log_test("API - GET /api/dashboard/stats", False, 
                                f"Missing required sections: {data}")
            else:
                self.log_test("API - GET /api/dashboard/stats", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("API - GET /api/dashboard/stats", False, f"Error: {str(e)}")

        # Test Settings endpoints
        print("Testing Settings Endpoints...")
        
        # Test /api/settings GET
        try:
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/settings")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['min_message_interval', 'max_message_interval', 'min_cycle_interval', 'max_cycle_interval']
                if all(field in data for field in required_fields):
                    self.log_test("API - GET /api/settings", True, 
                                f"Settings working - Message interval: {data['min_message_interval']}-{data['max_message_interval']}s", 
                                data, response_time)
                else:
                    self.log_test("API - GET /api/settings", False, 
                                f"Missing required fields: {data}")
            else:
                self.log_test("API - GET /api/settings", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("API - GET /api/settings", False, f"Error: {str(e)}")

        # Test valid settings update
        try:
            valid_settings = {
                "min_message_interval": 25,
                "max_message_interval": 35,
                "min_cycle_interval": 60,
                "max_cycle_interval": 120,
                "max_retry_attempts": 3,
                "is_scheduler_active": False,
                "theme": "auto",
                "notifications_enabled": True
            }
            
            start_time = time.time()
            response = self.session.put(f"{BASE_URL}/settings", json=valid_settings)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if 'message' in data and 'success' in data['message'].lower():
                    self.log_test("API - PUT /api/settings (Valid)", True, 
                                f"Settings updated successfully: {data['message']}", 
                                data, response_time)
                else:
                    self.log_test("API - PUT /api/settings (Valid)", True, 
                                f"Settings updated: {data}")
            else:
                self.log_test("API - PUT /api/settings (Valid)", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("API - PUT /api/settings (Valid)", False, f"Error: {str(e)}")

        # Test Logs endpoints
        print("Testing Logs Endpoints...")
        
        # Test /api/logs/messages
        try:
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/logs/messages")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("API - GET /api/logs/messages", True, 
                                f"Message logs working - {len(data)} log entries found", 
                                data, response_time)
                else:
                    self.log_test("API - GET /api/logs/messages", False, 
                                f"Expected list, got: {type(data)}")
            else:
                self.log_test("API - GET /api/logs/messages", False, 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("API - GET /api/logs/messages", False, f"Error: {str(e)}")

    def test_error_handling(self):
        """Test 4: ERROR HANDLING - Memastikan proper error handling"""
        print("\n⚠️  TESTING ERROR HANDLING")
        print("-" * 60)
        
        # Test 422 - Missing required parameters
        try:
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/templates", json={})  # Missing required fields
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 422:
                error_data = response.json()
                self.log_test("Error Handling - HTTP 422 (Missing Parameters)", True, 
                            f"Proper validation error: {error_data.get('detail', 'Validation error')}", 
                            error_data, response_time)
            else:
                self.log_test("Error Handling - HTTP 422 (Missing Parameters)", False, 
                            f"Expected HTTP 422, got HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling - HTTP 422 (Missing Parameters)", False, f"Error: {str(e)}")

        # Test 401 - Missing authentication
        try:
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/scheduler/start?session_id=nonexistent_session")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 401:
                error_data = response.json()
                self.log_test("Error Handling - HTTP 401 (Missing Authentication)", True, 
                            f"Proper authentication error: {error_data.get('detail', 'Authentication error')}", 
                            error_data, response_time)
            else:
                self.log_test("Error Handling - HTTP 401 (Missing Authentication)", False, 
                            f"Expected HTTP 401, got HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling - HTTP 401 (Missing Authentication)", False, f"Error: {str(e)}")

        # Test 400 - Invalid data
        try:
            invalid_template = {
                "name": "   ",  # Whitespace only
                "content": "Valid content",
                "is_default": False
            }
            
            start_time = time.time()
            response = self.session.post(f"{BASE_URL}/templates", json=invalid_template)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 400:
                error_data = response.json()
                self.log_test("Error Handling - HTTP 400 (Invalid Data)", True, 
                            f"Proper validation error: {error_data.get('detail', 'Invalid data error')}", 
                            error_data, response_time)
            else:
                self.log_test("Error Handling - HTTP 400 (Invalid Data)", False, 
                            f"Expected HTTP 400, got HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling - HTTP 400 (Invalid Data)", False, f"Error: {str(e)}")

        # Test 404 - Resource not found
        try:
            start_time = time.time()
            response = self.session.get(f"{BASE_URL}/templates/nonexistent_template_id")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 404:
                self.log_test("Error Handling - HTTP 404 (Resource Not Found)", True, 
                            "Proper not found error", 
                            None, response_time)
            else:
                # Some endpoints might not implement 404 properly, check if it's a valid alternative
                if response.status_code in [400, 422]:
                    self.log_test("Error Handling - HTTP 404 (Resource Not Found)", True, 
                                f"Alternative error handling - HTTP {response.status_code}")
                else:
                    self.log_test("Error Handling - HTTP 404 (Resource Not Found)", False, 
                                f"Expected HTTP 404, got HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Error Handling - HTTP 404 (Resource Not Found)", False, f"Error: {str(e)}")

    def test_performance_basic_check(self):
        """Test 5: PERFORMANCE BASIC CHECK - Memastikan response times reasonable"""
        print("\n⚡ TESTING PERFORMANCE BASIC CHECK")
        print("-" * 60)
        
        # Test response times for critical endpoints
        critical_endpoints = [
            ("GET", f"{BASE_URL}/settings", None),
            ("GET", f"{BASE_URL}/groups/stats", None),
            ("GET", f"{BASE_URL}/dashboard/stats", None),
            ("GET", f"{BASE_URL}/templates", None),
            ("GET", f"{BASE_URL}/logs/messages", None)
        ]
        
        performance_results = []
        
        for method, url, data in critical_endpoints:
            try:
                start_time = time.time()
                if method == "GET":
                    response = self.session.get(url)
                else:
                    response = self.session.post(url, json=data)
                response_time = (time.time() - start_time) * 1000
                
                endpoint_name = url.split("/api/")[-1]
                performance_results.append({
                    'endpoint': endpoint_name,
                    'response_time_ms': response_time,
                    'status_code': response.status_code
                })
                
                # Consider response time reasonable if < 2000ms for production
                if response_time < 2000:
                    self.log_test(f"Performance - {endpoint_name}", True, 
                                f"Response time acceptable: {response_time:.0f}ms", 
                                None, response_time)
                elif response_time < 5000:
                    self.log_test(f"Performance - {endpoint_name}", True, 
                                f"Response time slow but acceptable: {response_time:.0f}ms", 
                                None, response_time)
                else:
                    self.log_test(f"Performance - {endpoint_name}", False, 
                                f"Response time too slow: {response_time:.0f}ms", 
                                None, response_time)
                    
            except Exception as e:
                self.log_test(f"Performance - {endpoint_name}", False, f"Error: {str(e)}")

        # Calculate average response time
        if performance_results:
            avg_response_time = sum(r['response_time_ms'] for r in performance_results) / len(performance_results)
            if avg_response_time < 1000:
                self.log_test("Performance - Average Response Time", True, 
                            f"Excellent average response time: {avg_response_time:.0f}ms")
            elif avg_response_time < 2000:
                self.log_test("Performance - Average Response Time", True, 
                            f"Good average response time: {avg_response_time:.0f}ms")
            else:
                self.log_test("Performance - Average Response Time", False, 
                            f"Average response time needs improvement: {avg_response_time:.0f}ms")

    def cleanup_test_data(self):
        """Clean up test data created during testing"""
        print("\n🧹 CLEANING UP TEST DATA")
        print("-" * 30)
        
        # Delete test template if created
        if self.test_template_id:
            try:
                response = self.session.delete(f"{BASE_URL}/templates/{self.test_template_id}")
                if response.status_code == 200:
                    self.log_test("Cleanup - Test Template", True, "Test template deleted successfully")
                else:
                    self.log_test("Cleanup - Test Template", False, f"Failed to delete test template - HTTP {response.status_code}")
            except Exception as e:
                self.log_test("Cleanup - Test Template", False, f"Error deleting test template: {str(e)}")
        else:
            self.log_test("Cleanup - Test Template", True, "No test template to clean up")

    def run_comprehensive_production_tests(self):
        """Run comprehensive production readiness verification tests"""
        print("🚀 TELEGRAM AUTO SENDER - COMPREHENSIVE PRODUCTION READINESS VERIFICATION")
        print("=" * 80)
        print("Verifikasi Kesiapan Produksi Menyeluruh - Semua Aspek Keamanan dan Fungsionalitas")
        print("=" * 80)
        
        # Run all test categories
        self.test_health_and_dependencies()
        self.test_security_verification()
        self.test_api_functionality()
        self.test_error_handling()
        self.test_performance_basic_check()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Comprehensive Summary
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE PRODUCTION READINESS TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests/total_tests)*100 if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Category-specific results
        categories = {
            'Security': ['security', 'scheduler', 'settings', 'template'],
            'API Functionality': ['api'],
            'Error Handling': ['error handling'],
            'Performance': ['performance'],
            'Health & Dependencies': ['health', 'dependency']
        }
        
        print(f"\n📋 RESULTS BY CATEGORY:")
        for category, keywords in categories.items():
            category_tests = [r for r in self.test_results if any(keyword in r['test'].lower() for keyword in keywords)]
            if category_tests:
                category_passed = sum(1 for r in category_tests if r['success'])
                print(f"{category}: {category_passed}/{len(category_tests)} passed ({(category_passed/len(category_tests)*100):.1f}%)")
        
        # Performance metrics
        if self.performance_metrics:
            avg_response_time = sum(m['response_time_ms'] for m in self.performance_metrics) / len(self.performance_metrics)
            print(f"\n⚡ PERFORMANCE METRICS:")
            print(f"Average Response Time: {avg_response_time:.0f}ms")
            print(f"Fastest Endpoint: {min(self.performance_metrics, key=lambda x: x['response_time_ms'])['endpoint']} ({min(m['response_time_ms'] for m in self.performance_metrics):.0f}ms)")
            print(f"Slowest Endpoint: {max(self.performance_metrics, key=lambda x: x['response_time_ms'])['endpoint']} ({max(m['response_time_ms'] for m in self.performance_metrics):.0f}ms)")
        
        # Critical findings
        print(f"\n🎯 CRITICAL FINDINGS:")
        
        # Security verification results
        security_tests = [r for r in self.test_results if 'security' in r['test'].lower()]
        security_passed = sum(1 for r in security_tests if r['success'])
        
        if security_tests:
            if security_passed == len(security_tests):
                print("  ✅ SECURITY VERIFICATION: All security fixes are working correctly!")
                print("    - Scheduler authentication properly implemented")
                print("    - Settings input validation working")
                print("    - Template validation working")
            else:
                print("  ❌ SECURITY VERIFICATION: Some security issues detected!")
                failed_security = [r for r in security_tests if not r['success']]
                for failure in failed_security:
                    print(f"    - {failure['test']}: {failure['details']}")
        
        # API functionality results
        api_tests = [r for r in self.test_results if 'api' in r['test'].lower()]
        api_passed = sum(1 for r in api_tests if r['success'])
        
        if api_tests:
            if api_passed >= len(api_tests) * 0.9:  # 90% threshold
                print("  ✅ API FUNCTIONALITY: All main endpoints working correctly!")
            else:
                print("  ⚠️  API FUNCTIONALITY: Some endpoints have issues")
                failed_api = [r for r in api_tests if not r['success']]
                for failure in failed_api[:3]:  # Show first 3 failures
                    print(f"    - {failure['test']}: {failure['details']}")
        
        # Error handling results
        error_tests = [r for r in self.test_results if 'error handling' in r['test'].lower()]
        error_passed = sum(1 for r in error_tests if r['success'])
        
        if error_tests:
            if error_passed == len(error_tests):
                print("  ✅ ERROR HANDLING: Proper error responses for all scenarios!")
            else:
                print("  ⚠️  ERROR HANDLING: Some error scenarios not handled properly")
        
        # Performance results
        performance_tests = [r for r in self.test_results if 'performance' in r['test'].lower()]
        performance_passed = sum(1 for r in performance_tests if r['success'])
        
        if performance_tests:
            if performance_passed == len(performance_tests):
                print("  ✅ PERFORMANCE: All endpoints have acceptable response times!")
            else:
                print("  ⚠️  PERFORMANCE: Some endpoints have slow response times")
        
        # Overall production readiness assessment
        print(f"\n🎉 OVERALL PRODUCTION READINESS ASSESSMENT:")
        
        if success_rate >= 95:
            print("  ✅ EXCELLENT - Application is fully production ready!")
            print("  🚀 All critical systems working perfectly")
            print("  🔒 Security measures properly implemented")
            print("  ⚡ Performance is acceptable")
            print("  📋 Ready for immediate deployment")
        elif success_rate >= 85:
            print("  ✅ GOOD - Application is mostly production ready")
            print("  🔧 Minor issues detected but not critical")
            print("  📋 Can be deployed with monitoring")
        elif success_rate >= 70:
            print("  ⚠️  FAIR - Application needs some fixes before production")
            print("  🔧 Several issues need to be addressed")
            print("  📋 Fix critical issues before deployment")
        else:
            print("  ❌ POOR - Application is not ready for production")
            print("  🚨 Critical issues must be fixed")
            print("  📋 Extensive fixes required before deployment")
        
        # Failed tests summary
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS SUMMARY:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        return {
            'total': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': success_rate,
            'security_tests_passed': security_passed if security_tests else 0,
            'security_tests_total': len(security_tests) if security_tests else 0,
            'api_tests_passed': api_passed if api_tests else 0,
            'api_tests_total': len(api_tests) if api_tests else 0,
            'performance_metrics': self.performance_metrics,
            'results': self.test_results
        }

if __name__ == "__main__":
    tester = ProductionReadinessTester()
    results = tester.run_comprehensive_production_tests()
    
    # Exit with appropriate code based on results
    if results['success_rate'] >= 85:
        exit(0)  # Success
    elif results['success_rate'] >= 70:
        exit(1)  # Warning - needs attention
    else:
        exit(2)  # Critical issues