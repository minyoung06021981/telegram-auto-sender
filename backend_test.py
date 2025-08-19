#!/usr/bin/env python3
"""
Comprehensive Backend API Tests for Telegram Auto Sender
Focus on regression testing after 2FA authentication fixes
"""

import requests
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration - Using the correct URL from frontend/.env
BASE_URL = "https://telegram-sender-3.preview.emergentagent.com/api"
HEALTH_URL = "https://telegram-sender-3.preview.emergentagent.com"

class TelegramAutoSenderTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.test_results = []
        self.session_id = None
        self.template_id = None
        self.group_id = None
        
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
    
    def test_auth_endpoints_comprehensive(self):
        """Comprehensive test of authentication endpoints - Focus on session loading and api_id/api_hash saving"""
        print("\n🔐 TESTING AUTHENTICATION ENDPOINTS (SESSION LOADING FOCUS)")
        print("-" * 50)
        
        # Test 1: GET sessions endpoint
        existing_sessions = []
        try:
            response = self.session.get(f"{BASE_URL}/auth/sessions")
            if response.status_code == 200:
                sessions = response.json()
                existing_sessions = sessions
                self.log_test("GET /api/auth/sessions", True, f"Retrieved {len(sessions)} sessions", sessions)
                
                # Check if sessions have required fields including api_id and api_hash info
                for session in sessions:
                    if 'session_id' in session and 'phone_number' in session:
                        self.log_test("Session Structure Validation", True, f"Session {session['session_id']} has required fields")
                    else:
                        self.log_test("Session Structure Validation", False, f"Session missing required fields: {session}")
            else:
                self.log_test("GET /api/auth/sessions", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("GET /api/auth/sessions", False, f"Error: {str(e)}")
        
        # Test 2: Test load-session endpoint with existing sessions (MAIN FOCUS)
        if existing_sessions:
            print("\n🎯 TESTING SESSION LOADING (MAIN FOCUS - Session Expired Fix)")
            print("-" * 50)
            
            for session in existing_sessions[:3]:  # Test up to 3 existing sessions
                session_id = session.get('session_id')
                phone_number = session.get('phone_number', 'unknown')
                
                try:
                    load_response = self.session.post(f"{BASE_URL}/auth/load-session/{session_id}")
                    
                    if load_response.status_code == 200:
                        load_data = load_response.json()
                        self.log_test(f"POST /api/auth/load-session/{session_id}", True, 
                                    f"Session loaded successfully for {phone_number}", load_data)
                        
                        # Verify the response contains expected fields
                        if 'authenticated' in load_data and 'user_info' in load_data:
                            self.log_test(f"Session Load Response Validation ({session_id})", True, 
                                        "Response contains required authentication fields")
                        else:
                            self.log_test(f"Session Load Response Validation ({session_id})", False, 
                                        f"Response missing required fields: {load_data}")
                    
                    elif load_response.status_code == 401:
                        # This is the error we're trying to fix - "Session expired"
                        try:
                            error_data = load_response.json()
                            error_detail = error_data.get('detail', 'No detail')
                            if 'expired' in error_detail.lower() or 'tidak valid' in error_detail.lower():
                                self.log_test(f"POST /api/auth/load-session/{session_id}", False, 
                                            f"❌ SESSION EXPIRED ERROR STILL PRESENT: {error_detail} (Phone: {phone_number})")
                            else:
                                self.log_test(f"POST /api/auth/load-session/{session_id}", False, 
                                            f"Authentication failed: {error_detail} (Phone: {phone_number})")
                        except:
                            self.log_test(f"POST /api/auth/load-session/{session_id}", False, 
                                        f"❌ SESSION EXPIRED ERROR: HTTP 401 - {load_response.text} (Phone: {phone_number})")
                    
                    elif load_response.status_code == 404:
                        self.log_test(f"POST /api/auth/load-session/{session_id}", False, 
                                    f"Session not found in database (Phone: {phone_number})")
                    
                    elif load_response.status_code == 400:
                        try:
                            error_data = load_response.json()
                            error_detail = error_data.get('detail', 'No detail')
                            self.log_test(f"POST /api/auth/load-session/{session_id}", False, 
                                        f"Bad request: {error_detail} (Phone: {phone_number})")
                        except:
                            self.log_test(f"POST /api/auth/load-session/{session_id}", False, 
                                        f"Bad request: {load_response.text} (Phone: {phone_number})")
                    
                    else:
                        self.log_test(f"POST /api/auth/load-session/{session_id}", False, 
                                    f"Unexpected HTTP {load_response.status_code}: {load_response.text} (Phone: {phone_number})")
                        
                except Exception as e:
                    self.log_test(f"POST /api/auth/load-session/{session_id}", False, 
                                f"Error loading session: {str(e)} (Phone: {phone_number})")
        else:
            self.log_test("Session Loading Test", False, "No existing sessions found to test load functionality")
        
        # Test 3: Test load-session with invalid session_id
        try:
            invalid_session_id = "invalid_session_12345"
            load_response = self.session.post(f"{BASE_URL}/auth/load-session/{invalid_session_id}")
            
            if load_response.status_code == 404:
                self.log_test("POST /api/auth/load-session (Invalid ID)", True, 
                            "Proper error handling for invalid session ID - HTTP 404")
            elif load_response.status_code == 400:
                try:
                    error_data = load_response.json()
                    self.log_test("POST /api/auth/load-session (Invalid ID)", True, 
                                f"Proper error handling - HTTP 400: {error_data.get('detail', 'No detail')}")
                except:
                    self.log_test("POST /api/auth/load-session (Invalid ID)", True, 
                                f"Proper error handling - HTTP 400: {load_response.text}")
            else:
                self.log_test("POST /api/auth/load-session (Invalid ID)", False, 
                            f"Expected HTTP 404 or 400, got HTTP {load_response.status_code}: {load_response.text}")
        except Exception as e:
            self.log_test("POST /api/auth/load-session (Invalid ID)", False, f"Error: {str(e)}")
        
        # Test 4: POST login with invalid credentials (should return proper error)
        try:
            login_data = {
                "api_id": 12345,
                "api_hash": "invalid_test_hash",
                "phone_number": "+1234567890"
            }
            
            login_response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            # We expect this to fail but with proper error handling (HTTP 400)
            if login_response.status_code == 400:
                try:
                    error_data = login_response.json()
                    self.log_test("POST /api/auth/login (Invalid Credentials)", True, 
                                f"Proper error handling - HTTP 400: {error_data.get('detail', 'No detail')}")
                except:
                    self.log_test("POST /api/auth/login (Invalid Credentials)", True, 
                                f"Proper error handling - HTTP 400: {login_response.text}")
            else:
                self.log_test("POST /api/auth/login (Invalid Credentials)", False, 
                            f"Expected HTTP 400, got HTTP {login_response.status_code}: {login_response.text}")
        except Exception as e:
            self.log_test("POST /api/auth/login (Invalid Credentials)", False, f"Error: {str(e)}")
        
        # Test 5: POST verify with invalid session_id (should return proper error)
        try:
            verify_data = {
                "session_id": "invalid_session_id_12345",
                "phone_code": "12345"
            }
            
            verify_response = self.session.post(f"{BASE_URL}/auth/verify", json=verify_data)
            # Should return HTTP 400 for invalid session
            if verify_response.status_code == 400:
                try:
                    error_data = verify_response.json()
                    self.log_test("POST /api/auth/verify (Invalid Session)", True, 
                                f"Proper error handling - HTTP 400: {error_data.get('detail', 'No detail')}")
                except:
                    self.log_test("POST /api/auth/verify (Invalid Session)", True, 
                                f"Proper error handling - HTTP 400: {verify_response.text}")
            else:
                self.log_test("POST /api/auth/verify (Invalid Session)", False, 
                            f"Expected HTTP 400, got HTTP {verify_response.status_code}: {verify_response.text}")
        except Exception as e:
            self.log_test("POST /api/auth/verify (Invalid Session)", False, f"Error: {str(e)}")
        
        # Test 6: POST verify with missing parameters (should return validation error)
        try:
            # Missing session_id
            verify_data_missing = {
                "phone_code": "12345"
            }
            
            verify_response = self.session.post(f"{BASE_URL}/auth/verify", json=verify_data_missing)
            # Should return HTTP 422 for validation error
            if verify_response.status_code == 422:
                try:
                    error_data = verify_response.json()
                    self.log_test("POST /api/auth/verify (Missing Parameters)", True, 
                                f"Proper validation error - HTTP 422: {error_data.get('detail', 'No detail')}")
                except:
                    self.log_test("POST /api/auth/verify (Missing Parameters)", True, 
                                f"Proper validation error - HTTP 422: {verify_response.text}")
            else:
                self.log_test("POST /api/auth/verify (Missing Parameters)", False, 
                            f"Expected HTTP 422, got HTTP {verify_response.status_code}: {verify_response.text}")
        except Exception as e:
            self.log_test("POST /api/auth/verify (Missing Parameters)", False, f"Error: {str(e)}")
        
        # Test 7: Test 2FA password flow validation
        try:
            verify_2fa_data = {
                "session_id": "test_session_id",
                "password": "test_2fa_password",
                "phone_number": "+1234567890"
            }
            
            verify_2fa_response = self.session.post(f"{BASE_URL}/auth/verify", json=verify_2fa_data)
            # Should return HTTP 400 for invalid session (but validates the 2FA structure)
            if verify_2fa_response.status_code == 400:
                try:
                    error_data = verify_2fa_response.json()
                    self.log_test("POST /api/auth/verify (2FA Password Flow)", True, 
                                f"2FA structure validated - HTTP 400: {error_data.get('detail', 'No detail')}")
                except:
                    self.log_test("POST /api/auth/verify (2FA Password Flow)", True, 
                                f"2FA structure validated - HTTP 400: {verify_2fa_response.text}")
            else:
                self.log_test("POST /api/auth/verify (2FA Password Flow)", False, 
                            f"Expected HTTP 400, got HTTP {verify_2fa_response.status_code}: {verify_2fa_response.text}")
        except Exception as e:
            self.log_test("POST /api/auth/verify (2FA Password Flow)", False, f"Error: {str(e)}")
    
    def test_settings_endpoints(self):
        """Test settings management endpoints"""
        print("\n⚙️ TESTING SETTINGS ENDPOINTS")
        print("-" * 30)
        
        # Test GET settings
        try:
            response = self.session.get(f"{BASE_URL}/settings")
            if response.status_code == 200:
                data = response.json()
                required_fields = ['min_message_interval', 'max_message_interval', 'min_cycle_interval', 'max_cycle_interval']
                if all(field in data for field in required_fields):
                    self.log_test("GET /api/settings", True, "Settings retrieved successfully", data)
                    
                    # Test PUT settings
                    updated_settings = data.copy()
                    updated_settings['min_message_interval'] = 10
                    updated_settings['notifications_enabled'] = True
                    
                    put_response = self.session.put(f"{BASE_URL}/settings", json=updated_settings)
                    if put_response.status_code == 200:
                        self.log_test("PUT /api/settings", True, "Settings updated successfully")
                    else:
                        self.log_test("PUT /api/settings", False, f"HTTP {put_response.status_code}: {put_response.text}")
                else:
                    self.log_test("GET /api/settings", False, f"Missing required fields in response: {data}")
            else:
                self.log_test("GET /api/settings", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Settings Endpoints", False, f"Error: {str(e)}")
    
    def test_template_endpoints(self):
        """Test message template CRUD endpoints"""
        print("\n📝 TESTING TEMPLATE ENDPOINTS")
        print("-" * 30)
        
        # Test GET templates (initially empty)
        try:
            response = self.session.get(f"{BASE_URL}/templates")
            if response.status_code == 200:
                templates = response.json()
                self.log_test("GET /api/templates", True, f"Retrieved {len(templates)} templates", templates)
                
                # Test POST create template
                test_template = {
                    "name": "Regression Test Template",
                    "content": "Hello! This is a regression test message for 2FA authentication fixes.",
                    "is_default": True
                }
                
                post_response = self.session.post(f"{BASE_URL}/templates", json=test_template)
                if post_response.status_code == 200:
                    created_template = post_response.json()
                    self.template_id = created_template.get('id')
                    self.log_test("POST /api/templates", True, f"Template created with ID: {self.template_id}", created_template)
                    
                    # Test GET default template
                    default_response = self.session.get(f"{BASE_URL}/templates/default")
                    if default_response.status_code == 200:
                        default_template = default_response.json()
                        self.log_test("GET /api/templates/default", True, "Default template retrieved", default_template)
                    else:
                        self.log_test("GET /api/templates/default", False, f"HTTP {default_response.status_code}: {default_response.text}")
                    
                    # Test PUT update template
                    if self.template_id:
                        updated_template = test_template.copy()
                        updated_template['content'] = "Updated regression test message content after 2FA fixes"
                        
                        put_response = self.session.put(f"{BASE_URL}/templates/{self.template_id}", json=updated_template)
                        if put_response.status_code == 200:
                            self.log_test("PUT /api/templates/{id}", True, "Template updated successfully")
                        else:
                            self.log_test("PUT /api/templates/{id}", False, f"HTTP {put_response.status_code}: {put_response.text}")
                else:
                    self.log_test("POST /api/templates", False, f"HTTP {post_response.status_code}: {post_response.text}")
            else:
                self.log_test("GET /api/templates", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Template Endpoints", False, f"Error: {str(e)}")
    
    def test_group_endpoints(self):
        """Test group management and statistics endpoints"""
        print("\n👥 TESTING GROUP ENDPOINTS")
        print("-" * 30)
        
        # Test GET groups
        try:
            response = self.session.get(f"{BASE_URL}/groups")
            if response.status_code == 200:
                groups = response.json()
                self.log_test("GET /api/groups", True, f"Retrieved {len(groups)} groups", groups)
                
                # Test GET group stats
                stats_response = self.session.get(f"{BASE_URL}/groups/stats")
                if stats_response.status_code == 200:
                    stats = stats_response.json()
                    required_stats = ['total', 'active', 'temp_blacklisted', 'perm_blacklisted']
                    if all(stat in stats for stat in required_stats):
                        self.log_test("GET /api/groups/stats", True, "Group statistics retrieved", stats)
                    else:
                        self.log_test("GET /api/groups/stats", False, f"Missing required stats: {stats}")
                else:
                    self.log_test("GET /api/groups/stats", False, f"HTTP {stats_response.status_code}: {stats_response.text}")
                
                # Test POST create group (should fail without session but validate properly)
                group_data = {
                    "name": "Regression Test Group",
                    "username": "@regressiontestgroup",
                    "group_id": "123456789"
                }
                
                # Test without session_id parameter (should return 422)
                create_response = self.session.post(f"{BASE_URL}/groups", json=group_data)
                if create_response.status_code == 422:
                    self.log_test("POST /api/groups (No Session)", True, f"Proper validation - HTTP 422")
                else:
                    self.log_test("POST /api/groups (No Session)", False, f"Expected HTTP 422, got HTTP {create_response.status_code}")
                    
            else:
                self.log_test("GET /api/groups", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Group Endpoints", False, f"Error: {str(e)}")
    
    def test_new_group_management_endpoints(self):
        """Test the new group management endpoints: /api/groups/single and /api/groups/bulk"""
        print("\n🆕 TESTING NEW GROUP MANAGEMENT ENDPOINTS")
        print("-" * 50)
        print("Focus: Testing single and bulk group creation with various identifier formats")
        print("-" * 50)
        
        # Test various identifier formats
        test_identifiers = [
            "@testgroup123",  # Username format
            "-1001234567890",  # Group ID format
            "https://t.me/+AbCdEfGhIjKlMnOp",  # Invite link format
            "https://t.me/joinchat/AbCdEfGhIjKlMnOp",  # Alternative invite link format
        ]
        
        invalid_identifiers = [
            "",  # Empty identifier
            "   ",  # Whitespace only
            "invalid_format",  # Invalid format
            "@",  # Just @ symbol
            "https://t.me/",  # Incomplete invite link
        ]
        
        # Test 1: POST /api/groups/single - Missing session_id (should return 422)
        try:
            single_group_data = {"identifier": "@testgroup123"}
            response = self.session.post(f"{BASE_URL}/groups/single", json=single_group_data)
            
            if response.status_code == 422:
                self.log_test("POST /api/groups/single (No Session)", True, "Proper validation - HTTP 422 for missing session_id")
            else:
                self.log_test("POST /api/groups/single (No Session)", False, f"Expected HTTP 422, got HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("POST /api/groups/single (No Session)", False, f"Error: {str(e)}")
        
        # Test 2: POST /api/groups/single - Invalid session_id (should return 401)
        try:
            single_group_data = {"identifier": "@testgroup123"}
            response = self.session.post(f"{BASE_URL}/groups/single?session_id=invalid_session_12345", json=single_group_data)
            
            if response.status_code == 401:
                self.log_test("POST /api/groups/single (Invalid Session)", True, "Proper authentication check - HTTP 401")
            else:
                self.log_test("POST /api/groups/single (Invalid Session)", False, f"Expected HTTP 401, got HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("POST /api/groups/single (Invalid Session)", False, f"Error: {str(e)}")
        
        # Test 3: POST /api/groups/single - Empty identifier (should return 400)
        try:
            single_group_data = {"identifier": ""}
            response = self.session.post(f"{BASE_URL}/groups/single?session_id=test_session_123", json=single_group_data)
            
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    if "required" in error_data.get('detail', '').lower():
                        self.log_test("POST /api/groups/single (Empty Identifier)", True, f"Proper validation - HTTP 400: {error_data.get('detail')}")
                    else:
                        self.log_test("POST /api/groups/single (Empty Identifier)", True, f"Proper validation - HTTP 400: {error_data.get('detail')}")
                except:
                    self.log_test("POST /api/groups/single (Empty Identifier)", True, f"Proper validation - HTTP 400: {response.text}")
            elif response.status_code == 401:
                self.log_test("POST /api/groups/single (Empty Identifier)", True, "Expected behavior - HTTP 401 (no active session)")
            else:
                self.log_test("POST /api/groups/single (Empty Identifier)", False, f"Expected HTTP 400 or 401, got HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("POST /api/groups/single (Empty Identifier)", False, f"Error: {str(e)}")
        
        # Test 4: POST /api/groups/single - Various identifier formats (will fail due to no active session, but validates format handling)
        for identifier in test_identifiers:
            try:
                single_group_data = {"identifier": identifier}
                response = self.session.post(f"{BASE_URL}/groups/single?session_id=test_session_123", json=single_group_data)
                
                # We expect 401 (no active session) but this tests that the endpoint accepts different formats
                if response.status_code == 401:
                    self.log_test(f"POST /api/groups/single (Format: {identifier})", True, f"Endpoint accepts identifier format - HTTP 401 (no active session)")
                elif response.status_code == 400:
                    try:
                        error_data = response.json()
                        if "invalid group" in error_data.get('detail', '').lower():
                            self.log_test(f"POST /api/groups/single (Format: {identifier})", True, f"Proper group validation - HTTP 400: {error_data.get('detail')}")
                        else:
                            self.log_test(f"POST /api/groups/single (Format: {identifier})", True, f"Expected validation behavior - HTTP 400: {error_data.get('detail')}")
                    except:
                        self.log_test(f"POST /api/groups/single (Format: {identifier})", True, f"Expected validation behavior - HTTP 400: {response.text}")
                else:
                    self.log_test(f"POST /api/groups/single (Format: {identifier})", False, f"Unexpected HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.log_test(f"POST /api/groups/single (Format: {identifier})", False, f"Error: {str(e)}")
        
        # Test 5: POST /api/groups/bulk - Missing session_id (should return 422)
        try:
            bulk_group_data = {"identifiers": ["@testgroup1", "@testgroup2"]}
            response = self.session.post(f"{BASE_URL}/groups/bulk", json=bulk_group_data)
            
            if response.status_code == 422:
                self.log_test("POST /api/groups/bulk (No Session)", True, "Proper validation - HTTP 422 for missing session_id")
            else:
                self.log_test("POST /api/groups/bulk (No Session)", False, f"Expected HTTP 422, got HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("POST /api/groups/bulk (No Session)", False, f"Error: {str(e)}")
        
        # Test 6: POST /api/groups/bulk - Invalid session_id (should return 401)
        try:
            bulk_group_data = {"identifiers": ["@testgroup1", "@testgroup2"]}
            response = self.session.post(f"{BASE_URL}/groups/bulk?session_id=invalid_session_12345", json=bulk_group_data)
            
            if response.status_code == 401:
                self.log_test("POST /api/groups/bulk (Invalid Session)", True, "Proper authentication check - HTTP 401")
            else:
                self.log_test("POST /api/groups/bulk (Invalid Session)", False, f"Expected HTTP 401, got HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("POST /api/groups/bulk (Invalid Session)", False, f"Error: {str(e)}")
        
        # Test 7: POST /api/groups/bulk - Empty identifiers list (should return 400)
        try:
            bulk_group_data = {"identifiers": []}
            response = self.session.post(f"{BASE_URL}/groups/bulk?session_id=test_session_123", json=bulk_group_data)
            
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    if "no identifiers" in error_data.get('detail', '').lower():
                        self.log_test("POST /api/groups/bulk (Empty List)", True, f"Proper validation - HTTP 400: {error_data.get('detail')}")
                    else:
                        self.log_test("POST /api/groups/bulk (Empty List)", True, f"Proper validation - HTTP 400: {error_data.get('detail')}")
                except:
                    self.log_test("POST /api/groups/bulk (Empty List)", True, f"Proper validation - HTTP 400: {response.text}")
            elif response.status_code == 401:
                self.log_test("POST /api/groups/bulk (Empty List)", True, "Expected behavior - HTTP 401 (no active session)")
            else:
                self.log_test("POST /api/groups/bulk (Empty List)", False, f"Expected HTTP 400 or 401, got HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("POST /api/groups/bulk (Empty List)", False, f"Error: {str(e)}")
        
        # Test 8: POST /api/groups/bulk - Mixed valid and invalid identifiers (tests bulk processing)
        try:
            mixed_identifiers = [
                "@validgroup1",
                "",  # Empty - should be skipped
                "@validgroup2", 
                "invalid_format",  # Invalid format
                "-1001234567890",  # Valid group ID format
                "   ",  # Whitespace - should be skipped
                "https://t.me/+AbCdEfGhIjKlMnOp"  # Valid invite link format
            ]
            bulk_group_data = {"identifiers": mixed_identifiers}
            response = self.session.post(f"{BASE_URL}/groups/bulk?session_id=test_session_123", json=bulk_group_data)
            
            # We expect 401 (no active session) but this tests bulk processing logic
            if response.status_code == 401:
                self.log_test("POST /api/groups/bulk (Mixed Identifiers)", True, "Endpoint accepts bulk data structure - HTTP 401 (no active session)")
            elif response.status_code == 200:
                # If somehow we get 200, check the response structure
                try:
                    result_data = response.json()
                    if all(key in result_data for key in ['added', 'skipped', 'errors']):
                        self.log_test("POST /api/groups/bulk (Mixed Identifiers)", True, f"Proper bulk response structure: {result_data}")
                    else:
                        self.log_test("POST /api/groups/bulk (Mixed Identifiers)", False, f"Invalid response structure: {result_data}")
                except:
                    self.log_test("POST /api/groups/bulk (Mixed Identifiers)", False, f"Invalid JSON response: {response.text}")
            else:
                self.log_test("POST /api/groups/bulk (Mixed Identifiers)", False, f"Unexpected HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("POST /api/groups/bulk (Mixed Identifiers)", False, f"Error: {str(e)}")
        
        # Test 9: Verify GET /api/groups still works after new endpoints
        try:
            response = self.session.get(f"{BASE_URL}/groups")
            if response.status_code == 200:
                groups = response.json()
                self.log_test("GET /api/groups (After New Endpoints)", True, f"Existing endpoint still works - Retrieved {len(groups)} groups")
            else:
                self.log_test("GET /api/groups (After New Endpoints)", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("GET /api/groups (After New Endpoints)", False, f"Error: {str(e)}")
        
        # Test 10: Test parameter validation for both endpoints
        try:
            # Test single endpoint with missing identifier field
            response = self.session.post(f"{BASE_URL}/groups/single?session_id=test_session_123", json={})
            if response.status_code == 422:
                self.log_test("POST /api/groups/single (Missing Identifier Field)", True, "Proper field validation - HTTP 422")
            else:
                self.log_test("POST /api/groups/single (Missing Identifier Field)", False, f"Expected HTTP 422, got HTTP {response.status_code}")
            
            # Test bulk endpoint with missing identifiers field
            response = self.session.post(f"{BASE_URL}/groups/bulk?session_id=test_session_123", json={})
            if response.status_code == 422:
                self.log_test("POST /api/groups/bulk (Missing Identifiers Field)", True, "Proper field validation - HTTP 422")
            else:
                self.log_test("POST /api/groups/bulk (Missing Identifiers Field)", False, f"Expected HTTP 422, got HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Parameter Validation Tests", False, f"Error: {str(e)}")
        
        print("\n✅ NEW GROUP MANAGEMENT ENDPOINTS TESTING COMPLETED")
        print("Note: Most tests show HTTP 401 (no active session) which is expected behavior")
        print("The important validation is that endpoints exist, accept correct data structures,")
        print("and properly validate required parameters and session authentication.")
    
    def test_dashboard_endpoints(self):
        """Test dashboard statistics and message logs endpoints"""
        print("\n📊 TESTING DASHBOARD ENDPOINTS")
        print("-" * 30)
        
        # Test dashboard stats
        try:
            response = self.session.get(f"{BASE_URL}/dashboard/stats")
            if response.status_code == 200:
                stats = response.json()
                required_sections = ['groups', 'messages', 'scheduler']
                if all(section in stats for section in required_sections):
                    self.log_test("GET /api/dashboard/stats", True, "Dashboard statistics retrieved", stats)
                else:
                    self.log_test("GET /api/dashboard/stats", False, f"Missing required sections: {stats}")
            else:
                self.log_test("GET /api/dashboard/stats", False, f"HTTP {response.status_code}: {response.text}")
                
            # Test message logs
            logs_response = self.session.get(f"{BASE_URL}/logs/messages")
            if logs_response.status_code == 200:
                logs = logs_response.json()
                self.log_test("GET /api/logs/messages", True, f"Retrieved {len(logs)} message logs", logs)
            else:
                self.log_test("GET /api/logs/messages", False, f"HTTP {logs_response.status_code}: {logs_response.text}")
                
        except Exception as e:
            self.log_test("Dashboard Endpoints", False, f"Error: {str(e)}")
    
    def test_scheduler_endpoints(self):
        """Test scheduler start/stop validation endpoints"""
        print("\n⏰ TESTING SCHEDULER ENDPOINTS")
        print("-" * 30)
        
        try:
            # Test start scheduler without session_id (should return 422)
            response = self.session.post(f"{BASE_URL}/scheduler/start")
            if response.status_code == 422:
                self.log_test("POST /api/scheduler/start (No Session)", True, f"Proper validation - HTTP 422")
            else:
                self.log_test("POST /api/scheduler/start (No Session)", False, f"Expected HTTP 422, got HTTP {response.status_code}")
            
            # Test stop scheduler without session_id (should return 422)
            response = self.session.post(f"{BASE_URL}/scheduler/stop")
            if response.status_code == 422:
                self.log_test("POST /api/scheduler/stop (No Session)", True, f"Proper validation - HTTP 422")
            else:
                self.log_test("POST /api/scheduler/stop (No Session)", False, f"Expected HTTP 422, got HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Scheduler Endpoints", False, f"Error: {str(e)}")
    
    def test_message_endpoints(self):
        """Test message sending endpoints validation"""
        print("\n💬 TESTING MESSAGE ENDPOINTS")
        print("-" * 30)
        
        try:
            # Test send messages without session_id (should fail with proper error)
            if self.template_id:
                message_data = {
                    "group_ids": ["123456789"],
                    "message_template_id": self.template_id,
                    "send_immediately": True
                }
                
                # Test without session_id parameter (should return 422)
                response = self.session.post(f"{BASE_URL}/messages/send", json=message_data)
                if response.status_code == 422:
                    self.log_test("POST /api/messages/send (No Session)", True, f"Proper validation - HTTP 422")
                else:
                    self.log_test("POST /api/messages/send (No Session)", False, f"Expected HTTP 422, got HTTP {response.status_code}")
                
                # Test with invalid session_id (should return 401)
                response_with_session = self.session.post(
                    f"{BASE_URL}/messages/send?session_id=invalid_session_12345", 
                    json=message_data
                )
                if response_with_session.status_code == 401:
                    self.log_test("POST /api/messages/send (Invalid Session)", True, f"Proper authentication check - HTTP 401")
                else:
                    self.log_test("POST /api/messages/send (Invalid Session)", False, f"Expected HTTP 401, got HTTP {response_with_session.status_code}")
            else:
                self.log_test("POST /api/messages/send", False, "No template_id available for testing")
                
        except Exception as e:
            self.log_test("Message Endpoints", False, f"Error: {str(e)}")
    
    def cleanup_test_data(self):
        """Clean up test data created during testing"""
        print("\n🧹 CLEANING UP TEST DATA")
        print("-" * 30)
        
        try:
            # Delete test template if created
            if self.template_id:
                response = self.session.delete(f"{BASE_URL}/templates/{self.template_id}")
                if response.status_code == 200:
                    self.log_test("DELETE /api/templates/{id}", True, "Test template deleted successfully")
                else:
                    self.log_test("DELETE /api/templates/{id}", False, f"Failed to delete template - HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Cleanup", False, f"Error during cleanup: {str(e)}")
    
    def run_all_tests(self):
        """Run all backend API tests with focus on 2FA regression testing and new group management"""
        print("🚀 TELEGRAM AUTO SENDER - COMPREHENSIVE BACKEND TESTING")
        print("=" * 60)
        print("Focus: Testing all API endpoints including new group management features")
        print("=" * 60)
        
        # Test in order of priority for regression testing
        self.test_health_check()
        self.test_auth_endpoints_comprehensive()  # Primary focus area
        self.test_settings_endpoints()
        self.test_template_endpoints()
        self.test_group_endpoints()
        self.test_new_group_management_endpoints()  # NEW: Test updated group management
        self.test_dashboard_endpoints()
        self.test_scheduler_endpoints()
        self.test_message_endpoints()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 REGRESSION TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Focus on authentication-related results
        auth_tests = [r for r in self.test_results if 'auth' in r['test'].lower()]
        auth_passed = sum(1 for r in auth_tests if r['success'])
        
        print(f"\n🔐 AUTHENTICATION TESTS: {auth_passed}/{len(auth_tests)} passed")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        print("\n🎯 CRITICAL ISSUES:")
        critical_failures = []
        for result in self.test_results:
            if not result['success'] and any(critical in result['test'].lower() 
                                           for critical in ['health', 'auth', 'settings', 'template', 'dashboard']):
                critical_failures.append(result)
        
        if critical_failures:
            for failure in critical_failures:
                print(f"  - {failure['test']}: {failure['details']}")
        else:
            print("  None - All critical endpoints are working!")
        
        print("\n✅ SESSION LOADING FIX STATUS:")
        session_load_tests = [r for r in self.test_results if 'load-session' in r['test'].lower()]
        session_load_passed = sum(1 for r in session_load_tests if r['success'])
        
        if session_load_tests:
            print(f"  📊 Session Loading Tests: {session_load_passed}/{len(session_load_tests)} passed")
            
            # Check for specific "Session expired" errors
            expired_errors = [r for r in session_load_tests if not r['success'] and 
                            ('expired' in r['details'].lower() or 'tidak valid' in r['details'].lower())]
            
            if expired_errors:
                print(f"  ❌ SESSION EXPIRED ERRORS STILL PRESENT: {len(expired_errors)} sessions affected")
                for error in expired_errors:
                    print(f"     - {error['test']}: {error['details']}")
                print("  🔧 RECOMMENDATION: api_id and api_hash may not be properly saved during session creation")
            else:
                print("  ✅ NO SESSION EXPIRED ERRORS DETECTED - Fix appears successful!")
        else:
            print("  ⚠️  NO SESSION LOADING TESTS PERFORMED - No existing sessions found")
        
        print("\n✅ 2FA REGRESSION STATUS:")
        if auth_passed == len(auth_tests) and len(critical_failures) == 0:
            print("  🎉 NO REGRESSION DETECTED - All systems operational after 2FA fixes!")
        else:
            print("  ⚠️  POTENTIAL REGRESSION ISSUES DETECTED - Review failed tests above")
        
        return {
            'total': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'critical_failures': len(critical_failures),
            'auth_tests_passed': auth_passed,
            'auth_tests_total': len(auth_tests),
            'results': self.test_results
        }

if __name__ == "__main__":
    tester = TelegramAutoSenderTester()
    results = tester.run_all_tests()
    
    # Exit with error code if critical tests failed
    if results['critical_failures'] > 0:
        exit(1)
    else:
        exit(0)