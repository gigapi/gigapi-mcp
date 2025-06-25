"""Tests for GigAPI configuration."""

import os
import pytest
from unittest.mock import patch

from mcp_gigapi.config import GigAPIConfig, get_config


class TestGigAPIConfig:
    """Test cases for GigAPIConfig."""

    def test_init_defaults(self):
        """Test configuration initialization with defaults."""
        with patch.dict(os.environ, {}, clear=True):
            config = GigAPIConfig()
            
            assert config.host == "localhost"
            assert config.port == 7971
            assert config.username is None
            assert config.password is None
            assert config.timeout == 30
            assert config.verify_ssl is True
            assert config.transport == "stdio"
            assert config.default_database == "mydb"
            assert config.enabled is True

    def test_init_with_env_vars(self):
        """Test configuration initialization with environment variables."""
        env_vars = {
            "GIGAPI_HOST": "test-host.com",
            "GIGAPI_PORT": "8080",
            "GIGAPI_USERNAME": "testuser",
            "GIGAPI_PASSWORD": "testpass",
            "GIGAPI_TIMEOUT": "60",
            "GIGAPI_VERIFY_SSL": "false",
            "GIGAPI_DEFAULT_DATABASE": "testdb",
            "GIGAPI_ENABLED": "true"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = GigAPIConfig()
            
            assert config.host == "test-host.com"
            assert config.port == 8080
            assert config.username == "testuser"
            assert config.password == "testpass"
            assert config.timeout == 60
            assert config.verify_ssl is False
            assert config.default_database == "testdb"
            assert config.enabled is True

    def test_base_url_http(self):
        """Test base URL generation for HTTP."""
        config = GigAPIConfig()
        config.host = "test.com"
        config.port = 8080
        config.verify_ssl = False
        
        assert config.base_url == "http://test.com:8080"

    def test_base_url_https(self):
        """Test base URL generation for HTTPS."""
        config = GigAPIConfig()
        config.host = "test.com"
        config.port = 8443
        config.verify_ssl = True
        
        assert config.base_url == "https://test.com:8443"

    def test_validate_success(self):
        """Test successful validation."""
        config = GigAPIConfig()
        config.host = "test.com"
        config.port = 8080
        config.timeout = 30
        config.enabled = True
        
        # Should not raise any exception
        config.validate()

    def test_validate_disabled(self):
        """Test validation when disabled."""
        config = GigAPIConfig()
        config.enabled = False
        
        with pytest.raises(ValueError, match="GigAPI is disabled in configuration"):
            config.validate()

    def test_validate_invalid_host(self):
        """Test validation with invalid host."""
        config = GigAPIConfig()
        config.host = ""
        config.enabled = True
        
        with pytest.raises(ValueError, match="GIGAPI_HOST is required"):
            config.validate()

    def test_validate_invalid_port(self):
        """Test validation with invalid port."""
        config = GigAPIConfig()
        config.host = "test.com"
        config.port = 0
        config.enabled = True
        
        with pytest.raises(ValueError, match="GIGAPI_PORT must be between 1 and 65535"):
            config.validate()

    def test_validate_port_too_high(self):
        """Test validation with port too high."""
        config = GigAPIConfig()
        config.host = "test.com"
        config.port = 70000
        config.enabled = True
        
        with pytest.raises(ValueError, match="GIGAPI_PORT must be between 1 and 65535"):
            config.validate()

    def test_validate_invalid_timeout(self):
        """Test validation with invalid timeout."""
        config = GigAPIConfig()
        config.host = "test.com"
        config.port = 8080
        config.timeout = 0
        config.enabled = True
        
        with pytest.raises(ValueError, match="GIGAPI_TIMEOUT must be positive"):
            config.validate()

    def test_to_dict(self):
        """Test conversion to dictionary."""
        config = GigAPIConfig()
        config.host = "test.com"
        config.port = 8080
        config.username = "user"
        config.password = "pass"
        config.timeout = 30  # Ensure timeout is set to 30
        config.verify_ssl = True  # Ensure verify_ssl is set to True
        
        result = config.to_dict()
        
        assert result["host"] == "test.com"
        assert result["port"] == 8080
        assert result["username"] == "user"
        assert result["password"] == "***"  # Password should be masked
        assert result["timeout"] == 30
        assert result["verify_ssl"] is True
        assert result["enabled"] is True
        assert "base_url" in result

    def test_to_dict_no_password(self):
        """Test conversion to dictionary without password."""
        config = GigAPIConfig()
        config.host = "test.com"
        config.port = 8080
        config.username = "user"
        config.password = None
        
        result = config.to_dict()
        
        assert result["password"] is None


class TestGetConfig:
    """Test cases for get_config function."""

    def test_get_config(self):
        """Test getting configuration instance."""
        with patch.dict(os.environ, {}, clear=True):
            config = get_config()
            assert isinstance(config, GigAPIConfig)
            assert config.host == "localhost"
            assert config.port == 7971 