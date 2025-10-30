"""
Unit tests for authentication module - Fixed version
Tests only the functions that actually exist in the module
"""

import pytest
from app.auth import AuthManager, get_current_user, require_admin

class TestAuthManager:
    """Test AuthManager functionality"""
    
    def test_auth_manager_init(self):
        """Test AuthManager initialization"""
        auth = AuthManager()
        assert auth is not None
        assert hasattr(auth, 'users')
    
    def test_auth_manager_has_required_methods(self):
        """Test that AuthManager has required methods"""
        auth = AuthManager()
        assert hasattr(auth, 'create_user')
        assert hasattr(auth, 'authenticate')
        assert hasattr(auth, 'change_password')
    
    def test_auth_manager_users_attribute(self):
        """Test that AuthManager has users attribute"""
        auth = AuthManager()
        assert hasattr(auth, 'users')
        assert isinstance(auth.users, dict)

class TestAuthFunctions:
    """Test authentication helper functions"""
    
    def test_get_current_user_function_exists(self):
        """Test that get_current_user function exists and is callable"""
        assert callable(get_current_user)
    
    def test_require_admin_function_exists(self):
        """Test that require_admin function exists and is callable"""
        assert callable(require_admin)

class TestAuthManagerIntegration:
    """Test AuthManager integration scenarios"""
    
    def test_create_and_authenticate_user(self):
        """Test creating a user and authenticating them"""
        auth = AuthManager()
        username = "test_user"
        password = "test_password"
        
        # Create user
        result = auth.create_user(username, password)
        assert result is True
        assert username in auth.users
        
        # Authenticate user
        auth_result = auth.authenticate(username, password)
        assert auth_result is True
    
    def test_authenticate_nonexistent_user(self):
        """Test authenticating a user that doesn't exist"""
        auth = AuthManager()
        username = "nonexistent_user"
        password = "test_password"
        
        result = auth.authenticate(username, password)
        assert result is False
    
    def test_create_duplicate_user(self):
        """Test creating a user that already exists"""
        auth = AuthManager()
        username = "test_user"
        password = "test_password"
        
        # Create first user
        result1 = auth.create_user(username, password)
        assert result1 is True
        
        # Try to create duplicate
        result2 = auth.create_user(username, password)
        assert result2 is False
