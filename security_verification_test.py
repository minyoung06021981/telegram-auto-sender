#!/usr/bin/env python3
"""
CRITICAL SECURITY FIXES VERIFICATION TESTING
Focus: Verify that all critical security issues found in previous testing have been properly fixed
"""

import requests
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration - Using the correct URL from frontend/.env
BASE_URL = "https://stack-upgrade.preview.emergentagent.com/api"

class SecurityVerificationTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.test_results = []
        
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

    def test_scheduler_authentication_fixes(self):
        """CRITICAL: Test that scheduler endpoints now require valid session authentication"""
        print("\n🔒 TESTING SCHEDULER AUTHENTICATION FIXES (CRITICAL)")
        print("=" * 60)
        print("Verifying that authentication bypass vulnerability has been fixed")
        print("=" * 60)
        
        # Test 1: POST /api/scheduler/start with invalid session_id → should return HTTP 401
        try:
            invalid_session_id = "invalid_session_12345"
            response = self.session.post(f"{BASE_URL}/scheduler/start?session_id={invalid_session_id}")
            
            if response.status_code == 401:
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', '')
                    if 'session' in error_detail.lower() or 'expired' in error_detail.lower():
                        self.log_test("Scheduler Start - Invalid Session Auth", True, 
                                    f"✅ SECURITY FIX VERIFIED: HTTP 401 - {error_detail}")
                    else:
                        self.log_test("Scheduler Start - Invalid Session Auth", True, 
                                    f"✅ SECURITY FIX VERIFIED: HTTP 401 - {error_detail}")
                except:
                    self.log_test("Scheduler Start - Invalid Session Auth", True, 
                                f"✅ SECURITY FIX VERIFIED: HTTP 401 - {response.text}")
            else:
                self.log_test("Scheduler Start - Invalid Session Auth", False, 
                            f"🚨 SECURITY VULNERABILITY STILL EXISTS: Expected HTTP 401, got HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Scheduler Start - Invalid Session Auth", False, f"Error: {str(e)}")
        
        # Test 2: POST /api/scheduler/stop with invalid session_id → should return HTTP 401
        try:
            invalid_session_id = "invalid_session_67890"
            response = self.session.post(f"{BASE_URL}/scheduler/stop?session_id={invalid_session_id}")
            
            if response.status_code == 401:
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', '')
                    if 'session' in error_detail.lower() or 'expired' in error_detail.lower():
                        self.log_test("Scheduler Stop - Invalid Session Auth", True, 
                                    f"✅ SECURITY FIX VERIFIED: HTTP 401 - {error_detail}")
                    else:
                        self.log_test("Scheduler Stop - Invalid Session Auth", True, 
                                    f"✅ SECURITY FIX VERIFIED: HTTP 401 - {error_detail}")
                except:
                    self.log_test("Scheduler Stop - Invalid Session Auth", True, 
                                f"✅ SECURITY FIX VERIFIED: HTTP 401 - {response.text}")
            else:
                self.log_test("Scheduler Stop - Invalid Session Auth", False, 
                            f"🚨 SECURITY VULNERABILITY STILL EXISTS: Expected HTTP 401, got HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Scheduler Stop - Invalid Session Auth", False, f"Error: {str(e)}")
        
        # Test 3: POST /api/scheduler/start without session_id → should return HTTP 422
        try:
            response = self.session.post(f"{BASE_URL}/scheduler/start")
            
            if response.status_code == 422:
                try:
                    error_data = response.json()
                    self.log_test("Scheduler Start - Missing Session Param", True, 
                                f"✅ PARAMETER VALIDATION WORKING: HTTP 422 - {error_data.get('detail', 'Validation error')}")
                except:
                    self.log_test("Scheduler Start - Missing Session Param", True, 
                                f"✅ PARAMETER VALIDATION WORKING: HTTP 422 - {response.text}")
            else:
                self.log_test("Scheduler Start - Missing Session Param", False, 
                            f"Expected HTTP 422, got HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Scheduler Start - Missing Session Param", False, f"Error: {str(e)}")
        
        # Test 4: POST /api/scheduler/stop without session_id → should return HTTP 422
        try:
            response = self.session.post(f"{BASE_URL}/scheduler/stop")
            
            if response.status_code == 422:
                try:
                    error_data = response.json()
                    self.log_test("Scheduler Stop - Missing Session Param", True, 
                                f"✅ PARAMETER VALIDATION WORKING: HTTP 422 - {error_data.get('detail', 'Validation error')}")
                except:
                    self.log_test("Scheduler Stop - Missing Session Param", True, 
                                f"✅ PARAMETER VALIDATION WORKING: HTTP 422 - {response.text}")
            else:
                self.log_test("Scheduler Stop - Missing Session Param", False, 
                            f"Expected HTTP 422, got HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Scheduler Stop - Missing Session Param", False, f"Error: {str(e)}")

    def test_settings_validation_fixes(self):
        """Test that settings validation now properly rejects invalid data"""
        print("\n⚙️ TESTING SETTINGS VALIDATION FIXES")
        print("=" * 50)
        print("Verifying that invalid settings data is properly rejected")
        print("=" * 50)
        
        # Test 1: PUT /api/settings with negative intervals → should return HTTP 400
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
            
            response = self.session.put(f"{BASE_URL}/settings", json=invalid_settings)
            
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', '')
                    if 'positive' in error_detail.lower() or 'negative' in error_detail.lower():
                        self.log_test("Settings - Negative Intervals Validation", True, 
                                    f"✅ VALIDATION FIX VERIFIED: HTTP 400 - {error_detail}")
                    else:
                        self.log_test("Settings - Negative Intervals Validation", True, 
                                    f"✅ VALIDATION FIX VERIFIED: HTTP 400 - {error_detail}")
                except:
                    self.log_test("Settings - Negative Intervals Validation", True, 
                                f"✅ VALIDATION FIX VERIFIED: HTTP 400 - {response.text}")
            else:
                self.log_test("Settings - Negative Intervals Validation", False, 
                            f"🚨 VALIDATION BYPASS STILL EXISTS: Expected HTTP 400, got HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Settings - Negative Intervals Validation", False, f"Error: {str(e)}")
        
        # Test 2: PUT /api/settings with min >= max intervals → should return HTTP 400
        try:
            invalid_settings = {
                "min_message_interval": 30,
                "max_message_interval": 20,  # min > max
                "min_cycle_interval": 120,
                "max_cycle_interval": 60,    # min > max
                "max_retry_attempts": 3,
                "is_scheduler_active": False,
                "theme": "auto",
                "notifications_enabled": True
            }
            
            response = self.session.put(f"{BASE_URL}/settings", json=invalid_settings)
            
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', '')
                    if 'less than' in error_detail.lower() or 'greater than' in error_detail.lower():
                        self.log_test("Settings - Min/Max Logic Validation", True, 
                                    f"✅ VALIDATION FIX VERIFIED: HTTP 400 - {error_detail}")
                    else:
                        self.log_test("Settings - Min/Max Logic Validation", True, 
                                    f"✅ VALIDATION FIX VERIFIED: HTTP 400 - {error_detail}")
                except:
                    self.log_test("Settings - Min/Max Logic Validation", True, 
                                f"✅ VALIDATION FIX VERIFIED: HTTP 400 - {response.text}")
            else:
                self.log_test("Settings - Min/Max Logic Validation", False, 
                            f"🚨 VALIDATION BYPASS STILL EXISTS: Expected HTTP 400, got HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Settings - Min/Max Logic Validation", False, f"Error: {str(e)}")
        
        # Test 3: PUT /api/settings with valid data → should work normally
        try:
            valid_settings = {
                "min_message_interval": 20,
                "max_message_interval": 30,
                "min_cycle_interval": 60,
                "max_cycle_interval": 120,
                "max_retry_attempts": 3,
                "is_scheduler_active": False,
                "theme": "auto",
                "notifications_enabled": True
            }
            
            response = self.session.put(f"{BASE_URL}/settings", json=valid_settings)
            
            if response.status_code == 200:
                try:
                    success_data = response.json()
                    self.log_test("Settings - Valid Data Update", True, 
                                f"✅ VALID SETTINGS ACCEPTED: HTTP 200 - {success_data.get('message', 'Success')}")
                except:
                    self.log_test("Settings - Valid Data Update", True, 
                                f"✅ VALID SETTINGS ACCEPTED: HTTP 200 - {response.text}")
            else:
                self.log_test("Settings - Valid Data Update", False, 
                            f"Valid settings rejected: HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Settings - Valid Data Update", False, f"Error: {str(e)}")

    def test_template_validation_fixes(self):
        """Test that template validation now properly rejects empty/whitespace names and content"""
        print("\n📝 TESTING TEMPLATE VALIDATION FIXES")
        print("=" * 50)
        print("Verifying that empty/whitespace template data is properly rejected")
        print("=" * 50)
        
        # Test 1: POST /api/templates with empty name → should return HTTP 400
        try:
            invalid_template = {
                "name": "",
                "content": "Valid content here",
                "is_default": False
            }
            
            response = self.session.post(f"{BASE_URL}/templates", json=invalid_template)
            
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', '')
                    if 'empty' in error_detail.lower() or 'name' in error_detail.lower():
                        self.log_test("Template - Empty Name Validation", True, 
                                    f"✅ VALIDATION FIX VERIFIED: HTTP 400 - {error_detail}")
                    else:
                        self.log_test("Template - Empty Name Validation", True, 
                                    f"✅ VALIDATION FIX VERIFIED: HTTP 400 - {error_detail}")
                except:
                    self.log_test("Template - Empty Name Validation", True, 
                                f"✅ VALIDATION FIX VERIFIED: HTTP 400 - {response.text}")
            else:
                self.log_test("Template - Empty Name Validation", False, 
                            f"🚨 VALIDATION BYPASS STILL EXISTS: Expected HTTP 400, got HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Template - Empty Name Validation", False, f"Error: {str(e)}")
        
        # Test 2: POST /api/templates with whitespace-only name → should return HTTP 400
        try:
            invalid_template = {
                "name": "   \t\n   ",  # Only whitespace
                "content": "Valid content here",
                "is_default": False
            }
            
            response = self.session.post(f"{BASE_URL}/templates", json=invalid_template)
            
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', '')
                    if 'whitespace' in error_detail.lower() or 'empty' in error_detail.lower():
                        self.log_test("Template - Whitespace Name Validation", True, 
                                    f"✅ VALIDATION FIX VERIFIED: HTTP 400 - {error_detail}")
                    else:
                        self.log_test("Template - Whitespace Name Validation", True, 
                                    f"✅ VALIDATION FIX VERIFIED: HTTP 400 - {error_detail}")
                except:
                    self.log_test("Template - Whitespace Name Validation", True, 
                                f"✅ VALIDATION FIX VERIFIED: HTTP 400 - {response.text}")
            else:
                self.log_test("Template - Whitespace Name Validation", False, 
                            f"🚨 VALIDATION BYPASS STILL EXISTS: Expected HTTP 400, got HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Template - Whitespace Name Validation", False, f"Error: {str(e)}")
        
        # Test 3: PUT /api/templates/{id} with empty content → should return HTTP 400
        try:
            # First create a valid template to get an ID
            valid_template = {
                "name": "Security Test Template",
                "content": "Initial content",
                "is_default": False
            }
            
            create_response = self.session.post(f"{BASE_URL}/templates", json=valid_template)
            template_id = None
            
            if create_response.status_code == 200:
                try:
                    template_data = create_response.json()
                    template_id = template_data.get('id')
                except:
                    pass
            
            if template_id:
                # Now try to update with empty content
                invalid_update = {
                    "name": "Valid Name",
                    "content": "",  # Empty content
                    "is_default": False
                }
                
                response = self.session.put(f"{BASE_URL}/templates/{template_id}", json=invalid_update)
                
                if response.status_code == 400:
                    try:
                        error_data = response.json()
                        error_detail = error_data.get('detail', '')
                        if 'content' in error_detail.lower() or 'empty' in error_detail.lower():
                            self.log_test("Template - Empty Content Validation", True, 
                                        f"✅ VALIDATION FIX VERIFIED: HTTP 400 - {error_detail}")
                        else:
                            self.log_test("Template - Empty Content Validation", True, 
                                        f"✅ VALIDATION FIX VERIFIED: HTTP 400 - {error_detail}")
                    except:
                        self.log_test("Template - Empty Content Validation", True, 
                                    f"✅ VALIDATION FIX VERIFIED: HTTP 400 - {response.text}")
                else:
                    self.log_test("Template - Empty Content Validation", False, 
                                f"🚨 VALIDATION BYPASS STILL EXISTS: Expected HTTP 400, got HTTP {response.status_code}: {response.text}")
                
                # Cleanup: Delete the test template
                try:
                    self.session.delete(f"{BASE_URL}/templates/{template_id}")
                except:
                    pass
            else:
                self.log_test("Template - Empty Content Validation", False, 
                            "Could not create test template to test content validation")
                
        except Exception as e:
            self.log_test("Template - Empty Content Validation", False, f"Error: {str(e)}")
        
        # Test 4: POST /api/templates with valid data → should work normally
        try:
            valid_template = {
                "name": "Valid Security Test Template",
                "content": "This is valid template content for security testing",
                "is_default": False
            }
            
            response = self.session.post(f"{BASE_URL}/templates", json=valid_template)
            
            if response.status_code == 200:
                try:
                    template_data = response.json()
                    template_id = template_data.get('id')
                    self.log_test("Template - Valid Data Creation", True, 
                                f"✅ VALID TEMPLATE ACCEPTED: HTTP 200 - ID: {template_id}")
                    
                    # Cleanup: Delete the test template
                    if template_id:
                        try:
                            self.session.delete(f"{BASE_URL}/templates/{template_id}")
                        except:
                            pass
                except:
                    self.log_test("Template - Valid Data Creation", True, 
                                f"✅ VALID TEMPLATE ACCEPTED: HTTP 200 - {response.text}")
            else:
                self.log_test("Template - Valid Data Creation", False, 
                            f"Valid template rejected: HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Template - Valid Data Creation", False, f"Error: {str(e)}")

    def test_regression_endpoints(self):
        """Test that existing functionality still works after security fixes"""
        print("\n🔄 TESTING REGRESSION - EXISTING FUNCTIONALITY")
        print("=" * 50)
        print("Verifying that security fixes didn't break existing functionality")
        print("=" * 50)
        
        # Test 1: GET /api/settings still works
        try:
            response = self.session.get(f"{BASE_URL}/settings")
            if response.status_code == 200:
                data = response.json()
                required_fields = ['min_message_interval', 'max_message_interval']
                if all(field in data for field in required_fields):
                    self.log_test("Regression - GET Settings", True, 
                                f"✅ Settings endpoint working: {len(data)} fields returned")
                else:
                    self.log_test("Regression - GET Settings", False, 
                                f"Settings response missing required fields: {data}")
            else:
                self.log_test("Regression - GET Settings", False, 
                            f"Settings endpoint broken: HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Regression - GET Settings", False, f"Error: {str(e)}")
        
        # Test 2: GET /api/templates still works
        try:
            response = self.session.get(f"{BASE_URL}/templates")
            if response.status_code == 200:
                templates = response.json()
                self.log_test("Regression - GET Templates", True, 
                            f"✅ Templates endpoint working: {len(templates)} templates returned")
            else:
                self.log_test("Regression - GET Templates", False, 
                            f"Templates endpoint broken: HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Regression - GET Templates", False, f"Error: {str(e)}")
        
        # Test 3: GET /api/groups still works
        try:
            response = self.session.get(f"{BASE_URL}/groups")
            if response.status_code == 200:
                groups = response.json()
                self.log_test("Regression - GET Groups", True, 
                            f"✅ Groups endpoint working: {len(groups)} groups returned")
            else:
                self.log_test("Regression - GET Groups", False, 
                            f"Groups endpoint broken: HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Regression - GET Groups", False, f"Error: {str(e)}")
        
        # Test 4: GET /api/dashboard/stats still works
        try:
            response = self.session.get(f"{BASE_URL}/dashboard/stats")
            if response.status_code == 200:
                stats = response.json()
                required_sections = ['groups', 'messages', 'scheduler']
                if all(section in stats for section in required_sections):
                    self.log_test("Regression - GET Dashboard Stats", True, 
                                f"✅ Dashboard stats working: {len(stats)} sections returned")
                else:
                    self.log_test("Regression - GET Dashboard Stats", False, 
                                f"Dashboard stats missing sections: {stats}")
            else:
                self.log_test("Regression - GET Dashboard Stats", False, 
                            f"Dashboard stats broken: HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Regression - GET Dashboard Stats", False, f"Error: {str(e)}")
        
        # Test 5: Authentication endpoints still work
        try:
            response = self.session.get(f"{BASE_URL}/auth/sessions")
            if response.status_code == 200:
                sessions = response.json()
                self.log_test("Regression - GET Auth Sessions", True, 
                            f"✅ Auth sessions working: {len(sessions)} sessions returned")
            else:
                self.log_test("Regression - GET Auth Sessions", False, 
                            f"Auth sessions broken: HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Regression - GET Auth Sessions", False, f"Error: {str(e)}")

    def test_edge_cases(self):
        """Test boundary conditions and edge cases for validation rules"""
        print("\n🎯 TESTING EDGE CASES AND BOUNDARY CONDITIONS")
        print("=" * 50)
        print("Testing boundary values and edge cases for validation")
        print("=" * 50)
        
        # Test 1: Settings with boundary values
        try:
            boundary_settings = {
                "min_message_interval": 1,    # Minimum positive value
                "max_message_interval": 2,    # Just above minimum
                "min_cycle_interval": 1,      # Minimum positive value
                "max_cycle_interval": 2,      # Just above minimum
                "max_retry_attempts": 1,
                "is_scheduler_active": False,
                "theme": "auto",
                "notifications_enabled": True
            }
            
            response = self.session.put(f"{BASE_URL}/settings", json=boundary_settings)
            
            if response.status_code == 200:
                self.log_test("Edge Case - Boundary Settings Values", True, 
                            "✅ Boundary values accepted correctly")
            else:
                self.log_test("Edge Case - Boundary Settings Values", False, 
                            f"Boundary values rejected: HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Edge Case - Boundary Settings Values", False, f"Error: {str(e)}")
        
        # Test 2: Settings with zero values (should be rejected)
        try:
            zero_settings = {
                "min_message_interval": 0,    # Zero should be rejected
                "max_message_interval": 10,
                "min_cycle_interval": 60,
                "max_cycle_interval": 120,
                "max_retry_attempts": 3,
                "is_scheduler_active": False,
                "theme": "auto",
                "notifications_enabled": True
            }
            
            response = self.session.put(f"{BASE_URL}/settings", json=zero_settings)
            
            if response.status_code == 400:
                self.log_test("Edge Case - Zero Values Rejection", True, 
                            "✅ Zero values properly rejected")
            else:
                self.log_test("Edge Case - Zero Values Rejection", False, 
                            f"Zero values should be rejected: HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Edge Case - Zero Values Rejection", False, f"Error: {str(e)}")
        
        # Test 3: Template with very long name (should be accepted if not empty)
        try:
            long_name_template = {
                "name": "A" * 100,  # Very long but valid name
                "content": "Valid content",
                "is_default": False
            }
            
            response = self.session.post(f"{BASE_URL}/templates", json=long_name_template)
            
            if response.status_code == 200:
                try:
                    template_data = response.json()
                    template_id = template_data.get('id')
                    self.log_test("Edge Case - Long Template Name", True, 
                                f"✅ Long name accepted: ID {template_id}")
                    
                    # Cleanup
                    if template_id:
                        try:
                            self.session.delete(f"{BASE_URL}/templates/{template_id}")
                        except:
                            pass
                except:
                    self.log_test("Edge Case - Long Template Name", True, 
                                "✅ Long name accepted")
            else:
                self.log_test("Edge Case - Long Template Name", False, 
                            f"Long name rejected: HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Edge Case - Long Template Name", False, f"Error: {str(e)}")

    def run_security_verification_tests(self):
        """Run all security verification tests"""
        print("🔒 CRITICAL SECURITY FIXES VERIFICATION TESTING")
        print("=" * 70)
        print("OBJECTIVE: Verify that all critical security issues have been properly fixed")
        print("=" * 70)
        
        # Run tests in priority order
        self.test_scheduler_authentication_fixes()  # CRITICAL
        self.test_settings_validation_fixes()       # HIGH PRIORITY
        self.test_template_validation_fixes()       # HIGH PRIORITY
        self.test_regression_endpoints()            # REGRESSION CHECK
        self.test_edge_cases()                      # EDGE CASES
        
        # Summary
        print("\n" + "=" * 70)
        print("🔒 SECURITY VERIFICATION SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Security Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Critical security analysis
        scheduler_tests = [r for r in self.test_results if 'scheduler' in r['test'].lower() and 'auth' in r['test'].lower()]
        scheduler_passed = sum(1 for r in scheduler_tests if r['success'])
        
        settings_tests = [r for r in self.test_results if 'settings' in r['test'].lower() and 'validation' in r['test'].lower()]
        settings_passed = sum(1 for r in settings_tests if r['success'])
        
        template_tests = [r for r in self.test_results if 'template' in r['test'].lower() and 'validation' in r['test'].lower()]
        template_passed = sum(1 for r in template_tests if r['success'])
        
        print(f"\n🔒 CRITICAL SECURITY AREAS:")
        print(f"  📅 Scheduler Authentication: {scheduler_passed}/{len(scheduler_tests)} passed")
        print(f"  ⚙️  Settings Validation: {settings_passed}/{len(settings_tests)} passed")
        print(f"  📝 Template Validation: {template_passed}/{len(template_tests)} passed")
        
        # Security status
        critical_security_passed = scheduler_passed + settings_passed + template_passed
        critical_security_total = len(scheduler_tests) + len(settings_tests) + len(template_tests)
        
        print(f"\n🛡️  OVERALL SECURITY STATUS:")
        if critical_security_passed == critical_security_total:
            print("  ✅ ALL CRITICAL SECURITY FIXES VERIFIED - SYSTEM SECURE")
        else:
            print(f"  ❌ SECURITY VULNERABILITIES DETECTED: {critical_security_total - critical_security_passed} issues remain")
        
        # Failed tests details
        if failed_tests > 0:
            print(f"\n❌ FAILED SECURITY TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        # Regression status
        regression_tests = [r for r in self.test_results if 'regression' in r['test'].lower()]
        regression_passed = sum(1 for r in regression_tests if r['success'])
        
        print(f"\n🔄 REGRESSION STATUS:")
        if regression_passed == len(regression_tests):
            print("  ✅ NO REGRESSION DETECTED - All existing functionality working")
        else:
            print(f"  ⚠️  REGRESSION ISSUES: {len(regression_tests) - regression_passed} endpoints affected")
        
        return {
            'total': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'scheduler_auth_passed': scheduler_passed,
            'settings_validation_passed': settings_passed,
            'template_validation_passed': template_passed,
            'regression_passed': regression_passed,
            'critical_security_status': 'SECURE' if critical_security_passed == critical_security_total else 'VULNERABLE',
            'results': self.test_results
        }

if __name__ == "__main__":
    tester = SecurityVerificationTester()
    results = tester.run_security_verification_tests()
    
    # Exit with error code if critical security tests failed
    if results['critical_security_status'] == 'VULNERABLE':
        exit(1)
    else:
        exit(0)