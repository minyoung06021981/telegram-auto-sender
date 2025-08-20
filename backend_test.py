#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Telegram Auto Sender V2.0
Tests Clean Architecture implementation with FastAPI, JWT auth, and MongoDB
"""

import asyncio
import json
import os
import sys
import time
from typing import Dict, Any, Optional

import httpx
import pytest
from motor.motor_asyncio import AsyncIOMotorClient


class TelegramAutoSenderBackendTester:
    """Comprehensive backend tester for Clean Architecture implementation."""
    
    def __init__(self):
        # Get backend URL from frontend env (as per instructions)
        self.frontend_env_path = "/app/frontend/.env"
        self.backend_url = self._get_backend_url()
        self.client = httpx.AsyncClient(timeout=30.0)
        self.auth_token = None
        self.test_user_data = {
            "username": "testuser_v2_2025",
            "email": "testuser.v2.2025@example.com", 
            "password": "SecureTestPass123!",
            "full_name": "Test User V2 2025"
        }
        self.test_results = []
        
    def _get_backend_url(self) -> str:
        """Get backend URL from frontend .env file."""
        try:
            with open(self.frontend_env_path, 'r') as f:
                for line in f:
                    if line.startswith('VITE_API_URL='):
                        return line.split('=', 1)[1].strip()
            return "http://localhost:8001/api"  # fallback
        except Exception:
            return "http://localhost:8001/api"  # fallback
    
    def log_test(self, test_name: str, status: str, details: str = "", response_data: Any = None):
        """Log test results."""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": time.time()
        }
        if response_data:
            result["response"] = response_data
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
    
    async def test_health_endpoint(self):
        """Test health check endpoint."""
        try:
            # Test root health endpoint (no /api prefix)
            response = await self.client.get(f"{self.backend_url.replace('/api', '')}/health")
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["status", "version"]
                
                if all(field in data for field in expected_fields):
                    if data.get("status") == "healthy" and data.get("version") == "2.0.0":
                        self.log_test("Health Check", "PASS", 
                                    f"Status: {data.get('status')}, Version: {data.get('version')}", data)
                    else:
                        self.log_test("Health Check", "FAIL", 
                                    f"Unexpected values - Status: {data.get('status')}, Version: {data.get('version')}", data)
                else:
                    self.log_test("Health Check", "FAIL", 
                                f"Missing required fields. Got: {list(data.keys())}", data)
            else:
                self.log_test("Health Check", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Health Check", "FAIL", f"Exception: {str(e)}")
    
    async def test_root_endpoint(self):
        """Test root API information endpoint."""
        try:
            response = await self.client.get(f"{self.backend_url.replace('/api', '')}/")
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["name", "version", "description", "docs", "health"]
                
                if all(field in data for field in expected_fields):
                    self.log_test("Root Endpoint", "PASS", 
                                f"API Info retrieved successfully", data)
                else:
                    self.log_test("Root Endpoint", "FAIL", 
                                f"Missing fields. Got: {list(data.keys())}", data)
            else:
                self.log_test("Root Endpoint", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Root Endpoint", "FAIL", f"Exception: {str(e)}")
    
    async def test_api_docs(self):
        """Test API documentation endpoint."""
        try:
            response = await self.client.get(f"{self.backend_url}/docs")
            
            if response.status_code == 200:
                # Check if it's HTML content (Swagger UI)
                content_type = response.headers.get("content-type", "")
                if "text/html" in content_type:
                    self.log_test("API Documentation", "PASS", 
                                "Swagger UI accessible")
                else:
                    self.log_test("API Documentation", "WARN", 
                                f"Unexpected content type: {content_type}")
            else:
                self.log_test("API Documentation", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("API Documentation", "FAIL", f"Exception: {str(e)}")
    
    async def test_openapi_schema(self):
        """Test OpenAPI schema endpoint."""
        try:
            response = await self.client.get(f"{self.backend_url}/openapi.json")
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["openapi", "info", "paths"]
                
                if all(field in data for field in expected_fields):
                    # Check for our specific endpoints
                    paths = data.get("paths", {})
                    expected_paths = ["/api/auth/register", "/api/auth/login", "/api/auth/me"]
                    
                    found_paths = [path for path in expected_paths if path in paths]
                    if len(found_paths) == len(expected_paths):
                        self.log_test("OpenAPI Schema", "PASS", 
                                    f"Schema valid with {len(paths)} endpoints")
                    else:
                        self.log_test("OpenAPI Schema", "WARN", 
                                    f"Some expected paths missing. Found: {found_paths}")
                else:
                    self.log_test("OpenAPI Schema", "FAIL", 
                                f"Invalid schema structure. Got: {list(data.keys())}")
            else:
                self.log_test("OpenAPI Schema", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("OpenAPI Schema", "FAIL", f"Exception: {str(e)}")
    
    async def test_user_registration(self):
        """Test user registration endpoint."""
        try:
            response = await self.client.post(
                f"{self.backend_url}/auth/register",
                json=self.test_user_data
            )
            
            if response.status_code == 201:
                data = response.json()
                expected_fields = ["access_token", "token_type", "user"]
                
                if all(field in data for field in expected_fields):
                    if data.get("token_type") == "bearer":
                        self.auth_token = data.get("access_token")
                        user_data = data.get("user", {})
                        
                        self.log_test("User Registration", "PASS", 
                                    f"User created: {user_data.get('username')}", 
                                    {"user_id": user_data.get("id"), "username": user_data.get("username")})
                    else:
                        self.log_test("User Registration", "FAIL", 
                                    f"Invalid token type: {data.get('token_type')}", data)
                else:
                    self.log_test("User Registration", "FAIL", 
                                f"Missing fields. Got: {list(data.keys())}", data)
            elif response.status_code == 400:
                # User might already exist, try to login instead
                self.log_test("User Registration", "WARN", 
                            "User might already exist, will try login", response.json())
            else:
                self.log_test("User Registration", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("User Registration", "FAIL", f"Exception: {str(e)}")
    
    async def test_user_login(self):
        """Test user login endpoint."""
        try:
            login_data = {
                "username": self.test_user_data["username"],
                "password": self.test_user_data["password"]
            }
            
            response = await self.client.post(
                f"{self.backend_url}/auth/login",
                json=login_data
            )
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["access_token", "token_type", "user"]
                
                if all(field in data for field in expected_fields):
                    if data.get("token_type") == "bearer":
                        self.auth_token = data.get("access_token")
                        user_data = data.get("user", {})
                        
                        self.log_test("User Login", "PASS", 
                                    f"Login successful: {user_data.get('username')}", 
                                    {"user_id": user_data.get("id"), "token_length": len(self.auth_token)})
                    else:
                        self.log_test("User Login", "FAIL", 
                                    f"Invalid token type: {data.get('token_type')}", data)
                else:
                    self.log_test("User Login", "FAIL", 
                                f"Missing fields. Got: {list(data.keys())}", data)
            else:
                self.log_test("User Login", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("User Login", "FAIL", f"Exception: {str(e)}")
    
    async def test_protected_endpoint_without_token(self):
        """Test protected endpoint without authentication token."""
        try:
            response = await self.client.get(f"{self.backend_url}/auth/me")
            
            if response.status_code == 401:
                self.log_test("Protected Endpoint (No Token)", "PASS", 
                            "Correctly rejected unauthenticated request")
            else:
                self.log_test("Protected Endpoint (No Token)", "FAIL", 
                            f"Expected 401, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Protected Endpoint (No Token)", "FAIL", f"Exception: {str(e)}")
    
    async def test_get_current_user(self):
        """Test getting current user information."""
        if not self.auth_token:
            self.log_test("Get Current User", "SKIP", "No auth token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = await self.client.get(f"{self.backend_url}/auth/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["id", "username", "email", "full_name", "subscription_type", "subscription_active"]
                
                if all(field in data for field in expected_fields):
                    if data.get("username") == self.test_user_data["username"]:
                        self.log_test("Get Current User", "PASS", 
                                    f"User info retrieved: {data.get('username')}", 
                                    {"user_id": data.get("id"), "subscription": data.get("subscription_type")})
                    else:
                        self.log_test("Get Current User", "FAIL", 
                                    f"Username mismatch. Expected: {self.test_user_data['username']}, Got: {data.get('username')}", data)
                else:
                    self.log_test("Get Current User", "FAIL", 
                                f"Missing fields. Got: {list(data.keys())}", data)
            else:
                self.log_test("Get Current User", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Get Current User", "FAIL", f"Exception: {str(e)}")
    
    async def test_invalid_token(self):
        """Test with invalid JWT token."""
        try:
            headers = {"Authorization": "Bearer invalid-token-12345"}
            response = await self.client.get(f"{self.backend_url}/auth/me", headers=headers)
            
            if response.status_code == 401:
                self.log_test("Invalid Token", "PASS", 
                            "Correctly rejected invalid token")
            else:
                self.log_test("Invalid Token", "FAIL", 
                            f"Expected 401, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Invalid Token", "FAIL", f"Exception: {str(e)}")
    
    async def test_telegram_sessions_endpoint(self):
        """Test Telegram sessions endpoints."""
        if not self.auth_token:
            self.log_test("Telegram Sessions", "SKIP", "No auth token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test GET sessions (should return empty list initially)
            response = await self.client.get(f"{self.backend_url}/telegram/sessions", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Telegram Sessions List", "PASS", 
                                f"Retrieved {len(data)} sessions", {"count": len(data)})
                else:
                    self.log_test("Telegram Sessions List", "FAIL", 
                                f"Expected list, got {type(data)}", data)
            else:
                self.log_test("Telegram Sessions List", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Telegram Sessions List", "FAIL", f"Exception: {str(e)}")
    
    async def test_telegram_session_creation(self):
        """Test Telegram session creation (will fail without real API credentials)."""
        if not self.auth_token:
            self.log_test("Telegram Session Creation", "SKIP", "No auth token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            session_data = {
                "api_id": 12345,  # Fake API ID
                "api_hash": "fake_api_hash_for_testing",
                "phone_number": "+1234567890"
            }
            
            response = await self.client.post(
                f"{self.backend_url}/telegram/sessions", 
                headers=headers,
                json=session_data
            )
            
            # This should fail with fake credentials, but endpoint should be accessible
            if response.status_code in [400, 401, 422]:
                # Expected failure with fake credentials
                self.log_test("Telegram Session Creation", "PASS", 
                            f"Endpoint accessible, failed as expected with fake credentials (HTTP {response.status_code})")
            elif response.status_code == 201:
                # Unexpected success (shouldn't happen with fake credentials)
                self.log_test("Telegram Session Creation", "WARN", 
                            "Unexpected success with fake credentials", response.json())
            else:
                self.log_test("Telegram Session Creation", "FAIL", 
                            f"Unexpected HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Telegram Session Creation", "FAIL", f"Exception: {str(e)}")
    
    async def test_groups_endpoints(self):
        """Test Groups management endpoints."""
        if not self.auth_token:
            self.log_test("Groups Endpoints", "SKIP", "No auth token available")
            return
            
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Test GET groups
            response = await self.client.get(f"{self.backend_url}/groups", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Groups List", "PASS", 
                                f"Retrieved {len(data)} groups", {"count": len(data)})
                else:
                    self.log_test("Groups List", "FAIL", 
                                f"Expected list, got {type(data)}", data)
            else:
                self.log_test("Groups List", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
            
            # Test GET group stats
            response = await self.client.get(f"{self.backend_url}/groups/stats", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["total", "active", "inactive", "temp_blacklisted", "perm_blacklisted"]
                
                if all(field in data for field in expected_fields):
                    self.log_test("Groups Stats", "PASS", 
                                f"Stats retrieved: {data}", data)
                else:
                    self.log_test("Groups Stats", "FAIL", 
                                f"Missing fields. Got: {list(data.keys())}", data)
            else:
                self.log_test("Groups Stats", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Groups Endpoints", "FAIL", f"Exception: {str(e)}")
    
    async def test_input_validation(self):
        """Test input validation on various endpoints."""
        try:
            # Test registration with invalid data
            invalid_data = {
                "username": "",  # Empty username
                "email": "invalid-email",  # Invalid email
                "password": "123",  # Too short password
                "full_name": ""
            }
            
            response = await self.client.post(
                f"{self.backend_url}/auth/register",
                json=invalid_data
            )
            
            if response.status_code == 422:
                data = response.json()
                if "detail" in data:
                    self.log_test("Input Validation", "PASS", 
                                "Validation errors correctly returned", {"error_count": len(data.get("errors", []))})
                else:
                    self.log_test("Input Validation", "FAIL", 
                                "Expected validation error format not found", data)
            else:
                self.log_test("Input Validation", "FAIL", 
                            f"Expected 422, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_test("Input Validation", "FAIL", f"Exception: {str(e)}")
    
    async def test_cors_headers(self):
        """Test CORS headers are present."""
        try:
            response = await self.client.options(f"{self.backend_url}/auth/login")
            
            cors_headers = [
                "access-control-allow-origin",
                "access-control-allow-methods", 
                "access-control-allow-headers"
            ]
            
            present_headers = [h for h in cors_headers if h in response.headers]
            
            if len(present_headers) >= 2:  # At least some CORS headers present
                self.log_test("CORS Headers", "PASS", 
                            f"CORS headers present: {present_headers}")
            else:
                self.log_test("CORS Headers", "WARN", 
                            f"Limited CORS headers found: {present_headers}")
                
        except Exception as e:
            self.log_test("CORS Headers", "FAIL", f"Exception: {str(e)}")
    
    async def test_database_connectivity(self):
        """Test MongoDB database connectivity."""
        try:
            # Get MongoDB URL from backend env
            mongo_url = None
            try:
                with open("/app/backend/.env", 'r') as f:
                    for line in f:
                        if line.startswith('MONGO_URL='):
                            mongo_url = line.split('=', 1)[1].strip()
                            break
            except Exception:
                mongo_url = "mongodb://localhost:27017"
            
            if mongo_url:
                client = AsyncIOMotorClient(mongo_url)
                # Test connection
                await client.admin.command('ping')
                
                # Test database access
                db_name = "telegram_auto_sender_v2"  # From backend .env
                db = client[db_name]
                collections = await db.list_collection_names()
                
                self.log_test("Database Connectivity", "PASS", 
                            f"MongoDB connected, DB: {db_name}, Collections: {len(collections)}", 
                            {"collections": collections})
                
                await client.close()
            else:
                self.log_test("Database Connectivity", "FAIL", 
                            "Could not determine MongoDB URL")
                
        except Exception as e:
            self.log_test("Database Connectivity", "FAIL", f"Exception: {str(e)}")
    
    async def run_all_tests(self):
        """Run all backend tests."""
        print("🚀 Starting Telegram Auto Sender V2.0 Backend Tests")
        print(f"🔗 Backend URL: {self.backend_url}")
        print("=" * 60)
        
        # Core API Structure Tests
        await self.test_health_endpoint()
        await self.test_root_endpoint()
        await self.test_api_docs()
        await self.test_openapi_schema()
        
        # Authentication Flow Tests
        await self.test_user_registration()
        await self.test_user_login()
        await self.test_protected_endpoint_without_token()
        await self.test_get_current_user()
        await self.test_invalid_token()
        
        # Feature Endpoint Tests
        await self.test_telegram_sessions_endpoint()
        await self.test_telegram_session_creation()
        await self.test_groups_endpoints()
        
        # Security & Validation Tests
        await self.test_input_validation()
        await self.test_cors_headers()
        
        # Infrastructure Tests
        await self.test_database_connectivity()
        
        await self.client.aclose()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = len([t for t in self.test_results if t["status"] == "PASS"])
        failed = len([t for t in self.test_results if t["status"] == "FAIL"])
        warnings = len([t for t in self.test_results if t["status"] == "WARN"])
        skipped = len([t for t in self.test_results if t["status"] == "SKIP"])
        
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"⚠️  WARNINGS: {warnings}")
        print(f"⏭️  SKIPPED: {skipped}")
        print(f"📈 TOTAL: {len(self.test_results)}")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for test in self.test_results:
                if test["status"] == "FAIL":
                    print(f"   • {test['test']}: {test['details']}")
        
        return {
            "total": len(self.test_results),
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "skipped": skipped,
            "results": self.test_results
        }


async def main():
    """Main test runner."""
    tester = TelegramAutoSenderBackendTester()
    results = await tester.run_all_tests()
    
    # Exit with error code if tests failed
    if results["failed"] > 0:
        sys.exit(1)
    else:
        print("\n🎉 All critical tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())