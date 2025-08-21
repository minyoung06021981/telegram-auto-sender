#!/usr/bin/env python3
"""
COMPREHENSIVE ERROR IDENTIFICATION TEST
Focus: Identify ALL existing errors, bugs, and issues in the Telegram Auto Sender backend
"""

import requests
import json
import time
import uuid
import asyncio
import subprocess
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List

# Configuration
BASE_URL = "https://tidy-archives.preview.emergentagent.com/api"
HEALTH_URL = "https://tidy-archives.preview.emergentagent.com"

class ComprehensiveErrorTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.errors_found = []
        self.warnings_found = []
        self.test_results = []
        
    def log_error(self, category: str, severity: str, description: str, details: str = "", reproduction_steps: List[str] = None):
        """Log an error or issue found"""
        error = {
            'category': category,
            'severity': severity,  # critical, high, medium, low
            'description': description,
            'details': details,
            'reproduction_steps': reproduction_steps or [],
            'timestamp': datetime.now().isoformat()
        }
        
        if severity in ['critical', 'high']:
            self.errors_found.append(error)
            print(f"🚨 {severity.upper()} ERROR - {category}: {description}")
            if details:
                print(f"   Details: {details}")
        else:
            self.warnings_found.append(error)
            print(f"⚠️  {severity.upper()} WARNING - {category}: {description}")
            if details:
                print(f"   Details: {details}")
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}: {details}")
    
    def test_dependency_issues(self):
        """Test for dependency and startup issues"""
        print("\n🔍 TESTING DEPENDENCY & STARTUP ISSUES")
        print("-" * 50)
        
        try:
            # Test if backend is running
            response = self.session.get(f"{BASE_URL}/settings", timeout=10)
            if response.status_code == 200:
                self.log_test("Backend Service Status", True, "Backend is running and responding")
            else:
                self.log_error("Startup", "critical", "Backend service not responding properly", 
                             f"HTTP {response.status_code}: {response.text}")
                self.log_test("Backend Service Status", False, f"HTTP {response.status_code}")
        except requests.exceptions.ConnectionError:
            self.log_error("Startup", "critical", "Cannot connect to backend service", 
                         "Connection refused - service may be down")
            self.log_test("Backend Service Status", False, "Connection refused")
        except requests.exceptions.Timeout:
            self.log_error("Startup", "high", "Backend service timeout", 
                         "Service is slow to respond or hanging")
            self.log_test("Backend Service Status", False, "Timeout")
        except Exception as e:
            self.log_error("Startup", "high", "Unexpected error connecting to backend", str(e))
            self.log_test("Backend Service Status", False, f"Error: {str(e)}")
    
    def test_api_endpoint_errors(self):
        """Test ALL API endpoints for errors and crashes"""
        print("\n🔍 TESTING API ENDPOINT FUNCTIONALITY")
        print("-" * 50)
        
        # Test all endpoints with various inputs
        endpoints_to_test = [
            # Authentication endpoints
            ("GET", "/auth/sessions", None, "Authentication - Get Sessions"),
            ("POST", "/auth/login", {"api_id": "invalid", "api_hash": "invalid", "phone_number": "invalid"}, "Authentication - Login Invalid"),
            ("POST", "/auth/verify", {"session_id": "invalid", "phone_code": "12345"}, "Authentication - Verify Invalid"),
            ("POST", "/auth/load-session/invalid_id", None, "Authentication - Load Invalid Session"),
            
            # Group management endpoints
            ("GET", "/groups", None, "Groups - Get All"),
            ("GET", "/groups/stats", None, "Groups - Get Stats"),
            ("POST", "/groups/single", {"identifier": "@testgroup"}, "Groups - Create Single (No Session)"),
            ("POST", "/groups/bulk", {"identifiers": ["@test1", "@test2"]}, "Groups - Create Bulk (No Session)"),
            
            # Template endpoints
            ("GET", "/templates", None, "Templates - Get All"),
            ("POST", "/templates", {"name": "Test", "content": "Test content"}, "Templates - Create"),
            ("GET", "/templates/default", None, "Templates - Get Default"),
            
            # Settings endpoints
            ("GET", "/settings", None, "Settings - Get"),
            ("PUT", "/settings", {"min_message_interval": 10, "max_message_interval": 30}, "Settings - Update"),
            
            # Dashboard endpoints
            ("GET", "/dashboard/stats", None, "Dashboard - Get Stats"),
            ("GET", "/logs/messages", None, "Dashboard - Get Logs"),
            
            # Scheduler endpoints
            ("POST", "/scheduler/start", None, "Scheduler - Start (No Session)"),
            ("POST", "/scheduler/stop", None, "Scheduler - Stop (No Session)"),
            
            # Message endpoints
            ("POST", "/messages/send", {"group_ids": ["123"], "message_template_id": "test", "send_immediately": True}, "Messages - Send (No Session)"),
        ]
        
        for method, endpoint, data, description in endpoints_to_test:
            try:
                url = f"{BASE_URL}{endpoint}"
                
                if method == "GET":
                    response = self.session.get(url, timeout=10)
                elif method == "POST":
                    response = self.session.post(url, json=data, timeout=10)
                elif method == "PUT":
                    response = self.session.put(url, json=data, timeout=10)
                elif method == "DELETE":
                    response = self.session.delete(url, timeout=10)
                
                # Check for server errors (5xx)
                if 500 <= response.status_code < 600:
                    self.log_error("API Endpoint", "high", f"Server error in {description}", 
                                 f"HTTP {response.status_code}: {response.text}",
                                 [f"{method} {url}", f"Data: {data}"])
                    self.log_test(description, False, f"Server error - HTTP {response.status_code}")
                
                # Check for unexpected errors
                elif response.status_code not in [200, 201, 400, 401, 404, 422]:
                    self.log_error("API Endpoint", "medium", f"Unexpected status code in {description}", 
                                 f"HTTP {response.status_code}: {response.text}",
                                 [f"{method} {url}", f"Data: {data}"])
                    self.log_test(description, False, f"Unexpected status - HTTP {response.status_code}")
                
                else:
                    self.log_test(description, True, f"HTTP {response.status_code} (expected)")
                
                # Check response format
                if response.status_code in [200, 201]:
                    try:
                        response.json()
                    except json.JSONDecodeError:
                        self.log_error("API Endpoint", "medium", f"Invalid JSON response in {description}", 
                                     f"Response: {response.text[:200]}...",
                                     [f"{method} {url}"])
                
            except requests.exceptions.Timeout:
                self.log_error("API Endpoint", "high", f"Timeout in {description}", 
                             f"Endpoint {endpoint} is slow or hanging",
                             [f"{method} {url}", f"Data: {data}"])
                self.log_test(description, False, "Timeout")
            
            except requests.exceptions.ConnectionError:
                self.log_error("API Endpoint", "critical", f"Connection error in {description}", 
                             f"Cannot connect to {endpoint}",
                             [f"{method} {url}"])
                self.log_test(description, False, "Connection error")
            
            except Exception as e:
                self.log_error("API Endpoint", "high", f"Unexpected error in {description}", 
                             str(e),
                             [f"{method} {url}", f"Data: {data}"])
                self.log_test(description, False, f"Error: {str(e)}")
    
    def test_database_connectivity(self):
        """Test database connectivity and operations"""
        print("\n🔍 TESTING DATABASE CONNECTIVITY")
        print("-" * 50)
        
        try:
            # Test database operations through API endpoints
            
            # Test reading from database (groups)
            response = self.session.get(f"{BASE_URL}/groups")
            if response.status_code == 200:
                self.log_test("Database Read (Groups)", True, "Can read from groups collection")
            else:
                self.log_error("Database", "high", "Cannot read from groups collection", 
                             f"HTTP {response.status_code}: {response.text}")
                self.log_test("Database Read (Groups)", False, f"HTTP {response.status_code}")
            
            # Test reading from database (templates)
            response = self.session.get(f"{BASE_URL}/templates")
            if response.status_code == 200:
                self.log_test("Database Read (Templates)", True, "Can read from templates collection")
            else:
                self.log_error("Database", "high", "Cannot read from templates collection", 
                             f"HTTP {response.status_code}: {response.text}")
                self.log_test("Database Read (Templates)", False, f"HTTP {response.status_code}")
            
            # Test writing to database (create template)
            test_template = {
                "name": "DB Test Template",
                "content": "Testing database write operations",
                "is_default": False
            }
            
            response = self.session.post(f"{BASE_URL}/templates", json=test_template)
            if response.status_code == 200:
                template_data = response.json()
                template_id = template_data.get('id')
                self.log_test("Database Write (Templates)", True, f"Can write to templates collection - ID: {template_id}")
                
                # Test updating database
                updated_template = test_template.copy()
                updated_template['content'] = "Updated content for database test"
                
                update_response = self.session.put(f"{BASE_URL}/templates/{template_id}", json=updated_template)
                if update_response.status_code == 200:
                    self.log_test("Database Update (Templates)", True, "Can update templates collection")
                else:
                    self.log_error("Database", "medium", "Cannot update templates collection", 
                                 f"HTTP {update_response.status_code}: {update_response.text}")
                    self.log_test("Database Update (Templates)", False, f"HTTP {update_response.status_code}")
                
                # Test deleting from database
                delete_response = self.session.delete(f"{BASE_URL}/templates/{template_id}")
                if delete_response.status_code == 200:
                    self.log_test("Database Delete (Templates)", True, "Can delete from templates collection")
                else:
                    self.log_error("Database", "medium", "Cannot delete from templates collection", 
                                 f"HTTP {delete_response.status_code}: {delete_response.text}")
                    self.log_test("Database Delete (Templates)", False, f"HTTP {delete_response.status_code}")
                
            else:
                self.log_error("Database", "high", "Cannot write to templates collection", 
                             f"HTTP {response.status_code}: {response.text}")
                self.log_test("Database Write (Templates)", False, f"HTTP {response.status_code}")
            
        except Exception as e:
            self.log_error("Database", "critical", "Database connectivity test failed", str(e))
            self.log_test("Database Connectivity", False, f"Error: {str(e)}")
    
    def test_authentication_edge_cases(self):
        """Test authentication system edge cases"""
        print("\n🔍 TESTING AUTHENTICATION EDGE CASES")
        print("-" * 50)
        
        # Test malformed requests
        malformed_tests = [
            ({"api_id": "not_a_number", "api_hash": "test", "phone_number": "+1234567890"}, "Non-numeric API ID"),
            ({"api_id": 12345, "api_hash": "", "phone_number": "+1234567890"}, "Empty API hash"),
            ({"api_id": 12345, "api_hash": "test", "phone_number": "invalid_phone"}, "Invalid phone format"),
            ({"api_id": 12345, "api_hash": "test"}, "Missing phone number"),
            ({}, "Empty request body"),
            ({"api_id": -1, "api_hash": "test", "phone_number": "+1234567890"}, "Negative API ID"),
        ]
        
        for data, description in malformed_tests:
            try:
                response = self.session.post(f"{BASE_URL}/auth/login", json=data)
                
                if response.status_code == 422:
                    self.log_test(f"Auth Validation - {description}", True, "Proper validation error")
                elif response.status_code == 400:
                    self.log_test(f"Auth Validation - {description}", True, "Proper error handling")
                elif 500 <= response.status_code < 600:
                    self.log_error("Authentication", "high", f"Server error with {description}", 
                                 f"HTTP {response.status_code}: {response.text}")
                    self.log_test(f"Auth Validation - {description}", False, f"Server error - HTTP {response.status_code}")
                else:
                    self.log_error("Authentication", "medium", f"Unexpected response for {description}", 
                                 f"HTTP {response.status_code}: {response.text}")
                    self.log_test(f"Auth Validation - {description}", False, f"Unexpected - HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_error("Authentication", "high", f"Exception with {description}", str(e))
                self.log_test(f"Auth Validation - {description}", False, f"Exception: {str(e)}")
    
    def test_scheduler_system(self):
        """Test scheduler system for errors"""
        print("\n🔍 TESTING SCHEDULER SYSTEM")
        print("-" * 50)
        
        try:
            # Test scheduler endpoints without session
            start_response = self.session.post(f"{BASE_URL}/scheduler/start")
            if start_response.status_code == 422:
                self.log_test("Scheduler Start Validation", True, "Proper validation for missing session")
            else:
                self.log_error("Scheduler", "medium", "Scheduler start endpoint validation issue", 
                             f"Expected HTTP 422, got {start_response.status_code}")
                self.log_test("Scheduler Start Validation", False, f"HTTP {start_response.status_code}")
            
            stop_response = self.session.post(f"{BASE_URL}/scheduler/stop")
            if stop_response.status_code == 422:
                self.log_test("Scheduler Stop Validation", True, "Proper validation for missing session")
            else:
                self.log_error("Scheduler", "medium", "Scheduler stop endpoint validation issue", 
                             f"Expected HTTP 422, got {stop_response.status_code}")
                self.log_test("Scheduler Stop Validation", False, f"HTTP {stop_response.status_code}")
                
        except Exception as e:
            self.log_error("Scheduler", "high", "Scheduler system test failed", str(e))
            self.log_test("Scheduler System", False, f"Error: {str(e)}")
    
    def test_error_handling(self):
        """Test error handling and validation"""
        print("\n🔍 TESTING ERROR HANDLING & VALIDATION")
        print("-" * 50)
        
        # Test various invalid inputs
        invalid_tests = [
            ("POST", "/templates", {"name": "", "content": "test"}, "Empty template name"),
            ("POST", "/templates", {"name": "test"}, "Missing template content"),
            ("PUT", "/settings", {"min_message_interval": -1}, "Negative interval"),
            ("PUT", "/settings", {"min_message_interval": "not_a_number"}, "Non-numeric interval"),
            ("POST", "/groups/single", {"identifier": ""}, "Empty group identifier"),
            ("POST", "/groups/bulk", {"identifiers": []}, "Empty identifiers list"),
        ]
        
        for method, endpoint, data, description in invalid_tests:
            try:
                url = f"{BASE_URL}{endpoint}"
                
                if method == "POST":
                    response = self.session.post(url, json=data)
                elif method == "PUT":
                    response = self.session.put(url, json=data)
                
                if response.status_code in [400, 422]:
                    self.log_test(f"Error Handling - {description}", True, f"Proper validation - HTTP {response.status_code}")
                elif 500 <= response.status_code < 600:
                    self.log_error("Error Handling", "high", f"Server error with {description}", 
                                 f"HTTP {response.status_code}: {response.text}")
                    self.log_test(f"Error Handling - {description}", False, f"Server error - HTTP {response.status_code}")
                else:
                    self.log_error("Error Handling", "medium", f"Poor error handling for {description}", 
                                 f"Expected 400/422, got HTTP {response.status_code}")
                    self.log_test(f"Error Handling - {description}", False, f"Poor handling - HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_error("Error Handling", "high", f"Exception testing {description}", str(e))
                self.log_test(f"Error Handling - {description}", False, f"Exception: {str(e)}")
    
    def test_configuration_issues(self):
        """Test configuration and environment issues"""
        print("\n🔍 TESTING CONFIGURATION ISSUES")
        print("-" * 50)
        
        try:
            # Test if settings endpoint works (indicates config is readable)
            response = self.session.get(f"{BASE_URL}/settings")
            if response.status_code == 200:
                settings = response.json()
                
                # Check for required settings
                required_settings = ['min_message_interval', 'max_message_interval', 'min_cycle_interval', 'max_cycle_interval']
                missing_settings = [s for s in required_settings if s not in settings]
                
                if missing_settings:
                    self.log_error("Configuration", "medium", "Missing required settings", 
                                 f"Missing: {missing_settings}")
                    self.log_test("Configuration Completeness", False, f"Missing: {missing_settings}")
                else:
                    self.log_test("Configuration Completeness", True, "All required settings present")
                
                # Check for reasonable values
                if settings.get('min_message_interval', 0) < 1:
                    self.log_error("Configuration", "low", "Very low message interval", 
                                 f"min_message_interval: {settings.get('min_message_interval')}")
                
                if settings.get('max_message_interval', 0) > 300:
                    self.log_error("Configuration", "low", "Very high message interval", 
                                 f"max_message_interval: {settings.get('max_message_interval')}")
                
                self.log_test("Configuration Values", True, "Settings values are reasonable")
                
            else:
                self.log_error("Configuration", "high", "Cannot read configuration", 
                             f"Settings endpoint failed: HTTP {response.status_code}")
                self.log_test("Configuration Read", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.log_error("Configuration", "high", "Configuration test failed", str(e))
            self.log_test("Configuration Test", False, f"Error: {str(e)}")
    
    def test_memory_performance(self):
        """Test for memory leaks and performance issues"""
        print("\n🔍 TESTING MEMORY & PERFORMANCE")
        print("-" * 50)
        
        try:
            # Test multiple rapid requests to check for memory leaks
            start_time = time.time()
            
            for i in range(10):
                response = self.session.get(f"{BASE_URL}/settings")
                if response.status_code != 200:
                    self.log_error("Performance", "medium", f"Request {i+1} failed during load test", 
                                 f"HTTP {response.status_code}")
                    break
            
            end_time = time.time()
            total_time = end_time - start_time
            
            if total_time > 30:  # 10 requests taking more than 30 seconds
                self.log_error("Performance", "medium", "Slow response times detected", 
                             f"10 requests took {total_time:.2f} seconds")
                self.log_test("Performance Load Test", False, f"Slow - {total_time:.2f}s for 10 requests")
            else:
                self.log_test("Performance Load Test", True, f"Good - {total_time:.2f}s for 10 requests")
            
            # Test concurrent requests
            import threading
            import queue
            
            results_queue = queue.Queue()
            
            def make_request():
                try:
                    response = self.session.get(f"{BASE_URL}/dashboard/stats")
                    results_queue.put(response.status_code)
                except Exception as e:
                    results_queue.put(f"Error: {str(e)}")
            
            # Start 5 concurrent requests
            threads = []
            for i in range(5):
                thread = threading.Thread(target=make_request)
                threads.append(thread)
                thread.start()
            
            # Wait for all threads
            for thread in threads:
                thread.join(timeout=10)
            
            # Check results
            concurrent_results = []
            while not results_queue.empty():
                concurrent_results.append(results_queue.get())
            
            successful_concurrent = sum(1 for r in concurrent_results if r == 200)
            
            if successful_concurrent == 5:
                self.log_test("Concurrent Requests", True, "All 5 concurrent requests succeeded")
            else:
                self.log_error("Performance", "medium", "Concurrent request handling issues", 
                             f"Only {successful_concurrent}/5 requests succeeded: {concurrent_results}")
                self.log_test("Concurrent Requests", False, f"Only {successful_concurrent}/5 succeeded")
                
        except Exception as e:
            self.log_error("Performance", "high", "Performance test failed", str(e))
            self.log_test("Performance Test", False, f"Error: {str(e)}")
    
    def run_comprehensive_error_identification(self):
        """Run all error identification tests"""
        print("🔍 COMPREHENSIVE ERROR IDENTIFICATION - TELEGRAM AUTO SENDER")
        print("=" * 70)
        print("Objective: Identify ALL existing errors, bugs, and issues")
        print("=" * 70)
        
        # Run all test categories
        self.test_dependency_issues()
        self.test_api_endpoint_errors()
        self.test_database_connectivity()
        self.test_authentication_edge_cases()
        self.test_scheduler_system()
        self.test_error_handling()
        self.test_configuration_issues()
        self.test_memory_performance()
        
        # Generate comprehensive report
        print("\n" + "=" * 70)
        print("🚨 COMPREHENSIVE ERROR REPORT")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests Performed: {total_tests}")
        print(f"Tests Passed: {passed_tests} ✅")
        print(f"Tests Failed: {failed_tests} ❌")
        print(f"Overall Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n🚨 CRITICAL ERRORS FOUND: {len([e for e in self.errors_found if e['severity'] == 'critical'])}")
        print(f"🔥 HIGH PRIORITY ERRORS: {len([e for e in self.errors_found if e['severity'] == 'high'])}")
        print(f"⚠️  MEDIUM PRIORITY ERRORS: {len([e for e in self.errors_found if e['severity'] == 'medium'])}")
        print(f"💡 LOW PRIORITY WARNINGS: {len([e for e in self.warnings_found if e['severity'] == 'low'])}")
        
        # Detailed error breakdown
        if self.errors_found:
            print("\n🚨 DETAILED ERROR BREAKDOWN:")
            print("-" * 50)
            
            for error in self.errors_found:
                print(f"\n{error['severity'].upper()} - {error['category']}")
                print(f"Description: {error['description']}")
                if error['details']:
                    print(f"Details: {error['details']}")
                if error['reproduction_steps']:
                    print("Reproduction Steps:")
                    for step in error['reproduction_steps']:
                        print(f"  - {step}")
        
        if self.warnings_found:
            print("\n⚠️  WARNINGS & MINOR ISSUES:")
            print("-" * 50)
            
            for warning in self.warnings_found:
                print(f"\n{warning['severity'].upper()} - {warning['category']}")
                print(f"Description: {warning['description']}")
                if warning['details']:
                    print(f"Details: {warning['details']}")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        print("-" * 50)
        
        critical_errors = [e for e in self.errors_found if e['severity'] == 'critical']
        high_errors = [e for e in self.errors_found if e['severity'] == 'high']
        
        if critical_errors:
            print("🚨 IMMEDIATE ACTION REQUIRED:")
            for error in critical_errors:
                print(f"  - Fix {error['category']}: {error['description']}")
        
        if high_errors:
            print("🔥 HIGH PRIORITY FIXES:")
            for error in high_errors:
                print(f"  - Address {error['category']}: {error['description']}")
        
        if not self.errors_found:
            print("✅ NO CRITICAL OR HIGH PRIORITY ERRORS FOUND!")
            print("   The system appears to be functioning well.")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'critical_errors': len([e for e in self.errors_found if e['severity'] == 'critical']),
            'high_errors': len([e for e in self.errors_found if e['severity'] == 'high']),
            'medium_errors': len([e for e in self.errors_found if e['severity'] == 'medium']),
            'low_warnings': len([e for e in self.warnings_found if e['severity'] == 'low']),
            'errors_found': self.errors_found,
            'warnings_found': self.warnings_found,
            'test_results': self.test_results
        }

if __name__ == "__main__":
    tester = ComprehensiveErrorTester()
    results = tester.run_comprehensive_error_identification()
    
    # Exit with appropriate code
    if results['critical_errors'] > 0:
        print("\n🚨 CRITICAL ERRORS DETECTED - IMMEDIATE ATTENTION REQUIRED")
        exit(2)
    elif results['high_errors'] > 0:
        print("\n🔥 HIGH PRIORITY ERRORS DETECTED - SHOULD BE ADDRESSED SOON")
        exit(1)
    else:
        print("\n✅ NO CRITICAL ERRORS FOUND - SYSTEM IS STABLE")
        exit(0)