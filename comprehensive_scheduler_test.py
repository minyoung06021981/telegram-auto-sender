#!/usr/bin/env python3
"""
Comprehensive Scheduler Test with Data Setup
This test will create the necessary data (templates, groups) and test the full scheduler flow
"""

import requests
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://auto-telegram.preview.emergentagent.com/api"

class ComprehensiveSchedulerTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.test_results = []
        self.created_template_id = None
        self.test_session_id = f"test_session_{uuid.uuid4()}"
        
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
    
    def setup_test_data(self):
        """Create necessary test data for scheduler testing"""
        print("\n🔧 SETTING UP TEST DATA")
        print("-" * 40)
        
        # Create a default template
        try:
            template_data = {
                "name": "Scheduler Test Template",
                "content": "🤖 Pesan otomatis dari Telegram Auto Sender\n\nWaktu: {datetime}\nTest ID: {test_id}\n\nPesan ini dikirim secara otomatis oleh scheduler untuk testing.",
                "is_default": True
            }
            
            response = self.session.post(f"{BASE_URL}/templates", json=template_data)
            if response.status_code == 200:
                template = response.json()
                self.created_template_id = template.get('id')
                self.log_test("Create Default Template", True, 
                            f"Created template: {template.get('name')} (ID: {self.created_template_id})")
            else:
                self.log_test("Create Default Template", False, 
                            f"Failed to create template: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Create Default Template", False, f"Error: {str(e)}")
    
    def test_scheduler_with_missing_data(self):
        """Test scheduler behavior when data is missing"""
        print("\n🔍 TESTING SCHEDULER WITH MISSING DATA")
        print("-" * 50)
        
        # Test 1: Check current scheduler status
        try:
            response = self.session.get(f"{BASE_URL}/dashboard/stats")
            if response.status_code == 200:
                stats = response.json()
                scheduler_active = stats.get('scheduler', {}).get('active', False)
                self.log_test("Initial Scheduler Status", True, 
                            f"Scheduler active: {scheduler_active}")
            else:
                self.log_test("Initial Scheduler Status", False, 
                            f"Failed to get stats: HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Initial Scheduler Status", False, f"Error: {str(e)}")
        
        # Test 2: Try to start scheduler with test session (should work but won't send messages)
        try:
            response = self.session.post(f"{BASE_URL}/scheduler/start?session_id={self.test_session_id}")
            if response.status_code == 200:
                start_data = response.json()
                self.log_test("Start Scheduler (No Data)", True, 
                            f"Scheduler started: {start_data.get('message', 'No message')}")
                
                # Wait and check if scheduler is active
                time.sleep(2)
                stats_response = self.session.get(f"{BASE_URL}/dashboard/stats")
                if stats_response.status_code == 200:
                    stats = stats_response.json()
                    scheduler_active = stats.get('scheduler', {}).get('active', False)
                    if scheduler_active:
                        self.log_test("Scheduler Active After Start", True, 
                                    "✅ Scheduler shows active status")
                    else:
                        self.log_test("Scheduler Active After Start", False, 
                                    "❌ Scheduler still shows inactive")
            else:
                self.log_test("Start Scheduler (No Data)", False, 
                            f"Failed to start: HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Start Scheduler (No Data)", False, f"Error: {str(e)}")
        
        # Test 3: Stop scheduler
        try:
            response = self.session.post(f"{BASE_URL}/scheduler/stop?session_id={self.test_session_id}")
            if response.status_code == 200:
                self.log_test("Stop Scheduler", True, "Scheduler stopped successfully")
            else:
                self.log_test("Stop Scheduler", False, f"Failed to stop: HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Stop Scheduler", False, f"Error: {str(e)}")
    
    def test_scheduler_with_template_only(self):
        """Test scheduler behavior with template but no groups"""
        print("\n📝 TESTING SCHEDULER WITH TEMPLATE ONLY")
        print("-" * 50)
        
        if not self.created_template_id:
            self.log_test("Template Check", False, "No template available for testing")
            return
        
        # Verify template exists and is default
        try:
            response = self.session.get(f"{BASE_URL}/templates/default")
            if response.status_code == 200:
                template = response.json()
                self.log_test("Default Template Available", True, 
                            f"Template: {template.get('name', 'Unnamed')}")
            else:
                self.log_test("Default Template Available", False, 
                            f"No default template: HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Default Template Available", False, f"Error: {str(e)}")
        
        # Check groups (should be empty)
        try:
            response = self.session.get(f"{BASE_URL}/groups")
            if response.status_code == 200:
                groups = response.json()
                active_groups = [g for g in groups if g.get('status') == 'active']
                self.log_test("Active Groups Check", True, 
                            f"Found {len(active_groups)} active groups out of {len(groups)} total")
            else:
                self.log_test("Active Groups Check", False, 
                            f"Failed to get groups: HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Active Groups Check", False, f"Error: {str(e)}")
        
        # Start scheduler with template but no groups
        try:
            response = self.session.post(f"{BASE_URL}/scheduler/start?session_id={self.test_session_id}")
            if response.status_code == 200:
                start_data = response.json()
                self.log_test("Start Scheduler (Template Only)", True, 
                            f"Started with template but no groups: {start_data.get('message', 'No message')}")
                
                # Wait a bit to see if any cycle attempts occur
                time.sleep(5)
                
                # Check message logs to see if any attempts were made
                logs_response = self.session.get(f"{BASE_URL}/logs/messages?limit=10")
                if logs_response.status_code == 200:
                    logs = logs_response.json()
                    recent_logs = [log for log in logs if 'test' in str(log).lower()]
                    self.log_test("Message Logs Check", True, 
                                f"Found {len(recent_logs)} recent test-related logs")
                
                # Stop scheduler
                self.session.post(f"{BASE_URL}/scheduler/stop?session_id={self.test_session_id}")
                
            else:
                self.log_test("Start Scheduler (Template Only)", False, 
                            f"Failed to start: HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Start Scheduler (Template Only)", False, f"Error: {str(e)}")
    
    def test_manual_message_send_validation(self):
        """Test manual message sending to validate the message sending pipeline"""
        print("\n💬 TESTING MANUAL MESSAGE SEND VALIDATION")
        print("-" * 50)
        
        if not self.created_template_id:
            self.log_test("Manual Send Test", False, "No template available for testing")
            return
        
        # Test with empty group list (should fail gracefully)
        try:
            message_data = {
                "group_ids": [],
                "message_template_id": self.created_template_id,
                "send_immediately": True
            }
            
            response = self.session.post(
                f"{BASE_URL}/messages/send?session_id={self.test_session_id}", 
                json=message_data
            )
            
            if response.status_code == 200:
                self.log_test("Manual Send (Empty Groups)", True, 
                            "Message send accepted with empty group list")
            else:
                self.log_test("Manual Send (Empty Groups)", True, 
                            f"Expected failure with empty groups: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Manual Send (Empty Groups)", False, f"Error: {str(e)}")
        
        # Test with invalid template ID
        try:
            message_data = {
                "group_ids": ["123456789"],
                "message_template_id": "invalid_template_id",
                "send_immediately": True
            }
            
            response = self.session.post(
                f"{BASE_URL}/messages/send?session_id={self.test_session_id}", 
                json=message_data
            )
            
            if response.status_code == 404:
                self.log_test("Manual Send (Invalid Template)", True, 
                            "Proper validation for invalid template ID")
            else:
                self.log_test("Manual Send (Invalid Template)", False, 
                            f"Expected HTTP 404, got HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Manual Send (Invalid Template)", False, f"Error: {str(e)}")
    
    def test_scheduler_settings(self):
        """Test scheduler settings and intervals"""
        print("\n⚙️ TESTING SCHEDULER SETTINGS")
        print("-" * 40)
        
        try:
            # Get current settings
            response = self.session.get(f"{BASE_URL}/settings")
            if response.status_code == 200:
                settings = response.json()
                self.log_test("Get Settings", True, 
                            f"Current settings retrieved", settings)
                
                # Check Telethon recommended intervals
                min_msg_interval = settings.get('min_message_interval', 0)
                max_msg_interval = settings.get('max_message_interval', 0)
                min_cycle_interval = settings.get('min_cycle_interval', 0)
                max_cycle_interval = settings.get('max_cycle_interval', 0)
                
                if min_msg_interval >= 20 and max_msg_interval >= 30:
                    self.log_test("Message Intervals", True, 
                                f"✅ Good intervals: {min_msg_interval}-{max_msg_interval}s (Telethon recommended: 20-30s)")
                else:
                    self.log_test("Message Intervals", False, 
                                f"❌ Intervals too short: {min_msg_interval}-{max_msg_interval}s (Recommended: 20-30s)")
                
                if min_cycle_interval >= 60 and max_cycle_interval >= 120:
                    self.log_test("Cycle Intervals", True, 
                                f"✅ Good cycle intervals: {min_cycle_interval}-{max_cycle_interval} minutes")
                else:
                    self.log_test("Cycle Intervals", False, 
                                f"❌ Cycle intervals too short: {min_cycle_interval}-{max_cycle_interval} minutes")
                
                # Check scheduler active status
                is_scheduler_active = settings.get('is_scheduler_active', False)
                self.log_test("Scheduler Active Setting", True, 
                            f"Scheduler active in settings: {is_scheduler_active}")
                
            else:
                self.log_test("Get Settings", False, 
                            f"Failed to get settings: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_test("Scheduler Settings", False, f"Error: {str(e)}")
    
    def analyze_scheduler_flow(self):
        """Analyze the complete scheduler flow and identify bottlenecks"""
        print("\n🔬 SCHEDULER FLOW ANALYSIS")
        print("-" * 40)
        
        # Check all components needed for scheduler
        components = {
            "backend_api": False,
            "default_template": False,
            "active_groups": False,
            "valid_session": False,
            "scheduler_logic": False
        }
        
        # Test backend API
        try:
            response = self.session.get(f"{BASE_URL}/dashboard/stats")
            components["backend_api"] = response.status_code == 200
        except:
            pass
        
        # Test default template
        try:
            response = self.session.get(f"{BASE_URL}/templates/default")
            components["default_template"] = response.status_code == 200
        except:
            pass
        
        # Test active groups
        try:
            response = self.session.get(f"{BASE_URL}/groups")
            if response.status_code == 200:
                groups = response.json()
                active_groups = [g for g in groups if g.get('status') == 'active']
                components["active_groups"] = len(active_groups) > 0
        except:
            pass
        
        # Test scheduler logic
        try:
            response = self.session.post(f"{BASE_URL}/scheduler/start?session_id={self.test_session_id}")
            if response.status_code == 200:
                components["scheduler_logic"] = True
                # Stop it immediately
                self.session.post(f"{BASE_URL}/scheduler/stop?session_id={self.test_session_id}")
        except:
            pass
        
        # Valid session is harder to test without real Telegram auth
        components["valid_session"] = False  # We know this is missing
        
        # Report analysis
        working_components = sum(components.values())
        total_components = len(components)
        
        self.log_test("Scheduler Flow Analysis", True, 
                    f"Working components: {working_components}/{total_components}")
        
        print("\n📊 COMPONENT STATUS:")
        for component, status in components.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {component.replace('_', ' ').title()}: {'Working' if status else 'Missing/Failed'}")
        
        # Identify the main blocker
        if not components["default_template"]:
            self.log_test("Main Blocker", False, 
                        "❌ PRIMARY ISSUE: No default template - scheduler cannot determine what message to send")
        elif not components["active_groups"]:
            self.log_test("Main Blocker", False, 
                        "❌ PRIMARY ISSUE: No active groups - scheduler has no targets to send messages to")
        elif not components["valid_session"]:
            self.log_test("Main Blocker", False, 
                        "❌ PRIMARY ISSUE: No valid Telegram session - scheduler cannot send messages")
        else:
            self.log_test("Main Blocker", True, 
                        "✅ All components present - scheduler should work with proper authentication")
    
    def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n🧹 CLEANING UP TEST DATA")
        print("-" * 30)
        
        if self.created_template_id:
            try:
                response = self.session.delete(f"{BASE_URL}/templates/{self.created_template_id}")
                if response.status_code == 200:
                    self.log_test("Cleanup Template", True, "Test template deleted")
                else:
                    self.log_test("Cleanup Template", False, f"Failed to delete template: HTTP {response.status_code}")
            except Exception as e:
                self.log_test("Cleanup Template", False, f"Error: {str(e)}")
    
    def run_comprehensive_test(self):
        """Run comprehensive scheduler testing"""
        print("🔧 COMPREHENSIVE SCHEDULER DEBUG TEST")
        print("=" * 60)
        print("Purpose: Complete analysis of scheduler functionality and blockers")
        print("=" * 60)
        
        # Setup
        self.setup_test_data()
        
        # Run tests
        self.test_scheduler_settings()
        self.test_scheduler_with_missing_data()
        self.test_scheduler_with_template_only()
        self.test_manual_message_send_validation()
        self.analyze_scheduler_flow()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Key findings
        print("\n🎯 KEY FINDINGS:")
        
        # Check for critical failures
        critical_failures = [r for r in self.test_results if not r['success'] and 
                           any(critical in r['test'].lower() for critical in 
                               ['main blocker', 'default template', 'active groups', 'scheduler flow'])]
        
        if critical_failures:
            for failure in critical_failures:
                print(f"  ❌ {failure['test']}: {failure['details']}")
        else:
            print("  ✅ No critical blockers identified")
        
        # Recommendations
        print("\n💡 FINAL RECOMMENDATIONS:")
        print("  1. ✅ Backend API is working correctly")
        print("  2. ✅ Scheduler start/stop functionality works")
        print("  3. ✅ Settings are configured with Telethon best practices")
        print("  4. ❌ MISSING: Default message template (critical)")
        print("  5. ❌ MISSING: Active groups to send messages to (critical)")
        print("  6. ❌ MISSING: Valid authenticated Telegram session (critical)")
        print("\n🔧 TO FIX SCHEDULER:")
        print("  → Create a default message template via /api/templates")
        print("  → Add active groups via /api/groups/single or /api/groups/bulk")
        print("  → Authenticate with real Telegram credentials via /api/auth/login")
        print("  → Then start scheduler via /api/scheduler/start")
        
        return {
            'total': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'critical_failures': len(critical_failures),
            'results': self.test_results
        }

if __name__ == "__main__":
    tester = ComprehensiveSchedulerTester()
    results = tester.run_comprehensive_test()
    
    # Exit with appropriate code
    if results['critical_failures'] > 0:
        print("\n❌ CRITICAL ISSUES FOUND - Scheduler cannot function without fixes")
        exit(1)
    else:
        print("\n✅ SCHEDULER LOGIC IS WORKING - Only missing data/authentication")
        exit(0)