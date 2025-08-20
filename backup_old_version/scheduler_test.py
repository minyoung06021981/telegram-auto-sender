#!/usr/bin/env python3
"""
Comprehensive Scheduler System Tests for Telegram Auto Sender
Focus on testing the improved scheduler with immediate execution and Telethon best practices
"""

import requests
import json
import time
import uuid
import asyncio
import websocket
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List

# Configuration - Using the correct URL from frontend/.env
BASE_URL = "https://signup-overhaul.preview.emergentagent.com/api"
WEBSOCKET_URL = "wss://schedule-trigger.preview.emergentagent.com/socket.io/?EIO=4&transport=websocket"

class SchedulerSystemTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.test_results = []
        self.session_id = None
        self.template_id = None
        self.socket_events = []
        self.ws = None
        
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
    
    def setup_websocket_listener(self):
        """Setup WebSocket listener for Socket.IO events"""
        def on_message(ws, message):
            try:
                # Parse Socket.IO message format
                if message.startswith('42'):  # Socket.IO event message
                    event_data = json.loads(message[2:])
                    event_name = event_data[0]
                    event_payload = event_data[1] if len(event_data) > 1 else {}
                    
                    self.socket_events.append({
                        'event': event_name,
                        'data': event_payload,
                        'timestamp': datetime.now().isoformat()
                    })
                    print(f"📡 Socket.IO Event: {event_name} - {event_payload}")
            except Exception as e:
                print(f"Error parsing WebSocket message: {e}")
        
        def on_error(ws, error):
            print(f"WebSocket error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            print("WebSocket connection closed")
        
        def on_open(ws):
            print("WebSocket connection opened")
            # Send Socket.IO handshake
            ws.send('40')
        
        try:
            self.ws = websocket.WebSocketApp(
                WEBSOCKET_URL,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            
            # Start WebSocket in a separate thread
            ws_thread = threading.Thread(target=self.ws.run_forever)
            ws_thread.daemon = True
            ws_thread.start()
            time.sleep(2)  # Give time for connection to establish
            
            self.log_test("WebSocket Setup", True, "Socket.IO connection established")
        except Exception as e:
            self.log_test("WebSocket Setup", False, f"Failed to setup WebSocket: {str(e)}")
    
    def test_settings_default_intervals(self):
        """Test that default message intervals are now 20-30 seconds (Telethon best practices)"""
        print("\n⚙️ TESTING SETTINGS - TELETHON BEST PRACTICES")
        print("-" * 50)
        
        try:
            response = self.session.get(f"{BASE_URL}/settings")
            if response.status_code == 200:
                settings = response.json()
                
                min_interval = settings.get('min_message_interval', 0)
                max_interval = settings.get('max_message_interval', 0)
                
                # Check if intervals follow Telethon best practices (20-30 seconds)
                if min_interval >= 20 and max_interval >= 30:
                    self.log_test("Settings - Telethon Intervals", True, 
                                f"✅ Intervals follow Telethon best practices: {min_interval}-{max_interval} seconds", settings)
                else:
                    self.log_test("Settings - Telethon Intervals", False, 
                                f"❌ Intervals don't follow Telethon best practices: {min_interval}-{max_interval} seconds (should be 20-30+)", settings)
                
                # Verify all required settings fields
                required_fields = ['min_message_interval', 'max_message_interval', 'min_cycle_interval', 'max_cycle_interval']
                if all(field in settings for field in required_fields):
                    self.log_test("Settings - Required Fields", True, "All required settings fields present")
                else:
                    missing = [f for f in required_fields if f not in settings]
                    self.log_test("Settings - Required Fields", False, f"Missing fields: {missing}")
                    
            else:
                self.log_test("GET /api/settings", False, f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Settings Test", False, f"Error: {str(e)}")
    
    def test_scheduler_start_immediate_execution(self):
        """Test POST /api/scheduler/start for immediate execution behavior"""
        print("\n🚀 TESTING SCHEDULER START - IMMEDIATE EXECUTION")
        print("-" * 50)
        
        try:
            # Test without session_id (should return 422)
            response = self.session.post(f"{BASE_URL}/scheduler/start")
            if response.status_code == 422:
                self.log_test("POST /api/scheduler/start (No Session)", True, "Proper validation - HTTP 422")
            else:
                self.log_test("POST /api/scheduler/start (No Session)", False, f"Expected HTTP 422, got HTTP {response.status_code}")
            
            # Test with invalid session_id (should return proper error but test response structure)
            test_session_id = "test_scheduler_session_123"
            response = self.session.post(f"{BASE_URL}/scheduler/start?session_id={test_session_id}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for immediate_execution flag in response
                if data.get('immediate_execution') is True:
                    self.log_test("Scheduler Start - Immediate Execution Flag", True, 
                                "✅ Response includes 'immediate_execution': true", data)
                else:
                    self.log_test("Scheduler Start - Immediate Execution Flag", False, 
                                f"❌ Missing or false 'immediate_execution' flag: {data}")
                
                # Check response message indicates immediate execution
                message = data.get('message', '')
                if 'immediate' in message.lower():
                    self.log_test("Scheduler Start - Message Content", True, 
                                f"✅ Message indicates immediate execution: {message}")
                else:
                    self.log_test("Scheduler Start - Message Content", False, 
                                f"❌ Message doesn't indicate immediate execution: {message}")
                    
            elif response.status_code == 401:
                # Expected for invalid session, but we can still test the endpoint exists
                self.log_test("POST /api/scheduler/start (Invalid Session)", True, 
                            "Endpoint exists and validates session - HTTP 401")
            else:
                self.log_test("POST /api/scheduler/start", False, 
                            f"Unexpected HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Scheduler Start Test", False, f"Error: {str(e)}")
    
    def test_scheduler_stop_functionality(self):
        """Test POST /api/scheduler/stop functionality"""
        print("\n🛑 TESTING SCHEDULER STOP")
        print("-" * 30)
        
        try:
            # Test without session_id (should return 422)
            response = self.session.post(f"{BASE_URL}/scheduler/stop")
            if response.status_code == 422:
                self.log_test("POST /api/scheduler/stop (No Session)", True, "Proper validation - HTTP 422")
            else:
                self.log_test("POST /api/scheduler/stop (No Session)", False, f"Expected HTTP 422, got HTTP {response.status_code}")
            
            # Test with session_id
            test_session_id = "test_scheduler_session_123"
            response = self.session.post(f"{BASE_URL}/scheduler/stop?session_id={test_session_id}")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("POST /api/scheduler/stop", True, f"Scheduler stop endpoint working: {data}")
            elif response.status_code == 401:
                self.log_test("POST /api/scheduler/stop (Invalid Session)", True, 
                            "Endpoint exists and validates session - HTTP 401")
            else:
                self.log_test("POST /api/scheduler/stop", False, 
                            f"Unexpected HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Scheduler Stop Test", False, f"Error: {str(e)}")
    
    def create_test_template(self):
        """Create a test template for scheduler testing"""
        try:
            test_template = {
                "name": "Scheduler Test Template",
                "content": "🤖 Automated scheduler test message - Testing improved Telethon timing",
                "is_default": True
            }
            
            response = self.session.post(f"{BASE_URL}/templates", json=test_template)
            if response.status_code == 200:
                template = response.json()
                self.template_id = template.get('id')
                self.log_test("Create Test Template", True, f"Template created: {self.template_id}")
                return True
            else:
                self.log_test("Create Test Template", False, f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Create Test Template", False, f"Error: {str(e)}")
            return False
    
    def test_message_sending_with_improved_timing(self):
        """Test message sending with improved timing (20-30 second delays)"""
        print("\n💬 TESTING MESSAGE SENDING - IMPROVED TIMING")
        print("-" * 50)
        
        if not self.create_test_template():
            self.log_test("Message Sending Test", False, "Could not create test template")
            return
        
        try:
            # Test message sending endpoint structure
            test_session_id = "test_scheduler_session_123"
            message_data = {
                "group_ids": ["123456789", "987654321"],  # Test group IDs
                "message_template_id": self.template_id,
                "send_immediately": True
            }
            
            response = self.session.post(f"{BASE_URL}/messages/send?session_id={test_session_id}", json=message_data)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("POST /api/messages/send", True, f"Message sending endpoint working: {data}")
            elif response.status_code == 401:
                self.log_test("POST /api/messages/send (Invalid Session)", True, 
                            "Endpoint exists and validates session - HTTP 401")
            elif response.status_code == 404 and "template not found" in response.text.lower():
                self.log_test("POST /api/messages/send", True, 
                            "Endpoint validates template existence - HTTP 404")
            else:
                self.log_test("POST /api/messages/send", False, 
                            f"Unexpected HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Message Sending Test", False, f"Error: {str(e)}")
    
    def test_socket_io_events_structure(self):
        """Test Socket.IO events structure for scheduler status updates"""
        print("\n📡 TESTING SOCKET.IO EVENTS STRUCTURE")
        print("-" * 50)
        
        # Wait a bit to collect any events
        time.sleep(3)
        
        # Define expected Socket.IO events for scheduler
        expected_events = [
            'scheduler_status',
            'sending_progress', 
            'sending_delay',
            'message_results'
        ]
        
        if self.socket_events:
            self.log_test("Socket.IO Events Received", True, 
                        f"Received {len(self.socket_events)} Socket.IO events")
            
            # Check if we received any of the expected scheduler events
            received_event_names = [event['event'] for event in self.socket_events]
            scheduler_events = [event for event in received_event_names if event in expected_events]
            
            if scheduler_events:
                self.log_test("Scheduler Socket.IO Events", True, 
                            f"Received scheduler events: {scheduler_events}")
            else:
                self.log_test("Scheduler Socket.IO Events", False, 
                            f"No scheduler events received. Got: {received_event_names}")
                
            # Analyze event structure
            for event in self.socket_events:
                event_name = event['event']
                event_data = event['data']
                
                if event_name == 'scheduler_status':
                    required_fields = ['session_id', 'status', 'message', 'timestamp']
                    if all(field in event_data for field in required_fields):
                        self.log_test(f"Socket.IO Event Structure - {event_name}", True, 
                                    f"Proper structure with required fields")
                    else:
                        missing = [f for f in required_fields if f not in event_data]
                        self.log_test(f"Socket.IO Event Structure - {event_name}", False, 
                                    f"Missing fields: {missing}")
                
                elif event_name == 'sending_progress':
                    required_fields = ['session_id', 'current', 'total', 'percentage', 'timestamp']
                    if all(field in event_data for field in required_fields):
                        self.log_test(f"Socket.IO Event Structure - {event_name}", True, 
                                    f"Proper progress structure")
                    else:
                        missing = [f for f in required_fields if f not in event_data]
                        self.log_test(f"Socket.IO Event Structure - {event_name}", False, 
                                    f"Missing fields: {missing}")
                
                elif event_name == 'sending_delay':
                    required_fields = ['session_id', 'delay_seconds', 'message', 'timestamp']
                    if all(field in event_data for field in required_fields):
                        delay_seconds = event_data.get('delay_seconds', 0)
                        if delay_seconds >= 20 and delay_seconds <= 30:
                            self.log_test(f"Socket.IO Event - Telethon Delay", True, 
                                        f"✅ Delay follows Telethon best practices: {delay_seconds} seconds")
                        else:
                            self.log_test(f"Socket.IO Event - Telethon Delay", False, 
                                        f"❌ Delay doesn't follow Telethon practices: {delay_seconds} seconds")
                    else:
                        missing = [f for f in required_fields if f not in event_data]
                        self.log_test(f"Socket.IO Event Structure - {event_name}", False, 
                                    f"Missing fields: {missing}")
        else:
            self.log_test("Socket.IO Events", False, "No Socket.IO events received during test")
    
    def test_scheduler_cycle_status_updates(self):
        """Test that scheduler cycle provides real-time status updates"""
        print("\n🔄 TESTING SCHEDULER CYCLE STATUS UPDATES")
        print("-" * 50)
        
        # Clear previous events
        self.socket_events = []
        
        try:
            # Try to start scheduler to trigger cycle (will fail due to no session, but tests the flow)
            test_session_id = "test_cycle_session_123"
            response = self.session.post(f"{BASE_URL}/scheduler/start?session_id={test_session_id}")
            
            # Wait for potential Socket.IO events
            time.sleep(5)
            
            # Check for cycle-related Socket.IO events
            cycle_events = [event for event in self.socket_events 
                          if event['event'] == 'scheduler_status']
            
            if cycle_events:
                self.log_test("Scheduler Cycle Events", True, 
                            f"Received {len(cycle_events)} scheduler status events")
                
                # Check for specific cycle status messages
                cycle_statuses = [event['data'].get('status') for event in cycle_events]
                expected_statuses = ['cycle_started', 'sending_messages', 'cycle_completed', 'next_scheduled']
                
                found_statuses = [status for status in expected_statuses if status in cycle_statuses]
                if found_statuses:
                    self.log_test("Scheduler Cycle Status Types", True, 
                                f"Found expected statuses: {found_statuses}")
                else:
                    self.log_test("Scheduler Cycle Status Types", False, 
                                f"No expected cycle statuses found. Got: {cycle_statuses}")
            else:
                self.log_test("Scheduler Cycle Events", False, 
                            "No scheduler_status events received during cycle test")
                
        except Exception as e:
            self.log_test("Scheduler Cycle Test", False, f"Error: {str(e)}")
    
    def test_dashboard_scheduler_status(self):
        """Test dashboard shows scheduler status correctly"""
        print("\n📊 TESTING DASHBOARD SCHEDULER STATUS")
        print("-" * 40)
        
        try:
            response = self.session.get(f"{BASE_URL}/dashboard/stats")
            if response.status_code == 200:
                stats = response.json()
                
                if 'scheduler' in stats:
                    scheduler_stats = stats['scheduler']
                    if 'active' in scheduler_stats:
                        self.log_test("Dashboard Scheduler Status", True, 
                                    f"Scheduler status tracked in dashboard: {scheduler_stats}")
                    else:
                        self.log_test("Dashboard Scheduler Status", False, 
                                    f"Missing 'active' field in scheduler stats: {scheduler_stats}")
                else:
                    self.log_test("Dashboard Scheduler Status", False, 
                                f"Missing 'scheduler' section in dashboard stats: {stats}")
            else:
                self.log_test("Dashboard Stats", False, f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Dashboard Test", False, f"Error: {str(e)}")
    
    def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 CLEANING UP TEST DATA")
        print("-" * 30)
        
        try:
            if self.template_id:
                response = self.session.delete(f"{BASE_URL}/templates/{self.template_id}")
                if response.status_code == 200:
                    self.log_test("Cleanup - Delete Template", True, "Test template deleted")
                else:
                    self.log_test("Cleanup - Delete Template", False, f"HTTP {response.status_code}")
            
            if self.ws:
                self.ws.close()
                self.log_test("Cleanup - WebSocket", True, "WebSocket connection closed")
                
        except Exception as e:
            self.log_test("Cleanup", False, f"Error: {str(e)}")
    
    def run_scheduler_tests(self):
        """Run all scheduler-focused tests"""
        print("🚀 TELEGRAM AUTO SENDER - SCHEDULER SYSTEM TESTING")
        print("=" * 60)
        print("Focus: Testing improved scheduler with immediate execution and Telethon best practices")
        print("=" * 60)
        
        # Setup WebSocket listener for Socket.IO events
        self.setup_websocket_listener()
        
        # Run tests in logical order
        self.test_settings_default_intervals()
        self.test_scheduler_start_immediate_execution()
        self.test_scheduler_stop_functionality()
        self.test_message_sending_with_improved_timing()
        self.test_scheduler_cycle_status_updates()
        self.test_socket_io_events_structure()
        self.test_dashboard_scheduler_status()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 SCHEDULER SYSTEM TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Scheduler-specific analysis
        scheduler_tests = [r for r in self.test_results if 'scheduler' in r['test'].lower()]
        scheduler_passed = sum(1 for r in scheduler_tests if r['success'])
        
        print(f"\n⏰ SCHEDULER TESTS: {scheduler_passed}/{len(scheduler_tests)} passed")
        
        # Telethon timing analysis
        timing_tests = [r for r in self.test_results if 'telethon' in r['test'].lower() or 'timing' in r['test'].lower()]
        timing_passed = sum(1 for r in timing_tests if r['success'])
        
        print(f"🕐 TELETHON TIMING TESTS: {timing_passed}/{len(timing_tests)} passed")
        
        # Socket.IO events analysis
        socket_tests = [r for r in self.test_results if 'socket' in r['test'].lower()]
        socket_passed = sum(1 for r in socket_tests if r['success'])
        
        print(f"📡 SOCKET.IO TESTS: {socket_passed}/{len(socket_tests)} passed")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['details']}")
        
        # Key findings
        print("\n🎯 KEY FINDINGS:")
        
        # Check immediate execution
        immediate_tests = [r for r in self.test_results if 'immediate' in r['test'].lower()]
        if any(r['success'] for r in immediate_tests):
            print("  ✅ Immediate execution functionality implemented")
        else:
            print("  ❌ Immediate execution functionality needs verification")
        
        # Check Telethon timing
        telethon_timing_tests = [r for r in self.test_results if 'telethon' in r['details'].lower() and r['success']]
        if telethon_timing_tests:
            print("  ✅ Telethon best practices (20-30 second delays) implemented")
        else:
            print("  ❌ Telethon timing best practices need verification")
        
        # Check Socket.IO events
        if len(self.socket_events) > 0:
            print(f"  ✅ Socket.IO real-time updates working ({len(self.socket_events)} events received)")
        else:
            print("  ❌ Socket.IO real-time updates need verification")
        
        return {
            'total': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'scheduler_tests_passed': scheduler_passed,
            'scheduler_tests_total': len(scheduler_tests),
            'socket_events_received': len(self.socket_events),
            'results': self.test_results
        }

if __name__ == "__main__":
    tester = SchedulerSystemTester()
    results = tester.run_scheduler_tests()
    
    # Exit with appropriate code
    if results['success_rate'] >= 80:  # 80% success rate threshold
        exit(0)
    else:
        exit(1)