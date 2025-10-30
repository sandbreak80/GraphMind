"""
Unit tests for authentication module
"""

import pytest
from datetime import datetime, timedelta
from app.auth import AuthManager, get_current_user, require_admin

class TestPasswordHashing:
    """Test password hashing and verification"""
    
    def test_password_hash_creation(self):
        """Test password hash is created correctly"""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 20  # Bcrypt hashes are long
    
    def test_password_verification_correct(self):
        """Test password verification with correct password"""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_password_verification_incorrect(self):
        """Test password verification with incorrect password"""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_different_hashes_for_same_password(self):
        """Test that same password generates different hashes (salt)"""
        password = "test_password_123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        assert hash1 != hash2  # Different due to random salt
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

class TestJWTTokens:
    """Test JWT token creation and verification"""
    
    def test_create_access_token(self):
        """Test access token creation"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 20
    
    def test_create_token_with_expiry(self):
        """Test token creation with custom expiry"""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=15)
        token = create_access_token(data, expires_delta=expires_delta)
        
        assert token is not None
    
    def test_verify_valid_token(self):
        """Test verification of valid token"""
        data = {"sub": "testuser", "is_admin": True}
        token = create_access_token(data)
        
        payload = verify_token(token)
        
        assert payload is not None
        assert payload.get("sub") == "testuser"
        assert payload.get("is_admin") is True
    
    def test_verify_invalid_token(self):
        """Test verification of invalid token"""
        invalid_token = "invalid.token.here"
        
        payload = verify_token(invalid_token)
        assert payload is None
    
    def test_verify_expired_token(self):
        """Test verification of expired token"""
        data = {"sub": "testuser"}
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = create_access_token(data, expires_delta=expires_delta)
        
        payload = verify_token(token)
        assert payload is None

class TestAuthManager:
    """Test AuthManager class"""
    
    def test_init(self, temp_dir):
        """Test AuthManager initialization"""
        auth_manager = AuthManager(storage_dir=str(temp_dir))
        
        assert auth_manager.storage_dir == temp_dir
        assert auth_manager.users_file.exists()
    
    def test_create_user(self, temp_dir):
        """Test user creation"""
        auth_manager = AuthManager(storage_dir=str(temp_dir))
        
        success = auth_manager.create_user("testuser", "password123", is_admin=False)
        assert success is True
        
        # Verify user exists
        users = auth_manager._load_users()
        assert "testuser" in users
        assert users["testuser"]["is_admin"] is False
    
    def test_create_duplicate_user(self, temp_dir):
        """Test creating duplicate user fails"""
        auth_manager = AuthManager(storage_dir=str(temp_dir))
        
        auth_manager.create_user("testuser", "password123")
        success = auth_manager.create_user("testuser", "password456")
        
        assert success is False
    
    def test_authenticate_valid_user(self, temp_dir):
        """Test authentication with valid credentials"""
        auth_manager = AuthManager(storage_dir=str(temp_dir))
        
        auth_manager.create_user("testuser", "password123", is_admin=True)
        user = auth_manager.authenticate_user("testuser", "password123")
        
        assert user is not None
        assert user["username"] == "testuser"
        assert user["is_admin"] is True
    
    def test_authenticate_invalid_password(self, temp_dir):
        """Test authentication with invalid password"""
        auth_manager = AuthManager(storage_dir=str(temp_dir))
        
        auth_manager.create_user("testuser", "password123")
        user = auth_manager.authenticate_user("testuser", "wrong_password")
        
        assert user is None
    
    def test_authenticate_nonexistent_user(self, temp_dir):
        """Test authentication with non-existent user"""
        auth_manager = AuthManager(storage_dir=str(temp_dir))
        
        user = auth_manager.authenticate_user("nonexistent", "password")
        assert user is None
    
    def test_change_password(self, temp_dir):
        """Test password change functionality"""
        auth_manager = AuthManager(storage_dir=str(temp_dir))
        
        auth_manager.create_user("testuser", "old_password")
        success = auth_manager.change_password("testuser", "old_password", "new_password")
        
        assert success is True
        
        # Old password should not work
        user = auth_manager.authenticate_user("testuser", "old_password")
        assert user is None
        
        # New password should work
        user = auth_manager.authenticate_user("testuser", "new_password")
        assert user is not None
    
    def test_change_password_wrong_old_password(self, temp_dir):
        """Test password change with wrong old password"""
        auth_manager = AuthManager(storage_dir=str(temp_dir))
        
        auth_manager.create_user("testuser", "password123")
        success = auth_manager.change_password("testuser", "wrong_old", "new_password")
        
        assert success is False

