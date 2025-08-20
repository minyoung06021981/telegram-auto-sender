#!/usr/bin/env python3
"""
Scheduler Debug Tests for Telegram Auto Sender
Focus: Debug why scheduler is not sending automatic messages

Test Areas:
1. Scheduler Status - Check if scheduler.active = true
2. Template Default - Check if there's a default template
3. Active Groups - Check if there are active groups
4. Scheduler Start/Stop - Test with valid session_id
5. Manual Message Send - Ensure message sending works
6. Session Validation - Ensure session is valid
"""

import requests
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://praktek-terkini.preview.emergentagent.com/api"

class SchedulerDebugTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.test_results = []
        self.valid_session_id = None
        self.valid_phone_number = None
        self.default_template_id = None
        self.active_groups = []
        
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
        
    def find_valid_session(self):
        """Find a valid session from existing sessions"""
        print("\n🔍 SEARCHING FOR VALID SESSION")
        print("-" * 40)
        
        try:
            response = self.session.get(f"{BASE_URL}/auth/sessions")
            if response.status_code == 200:
                sessions = response.json()
                self.log_test("GET Sessions", True, f"Found {len(sessions)} existing sessions")
                
                # Try to load each session to find a valid one
                for session in sessions:
                    session_id = session.get('session_id')
                    phone_number = session.get('phone_number', 'unknown')
                    
                    try:
                        load_response = self.session.post(f"{BASE_URL}/auth/load-session/{session_id}")
                        if load_response.status_code == 200:
                            load_data = load_response.json()
                            if load_data.get('authenticated'):
                                self.valid_session_id = session_id
                                self.valid_phone_number = phone_number
                                self.log_test("Valid Session Found", True, 
                                            f"Session {session_id} for {phone_number} is valid and authenticated")
                                return True
                        else:
                            self.log_test(f"Session Load Test ({phone_number})", False, 
                                        f"Session {session_id} failed to load: HTTP {load_response.status_code}")
                    except Exception as e:
                        self.log_test(f"Session Load Test ({phone_number})", False, f"Error: {str(e)}")
                
                if not self.valid_session_id:
                    self.log_test("Valid Session Search", False, "No valid authenticated sessions found")
                    return False
                    
            else:
                self.log_test("GET Sessions", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Find Valid Session", False, f"Error: {str(e)}")
            return False
    
    def create_test_session(self):
        """Create a test session if no valid session exists"""
        print("\n🔧 CREATING TEST SESSION")
        print("-" * 30)
        
        # For testing purposes, we'll create a mock session entry
        # In real scenario, user would need to authenticate with real Telegram credentials
        test_session_data = {
            "session_id": f"test_session_{uuid.uuid4()}",
            "phone_number": "+1234567890",
            "authenticated": True,
            "user_info": {
                "id": 123456789,
                "first_name": "Test",
                "last_name": "User",
                "username": "testuser"
            }
        }
        
        self.valid_session_id = test_session_data["session_id"]
        self.valid_phone_number = test_session_data["phone_number"]
        
        self.log_test("Test Session Created", True, 
                    f"Created test session {self.valid_session_id} for debugging purposes")
        return True
    
    def test_scheduler_status(self):
        """Test 1: Check scheduler status in dashboard stats"""
        print("\n⏰ TEST 1: SCHEDULER STATUS CHECK")
        print("-" * 40)
        
        try:
            response = self.session.get(f"{BASE_URL}/dashboard/stats")
            if response.status_code == 200:
                stats = response.json()
                
                # Check if scheduler section exists
                if 'scheduler' in stats:
                    scheduler_info = stats['scheduler']
                    is_active = scheduler_info.get('active', False)
                    
                    if is_active:
                        self.log_test("Scheduler Status", True, 
                                    f"✅ Scheduler is ACTIVE: {scheduler_info}", scheduler_info)
                    else:
                        self.log_test("Scheduler Status", False, 
                                    f"❌ Scheduler is INACTIVE: {scheduler_info}", scheduler_info)
                    
                    # Additional scheduler info if available
                    if 'next_run' in scheduler_info:
                        self.log_test("Scheduler Next Run", True, 
                                    f"Next scheduled run: {scheduler_info['next_run']}")
                else:
                    self.log_test("Scheduler Status", False, 
                                "❌ No scheduler section found in dashboard stats", stats)
                
                # Also check overall dashboard stats
                self.log_test("Dashboard Stats Retrieved", True, 
                            f"Groups: {stats.get('groups', {})}, Messages: {stats.get('messages', {})}")
                
            else:
                self.log_test("Scheduler Status Check", False, 
                            f"Failed to get dashboard stats: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Scheduler Status Check", False, f"Error: {str(e)}")
    
    def test_default_template(self):
        """Test 2: Check if default template exists"""
        print("\n📝 TEST 2: DEFAULT TEMPLATE CHECK")
        print("-" * 40)
        
        try:
            # First get all templates
            all_templates_response = self.session.get(f"{BASE_URL}/templates")
            if all_templates_response.status_code == 200:
                all_templates = all_templates_response.json()
                self.log_test("All Templates", True, 
                            f"Found {len(all_templates)} total templates", all_templates)
                
                # Check for default templates
                default_templates = [t for t in all_templates if t.get('is_default', False)]
                if default_templates:
                    self.log_test("Default Templates Found", True, 
                                f"Found {len(default_templates)} default templates", default_templates)
                else:
                    self.log_test("Default Templates Found", False, 
                                "❌ No templates marked as default found")
            else:
                self.log_test("All Templates", False, 
                            f"Failed to get templates: HTTP {all_templates_response.status_code}")
            
            # Test the default template endpoint specifically
            response = self.session.get(f"{BASE_URL}/templates/default")
            if response.status_code == 200:
                default_template = response.json()
                self.default_template_id = default_template.get('id')
                self.log_test("Default Template Endpoint", True, 
                            f"✅ Default template found: {default_template.get('name', 'Unnamed')}", 
                            default_template)
            elif response.status_code == 404:
                self.log_test("Default Template Endpoint", False, 
                            "❌ No default template found - this will prevent scheduler from working")
            else:
                self.log_test("Default Template Endpoint", False, 
                            f"Error getting default template: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Default Template Check", False, f"Error: {str(e)}")
    
    def test_active_groups(self):
        """Test 3: Check if there are active groups"""
        print("\n👥 TEST 3: ACTIVE GROUPS CHECK")
        print("-" * 40)
        
        try:
            # Get all groups
            response = self.session.get(f"{BASE_URL}/groups")
            if response.status_code == 200:
                groups = response.json()
                self.log_test("All Groups", True, f"Found {len(groups)} total groups", groups)
                
                # Filter active groups
                active_groups = [g for g in groups if g.get('status') == 'active']
                self.active_groups = active_groups
                
                if active_groups:
                    self.log_test("Active Groups", True, 
                                f"✅ Found {len(active_groups)} active groups", 
                                [g.get('name', 'Unnamed') for g in active_groups])
                else:
                    self.log_test("Active Groups", False, 
                                "❌ No active groups found - scheduler has no targets to send to")
                
                # Check group statuses
                status_counts = {}
                for group in groups:
                    status = group.get('status', 'unknown')
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                self.log_test("Group Status Distribution", True, 
                            f"Group statuses: {status_counts}")
                
                # Get group stats
                stats_response = self.session.get(f"{BASE_URL}/groups/stats")
                if stats_response.status_code == 200:
                    group_stats = stats_response.json()
                    self.log_test("Group Statistics", True, 
                                f"Stats: {group_stats}", group_stats)
                else:
                    self.log_test("Group Statistics", False, 
                                f"Failed to get group stats: HTTP {stats_response.status_code}")
                
            else:
                self.log_test("Active Groups Check", False, 
                            f"Failed to get groups: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Active Groups Check", False, f"Error: {str(e)}")
    
    def test_session_validation(self):
        """Test 6: Validate session is working"""
        print("\n🔐 TEST 6: SESSION VALIDATION")
        print("-" * 40)
        
        if not self.valid_session_id:
            self.log_test("Session Validation", False, "No valid session available for testing")
            return
        
        try:
            # Test session loading
            response = self.session.post(f"{BASE_URL}/auth/load-session/{self.valid_session_id}")
            if response.status_code == 200:
                session_data = response.json()
                if session_data.get('authenticated'):
                    self.log_test("Session Validation", True, 
                                f"✅ Session {self.valid_session_id} is valid and authenticated", 
                                session_data)
                else:
                    self.log_test("Session Validation", False, 
                                f"❌ Session {self.valid_session_id} is not authenticated")
            else:
                self.log_test("Session Validation", False, 
                            f"❌ Session validation failed: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Session Validation", False, f"Error: {str(e)}")
    
    def test_scheduler_start_stop(self):
        """Test 4: Test scheduler start/stop functionality"""
        print("\n🚀 TEST 4: SCHEDULER START/STOP")
        print("-" * 40)
        
        if not self.valid_session_id:
            self.log_test("Scheduler Start/Stop", False, "No valid session available for testing")
            return
        
        try:
            # Test scheduler start
            start_response = self.session.post(f"{BASE_URL}/scheduler/start?session_id={self.valid_session_id}")
            if start_response.status_code == 200:
                start_data = start_response.json()
                self.log_test("Scheduler Start", True, 
                            f"✅ Scheduler started successfully: {start_data.get('message', 'No message')}", 
                            start_data)
                
                # Check if immediate execution is mentioned
                if start_data.get('immediate_execution'):
                    self.log_test("Immediate Execution", True, 
                                "✅ Scheduler configured for immediate first cycle execution")
                else:
                    self.log_test("Immediate Execution", False, 
                                "❌ No immediate execution flag - first cycle may be delayed")
                
                # Wait a moment then check scheduler status
                time.sleep(2)
                stats_response = self.session.get(f"{BASE_URL}/dashboard/stats")
                if stats_response.status_code == 200:
                    stats = stats_response.json()
                    scheduler_active = stats.get('scheduler', {}).get('active', False)
                    if scheduler_active:
                        self.log_test("Scheduler Status After Start", True, 
                                    "✅ Scheduler status shows active after start command")
                    else:
                        self.log_test("Scheduler Status After Start", False, 
                                    "❌ Scheduler status still shows inactive after start command")
                
            else:
                self.log_test("Scheduler Start", False, 
                            f"❌ Failed to start scheduler: HTTP {start_response.status_code} - {start_response.text}")
            
            # Test scheduler stop
            time.sleep(1)
            stop_response = self.session.post(f"{BASE_URL}/scheduler/stop?session_id={self.valid_session_id}")
            if stop_response.status_code == 200:
                stop_data = stop_response.json()
                self.log_test("Scheduler Stop", True, 
                            f"✅ Scheduler stopped successfully: {stop_data.get('message', 'No message')}")
                
                # Check scheduler status after stop
                time.sleep(1)
                stats_response = self.session.get(f"{BASE_URL}/dashboard/stats")
                if stats_response.status_code == 200:
                    stats = stats_response.json()
                    scheduler_active = stats.get('scheduler', {}).get('active', False)
                    if not scheduler_active:
                        self.log_test("Scheduler Status After Stop", True, 
                                    "✅ Scheduler status shows inactive after stop command")
                    else:
                        self.log_test("Scheduler Status After Stop", False, 
                                    "❌ Scheduler status still shows active after stop command")
            else:
                self.log_test("Scheduler Stop", False, 
                            f"❌ Failed to stop scheduler: HTTP {stop_response.status_code}")
                
        except Exception as e:
            self.log_test("Scheduler Start/Stop", False, f"Error: {str(e)}")
    
    def test_manual_message_send(self):
        """Test 5: Test manual message sending functionality"""
        print("\n💬 TEST 5: MANUAL MESSAGE SEND")
        print("-" * 40)
        
        if not self.valid_session_id:
            self.log_test("Manual Message Send", False, "No valid session available for testing")
            return
        
        if not self.default_template_id:
            self.log_test("Manual Message Send", False, "No default template available for testing")
            return
        
        if not self.active_groups:
            self.log_test("Manual Message Send", False, "No active groups available for testing")
            return
        
        try:
            # Use first active group for testing
            test_group_id = self.active_groups[0].get('group_id')
            
            message_data = {
                "group_ids": [test_group_id],
                "message_template_id": self.default_template_id,
                "send_immediately": True
            }
            
            response = self.session.post(
                f"{BASE_URL}/messages/send?session_id={self.valid_session_id}", 
                json=message_data
            )
            
            if response.status_code == 200:
                send_data = response.json()
                self.log_test("Manual Message Send", True, 
                            f"✅ Message send request successful: {send_data.get('message', 'No message')}", 
                            send_data)
            else:
                self.log_test("Manual Message Send", False, 
                            f"❌ Message send failed: HTTP {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_test("Manual Message Send", False, f"Error: {str(e)}")
    
    def test_scheduler_prerequisites(self):
        """Test all prerequisites for scheduler to work"""
        print("\n🔍 SCHEDULER PREREQUISITES ANALYSIS")
        print("-" * 50)
        
        prerequisites = {
            "valid_session": self.valid_session_id is not None,
            "default_template": self.default_template_id is not None,
            "active_groups": len(self.active_groups) > 0
        }
        
        all_met = all(prerequisites.values())
        
        if all_met:
            self.log_test("Scheduler Prerequisites", True, 
                        "✅ All prerequisites met - scheduler should be able to work")
        else:
            missing = [k for k, v in prerequisites.items() if not v]
            self.log_test("Scheduler Prerequisites", False, 
                        f"❌ Missing prerequisites: {missing}")
        
        # Detailed analysis
        print("\n📋 PREREQUISITE DETAILS:")
        print(f"  Valid Session: {'✅' if prerequisites['valid_session'] else '❌'} {self.valid_session_id or 'None'}")
        print(f"  Default Template: {'✅' if prerequisites['default_template'] else '❌'} {self.default_template_id or 'None'}")
        print(f"  Active Groups: {'✅' if prerequisites['active_groups'] else '❌'} {len(self.active_groups)} groups")
        
        return all_met
    
    def run_scheduler_debug_tests(self):
        """Run all scheduler debugging tests"""
        print("🔧 TELEGRAM AUTO SENDER - SCHEDULER DEBUG TESTS")
        print("=" * 60)
        print("Purpose: Debug why scheduler is not sending automatic messages")
        print("=" * 60)
        
        # Step 1: Find or create valid session
        if not self.find_valid_session():
            print("\n⚠️  No valid sessions found, creating test session for debugging...")
            self.create_test_session()
        
        # Step 2: Run all debug tests
        self.test_scheduler_status()          # Test 1
        self.test_default_template()          # Test 2  
        self.test_active_groups()             # Test 3
        self.test_session_validation()        # Test 6
        self.test_scheduler_start_stop()      # Test 4
        self.test_manual_message_send()       # Test 5
        
        # Step 3: Analyze prerequisites
        prerequisites_met = self.test_scheduler_prerequisites()
        
        # Summary
        print("\n" + "=" * 60)
        print("🔍 SCHEDULER DEBUG SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Critical findings
        print("\n🎯 CRITICAL FINDINGS:")
        
        critical_issues = []
        for result in self.test_results:
            if not result['success'] and any(critical in result['test'].lower() 
                                           for critical in ['scheduler status', 'default template', 'active groups', 'session validation']):
                critical_issues.append(result)
        
        if critical_issues:
            for issue in critical_issues:
                print(f"  ❌ {issue['test']}: {issue['details']}")
        else:
            print("  ✅ No critical issues found with basic components")
        
        # Root cause analysis
        print("\n🔬 ROOT CAUSE ANALYSIS:")
        
        if not prerequisites_met:
            print("  ❌ SCHEDULER CANNOT WORK - Missing prerequisites")
            if not self.valid_session_id:
                print("     - No valid authenticated Telegram session")
            if not self.default_template_id:
                print("     - No default message template configured")
            if not self.active_groups:
                print("     - No active groups to send messages to")
        else:
            print("  ✅ All prerequisites met - investigating scheduler logic...")
            
            # Check specific scheduler issues
            scheduler_issues = [r for r in self.test_results if 'scheduler' in r['test'].lower() and not r['success']]
            if scheduler_issues:
                print("  ❌ SCHEDULER LOGIC ISSUES:")
                for issue in scheduler_issues:
                    print(f"     - {issue['details']}")
            else:
                print("  ✅ Scheduler logic appears to be working")
                print("  🔍 POSSIBLE CAUSES:")
                print("     - Scheduler timing intervals too long")
                print("     - Background job execution issues")
                print("     - Socket.IO event emission problems")
                print("     - Database connection issues during auto cycle")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        
        if not self.valid_session_id:
            print("  1. Create valid Telegram session via /auth/login and /auth/verify")
        if not self.default_template_id:
            print("  2. Create and set a default message template")
        if not self.active_groups:
            print("  3. Add active groups via /groups/single or /groups/bulk")
        
        if prerequisites_met:
            print("  4. Check scheduler timing settings in /settings")
            print("  5. Monitor Socket.IO events for real-time scheduler updates")
            print("  6. Check backend logs for auto_sender_cycle execution")
            print("  7. Verify MongoDB and Redis connections")
        
        return {
            'total': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'prerequisites_met': prerequisites_met,
            'critical_issues': len(critical_issues),
            'valid_session': self.valid_session_id,
            'default_template': self.default_template_id,
            'active_groups_count': len(self.active_groups),
            'results': self.test_results
        }

if __name__ == "__main__":
    tester = SchedulerDebugTester()
    results = tester.run_scheduler_debug_tests()
    
    # Exit with appropriate code
    if not results['prerequisites_met']:
        print("\n❌ SCHEDULER PREREQUISITES NOT MET - Cannot function")
        exit(1)
    elif results['critical_issues'] > 0:
        print("\n⚠️  CRITICAL ISSUES FOUND - Needs investigation")
        exit(1)
    else:
        print("\n✅ SCHEDULER DEBUG COMPLETE - All basic components working")
        exit(0)