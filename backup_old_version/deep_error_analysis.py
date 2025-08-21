#!/usr/bin/env python3
"""
DEEP ERROR ANALYSIS - Focus on specific potential issues
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "https://tidy-archives.preview.emergentagent.com/api"

class DeepErrorAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.issues_found = []
    
    def log_issue(self, category: str, severity: str, description: str, details: str = ""):
        """Log an issue found"""
        issue = {
            'category': category,
            'severity': severity,
            'description': description,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.issues_found.append(issue)
        print(f"🔍 {severity.upper()} - {category}: {description}")
        if details:
            print(f"   Details: {details}")
    
    def test_template_validation_bug(self):
        """Test the template validation bug found in comprehensive test"""
        print("\n🔍 ANALYZING TEMPLATE VALIDATION BUG")
        print("-" * 50)
        
        # Test empty template name (should fail but doesn't)
        empty_name_template = {
            "name": "",
            "content": "This template has an empty name",
            "is_default": False
        }
        
        response = self.session.post(f"{BASE_URL}/templates", json=empty_name_template)
        if response.status_code == 200:
            template_data = response.json()
            self.log_issue("Validation Bug", "medium", 
                         "Template creation accepts empty name", 
                         f"Created template with empty name, ID: {template_data.get('id')}")
            
            # Clean up
            if template_data.get('id'):
                self.session.delete(f"{BASE_URL}/templates/{template_data['id']}")
        
        # Test whitespace-only name
        whitespace_name_template = {
            "name": "   ",
            "content": "This template has whitespace-only name",
            "is_default": False
        }
        
        response = self.session.post(f"{BASE_URL}/templates", json=whitespace_name_template)
        if response.status_code == 200:
            template_data = response.json()
            self.log_issue("Validation Bug", "medium", 
                         "Template creation accepts whitespace-only name", 
                         f"Created template with whitespace name, ID: {template_data.get('id')}")
            
            # Clean up
            if template_data.get('id'):
                self.session.delete(f"{BASE_URL}/templates/{template_data['id']}")
    
    def test_settings_validation_bug(self):
        """Test the settings validation bug found"""
        print("\n🔍 ANALYZING SETTINGS VALIDATION BUG")
        print("-" * 50)
        
        # Get current settings
        current_response = self.session.get(f"{BASE_URL}/settings")
        if current_response.status_code == 200:
            current_settings = current_response.json()
            
            # Test negative intervals (should fail but doesn't)
            invalid_settings = current_settings.copy()
            invalid_settings['min_message_interval'] = -10
            invalid_settings['max_message_interval'] = -5
            invalid_settings['min_cycle_interval'] = -60
            invalid_settings['max_cycle_interval'] = -30
            
            response = self.session.put(f"{BASE_URL}/settings", json=invalid_settings)
            if response.status_code == 200:
                self.log_issue("Validation Bug", "medium", 
                             "Settings update accepts negative intervals", 
                             f"Negative intervals were accepted: min_msg={invalid_settings['min_message_interval']}, max_msg={invalid_settings['max_message_interval']}")
                
                # Restore original settings
                self.session.put(f"{BASE_URL}/settings", json=current_settings)
            
            # Test illogical intervals (min > max)
            illogical_settings = current_settings.copy()
            illogical_settings['min_message_interval'] = 100
            illogical_settings['max_message_interval'] = 50  # min > max
            
            response = self.session.put(f"{BASE_URL}/settings", json=illogical_settings)
            if response.status_code == 200:
                self.log_issue("Logic Bug", "medium", 
                             "Settings accepts min_interval > max_interval", 
                             f"Accepted min={illogical_settings['min_message_interval']} > max={illogical_settings['max_message_interval']}")
                
                # Restore original settings
                self.session.put(f"{BASE_URL}/settings", json=current_settings)
    
    def test_potential_sql_injection(self):
        """Test for potential injection vulnerabilities"""
        print("\n🔍 TESTING FOR INJECTION VULNERABILITIES")
        print("-" * 50)
        
        # Test SQL injection patterns in various endpoints
        injection_payloads = [
            "'; DROP TABLE templates; --",
            "' OR '1'='1",
            "'; SELECT * FROM sessions; --",
            "<script>alert('xss')</script>",
            "{{7*7}}",  # Template injection
            "${7*7}",   # Expression injection
        ]
        
        for payload in injection_payloads:
            # Test in template name
            try:
                template_data = {
                    "name": payload,
                    "content": "Testing injection",
                    "is_default": False
                }
                
                response = self.session.post(f"{BASE_URL}/templates", json=template_data)
                if response.status_code == 200:
                    template_result = response.json()
                    
                    # Check if payload was executed or processed
                    if template_result.get('name') != payload:
                        self.log_issue("Security", "high", 
                                     "Potential template injection vulnerability", 
                                     f"Payload '{payload}' was processed differently: {template_result.get('name')}")
                    
                    # Clean up
                    if template_result.get('id'):
                        self.session.delete(f"{BASE_URL}/templates/{template_result['id']}")
                        
            except Exception as e:
                if "500" in str(e) or "error" in str(e).lower():
                    self.log_issue("Security", "medium", 
                                 "Injection payload caused server error", 
                                 f"Payload '{payload}' caused: {str(e)}")
    
    def test_rate_limiting(self):
        """Test for rate limiting and DoS protection"""
        print("\n🔍 TESTING RATE LIMITING & DOS PROTECTION")
        print("-" * 50)
        
        # Test rapid requests to see if there's rate limiting
        start_time = time.time()
        responses = []
        
        for i in range(50):  # 50 rapid requests
            try:
                response = self.session.get(f"{BASE_URL}/settings")
                responses.append(response.status_code)
                
                if response.status_code == 429:  # Rate limited
                    print(f"✅ Rate limiting detected at request {i+1}")
                    break
                    
            except Exception as e:
                responses.append(f"Error: {str(e)}")
                break
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Check if all requests succeeded (potential DoS vulnerability)
        successful_requests = sum(1 for r in responses if r == 200)
        
        if successful_requests == 50:
            self.log_issue("Security", "low", 
                         "No rate limiting detected", 
                         f"50 rapid requests all succeeded in {total_time:.2f} seconds")
        elif successful_requests > 30:
            self.log_issue("Security", "low", 
                         "Weak rate limiting", 
                         f"{successful_requests}/50 requests succeeded")
    
    def test_authentication_bypass(self):
        """Test for authentication bypass vulnerabilities"""
        print("\n🔍 TESTING AUTHENTICATION BYPASS")
        print("-" * 50)
        
        # Test accessing protected endpoints without proper authentication
        protected_endpoints = [
            ("POST", "/groups/single", {"identifier": "@test"}),
            ("POST", "/groups/bulk", {"identifiers": ["@test1", "@test2"]}),
            ("POST", "/messages/send", {"group_ids": ["123"], "message_template_id": "test", "send_immediately": True}),
            ("POST", "/scheduler/start", {}),
            ("POST", "/scheduler/stop", {}),
        ]
        
        for method, endpoint, data in protected_endpoints:
            # Test with invalid session_id
            try:
                url = f"{BASE_URL}{endpoint}?session_id=invalid_session_123"
                
                if method == "POST":
                    response = self.session.post(url, json=data)
                
                if response.status_code == 200:
                    self.log_issue("Security", "high", 
                                 f"Authentication bypass in {endpoint}", 
                                 f"Endpoint accessible with invalid session_id")
                elif response.status_code not in [401, 403]:
                    self.log_issue("Security", "medium", 
                                 f"Unexpected auth response in {endpoint}", 
                                 f"Expected 401/403, got {response.status_code}")
                    
            except Exception as e:
                pass  # Expected for some endpoints
    
    def test_data_exposure(self):
        """Test for potential data exposure issues"""
        print("\n🔍 TESTING DATA EXPOSURE")
        print("-" * 50)
        
        # Test if sensitive data is exposed in responses
        
        # Check sessions endpoint for sensitive data
        response = self.session.get(f"{BASE_URL}/auth/sessions")
        if response.status_code == 200:
            sessions = response.json()
            for session in sessions:
                if 'encrypted_session' in session or 'api_hash' in session or 'password' in session:
                    self.log_issue("Security", "high", 
                                 "Sensitive data exposed in sessions endpoint", 
                                 f"Session contains sensitive fields: {list(session.keys())}")
        
        # Check if error messages expose sensitive information
        response = self.session.post(f"{BASE_URL}/auth/login", json={
            "api_id": 12345,
            "api_hash": "test_hash",
            "phone_number": "+1234567890"
        })
        
        if response.status_code == 400:
            try:
                error_data = response.json()
                error_detail = error_data.get('detail', '')
                
                # Check if error exposes internal paths or sensitive info
                if '/app/' in error_detail or 'mongodb://' in error_detail or 'password' in error_detail.lower():
                    self.log_issue("Security", "medium", 
                                 "Error message exposes sensitive information", 
                                 f"Error detail: {error_detail}")
            except:
                pass
    
    def test_cors_configuration(self):
        """Test CORS configuration"""
        print("\n🔍 TESTING CORS CONFIGURATION")
        print("-" * 50)
        
        # Test CORS headers
        response = self.session.options(f"{BASE_URL}/settings")
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
        }
        
        # Check for overly permissive CORS
        if cors_headers['Access-Control-Allow-Origin'] == '*':
            self.log_issue("Security", "low", 
                         "Overly permissive CORS policy", 
                         "Access-Control-Allow-Origin is set to '*'")
    
    def test_error_information_disclosure(self):
        """Test for information disclosure in error messages"""
        print("\n🔍 TESTING ERROR INFORMATION DISCLOSURE")
        print("-" * 50)
        
        # Test various malformed requests to see error details
        malformed_requests = [
            ("POST", "/templates", "invalid_json"),
            ("PUT", "/settings", {"invalid": "structure"}),
            ("POST", "/auth/login", {"api_id": "extremely_long_string" * 1000}),
        ]
        
        for method, endpoint, data in malformed_requests:
            try:
                url = f"{BASE_URL}{endpoint}"
                
                if method == "POST":
                    if isinstance(data, str):
                        # Send invalid JSON
                        response = self.session.post(url, data=data, headers={'Content-Type': 'application/json'})
                    else:
                        response = self.session.post(url, json=data)
                elif method == "PUT":
                    response = self.session.put(url, json=data)
                
                if 400 <= response.status_code < 500:
                    try:
                        error_data = response.json()
                        error_detail = str(error_data)
                        
                        # Check for stack traces or internal paths
                        if 'Traceback' in error_detail or '/app/' in error_detail or 'File "' in error_detail:
                            self.log_issue("Security", "medium", 
                                         f"Stack trace exposed in {endpoint}", 
                                         f"Error contains internal details: {error_detail[:200]}...")
                    except:
                        pass
                        
            except Exception as e:
                pass
    
    def run_deep_analysis(self):
        """Run all deep error analysis tests"""
        print("🔍 DEEP ERROR ANALYSIS - TELEGRAM AUTO SENDER")
        print("=" * 60)
        print("Focus: Specific bugs and security vulnerabilities")
        print("=" * 60)
        
        self.test_template_validation_bug()
        self.test_settings_validation_bug()
        self.test_potential_sql_injection()
        self.test_rate_limiting()
        self.test_authentication_bypass()
        self.test_data_exposure()
        self.test_cors_configuration()
        self.test_error_information_disclosure()
        
        # Generate report
        print("\n" + "=" * 60)
        print("🔍 DEEP ANALYSIS REPORT")
        print("=" * 60)
        
        if not self.issues_found:
            print("✅ NO ADDITIONAL ISSUES FOUND IN DEEP ANALYSIS")
            return
        
        # Categorize issues
        critical_issues = [i for i in self.issues_found if i['severity'] == 'critical']
        high_issues = [i for i in self.issues_found if i['severity'] == 'high']
        medium_issues = [i for i in self.issues_found if i['severity'] == 'medium']
        low_issues = [i for i in self.issues_found if i['severity'] == 'low']
        
        print(f"🚨 Critical Issues: {len(critical_issues)}")
        print(f"🔥 High Priority Issues: {len(high_issues)}")
        print(f"⚠️  Medium Priority Issues: {len(medium_issues)}")
        print(f"💡 Low Priority Issues: {len(low_issues)}")
        
        # Show all issues
        for issue in self.issues_found:
            print(f"\n{issue['severity'].upper()} - {issue['category']}")
            print(f"Description: {issue['description']}")
            if issue['details']:
                print(f"Details: {issue['details']}")
        
        return {
            'total_issues': len(self.issues_found),
            'critical': len(critical_issues),
            'high': len(high_issues),
            'medium': len(medium_issues),
            'low': len(low_issues),
            'issues': self.issues_found
        }

if __name__ == "__main__":
    analyzer = DeepErrorAnalyzer()
    results = analyzer.run_deep_analysis()
    
    if results and results['critical'] > 0:
        exit(2)
    elif results and results['high'] > 0:
        exit(1)
    else:
        exit(0)