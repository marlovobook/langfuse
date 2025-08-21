"""Tests for the BedrockLangfuseClient."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime

from bedrock_langfuse.client import BedrockLangfuseClient
from bedrock_langfuse.models import ChatMessage, MessageRole, ModelConfig
from bedrock_langfuse.exceptions import (
    ModelNotAvailableError, AuthenticationError, InvalidRequestError
)


class TestBedrockLangfuseClient(unittest.TestCase):
    """Test cases for BedrockLangfuseClient."""
    
    def setUp(self):
        """Set up test fixtures."""
        with patch('boto3.client'), patch('bedrock_langfuse.client.Langfuse'):
            self.client = BedrockLangfuseClient(
                aws_access_key_id="test_key",
                aws_secret_access_key="test_secret",
                aws_region="us-east-1",
                langfuse_secret_key="test_secret",
                langfuse_public_key="test_public",
                langfuse_host="https://test.langfuse.com"
            )
    
    def test_client_initialization(self):
        """Test client initialization."""
        self.assertIsNotNone(self.client.bedrock_client)
        self.assertIsNotNone(self.client.langfuse)
    
    def test_validate_model_success(self):
        """Test model validation with valid model."""
        model_config = self.client._validate_model("anthropic.claude-3-haiku-20240307-v1:0")
        self.assertIsInstance(model_config, dict)
        self.assertIn("name", model_config)
        self.assertIn("provider", model_config)
    
    def test_validate_model_failure(self):
        """Test model validation with invalid model."""
        with self.assertRaises(ModelNotAvailableError):
            self.client._validate_model("invalid-model-id")
    
    def test_format_messages_for_claude(self):
        """Test message formatting for Claude models."""
        messages = [
            ChatMessage(role=MessageRole.SYSTEM, content="You are helpful."),
            ChatMessage(role=MessageRole.USER, content="Hello"),
            ChatMessage(role=MessageRole.ASSISTANT, content="Hi there!")
        ]
        
        formatted = self.client._format_messages_for_bedrock(
            messages, "anthropic.claude-3-haiku-20240307-v1:0"
        )
        
        self.assertIn("messages", formatted)
        self.assertIn("system", formatted)
        self.assertEqual(formatted["system"], "You are helpful.")
        self.assertEqual(len(formatted["messages"]), 2)
    
    def test_format_messages_for_llama(self):
        """Test message formatting for Llama models."""
        messages = [
            ChatMessage(role=MessageRole.USER, content="Hello")
        ]
        
        formatted = self.client._format_messages_for_bedrock(
            messages, "meta.llama2-70b-chat-v1"
        )
        
        self.assertIn("prompt", formatted)
        self.assertIn("Hello", formatted["prompt"])
    
    def test_parse_claude_response(self):
        """Test parsing Claude response."""
        mock_response = {
            "content": [{"text": "Hello! How can I help you?"}],
            "usage": {
                "input_tokens": 10,
                "output_tokens": 8
            }
        }
        
        content, usage = self.client._parse_bedrock_response(
            mock_response, "anthropic.claude-3-haiku-20240307-v1:0"
        )
        
        self.assertEqual(content, "Hello! How can I help you?")
        self.assertEqual(usage.input_tokens, 10)
        self.assertEqual(usage.output_tokens, 8)
        self.assertEqual(usage.total_tokens, 18)
    
    def test_calculate_cost(self):
        """Test cost calculation."""
        from bedrock_langfuse.models import ModelUsage, SUPPORTED_MODELS
        
        usage = ModelUsage(
            input_tokens=100,
            output_tokens=50,
            total_tokens=150
        )
        
        model_config = SUPPORTED_MODELS["anthropic.claude-3-haiku-20240307-v1:0"]
        cost = self.client._calculate_cost(usage, model_config)
        
        expected_cost = (100 / 1000) * 0.00025 + (50 / 1000) * 0.00125
        self.assertAlmostEqual(cost, expected_cost, places=6)
    
    @patch('bedrock_langfuse.client.BedrockLangfuseClient._parse_bedrock_response')
    @patch('bedrock_langfuse.client.BedrockLangfuseClient._format_messages_for_bedrock')
    def test_chat_completion_success(self, mock_format, mock_parse):
        """Test successful chat completion."""
        # Mock the format method
        mock_format.return_value = {"messages": [{"role": "user", "content": "Hello"}]}
        
        # Mock the parse method
        from bedrock_langfuse.models import ModelUsage
        mock_parse.return_value = (
            "Hello! How can I help?",
            ModelUsage(input_tokens=5, output_tokens=6, total_tokens=11)
        )
        
        # Mock bedrock client response
        mock_response = {
            'body': Mock()
        }
        mock_response['body'].read.return_value = json.dumps({
            "content": [{"text": "Hello! How can I help?"}]
        }).encode()
        
        self.client.bedrock_client.invoke_model.return_value = mock_response
        
        # Mock langfuse span and generation
        mock_span = Mock()
        mock_span.id = "test-trace-id"
        mock_span.__enter__ = Mock(return_value=mock_span)
        mock_span.__exit__ = Mock(return_value=None)
        mock_generation = Mock()
        self.client.langfuse.start_as_current_span.return_value = mock_span
        self.client.langfuse.start_generation.return_value = mock_generation
        
        # Test the method
        messages = [ChatMessage(role=MessageRole.USER, content="Hello")]
        response = self.client.chat_completion(
            model="anthropic.claude-3-haiku-20240307-v1:0",
            messages=messages
        )
        
        self.assertEqual(response.content, "Hello! How can I help?")
        self.assertEqual(response.model, "anthropic.claude-3-haiku-20240307-v1:0")
        self.assertEqual(response.usage.total_tokens, 11)
        self.assertEqual(response.trace_id, "test-trace-id")
    
    def test_list_available_models(self):
        """Test listing available models."""
        models = self.client.list_available_models()
        self.assertIsInstance(models, dict)
        self.assertIn("anthropic.claude-3-haiku-20240307-v1:0", models)
        self.assertIn("amazon.titan-text-express-v1", models)
    
    def test_get_model_info_success(self):
        """Test getting model info for valid model."""
        info = self.client.get_model_info("anthropic.claude-3-haiku-20240307-v1:0")
        self.assertIsInstance(info, dict)
        self.assertIn("name", info)
        self.assertIn("provider", info)
        self.assertEqual(info["provider"], "Anthropic")
    
    def test_get_model_info_failure(self):
        """Test getting model info for invalid model."""
        with self.assertRaises(ModelNotAvailableError):
            self.client.get_model_info("invalid-model")


class TestClientAuthentication(unittest.TestCase):
    """Test authentication scenarios."""
    
    @patch('boto3.client')
    def test_aws_authentication_error(self, mock_boto_client):
        """Test AWS authentication error handling."""
        mock_boto_client.side_effect = Exception("Invalid credentials")
        
        with self.assertRaises(AuthenticationError):
            BedrockLangfuseClient(
                aws_access_key_id="invalid",
                aws_secret_access_key="invalid"
            )
    
    @patch('boto3.client')
    @patch('bedrock_langfuse.client.Langfuse')
    def test_langfuse_authentication_error(self, mock_langfuse, mock_boto_client):
        """Test Langfuse authentication error handling."""
        mock_langfuse.side_effect = Exception("Invalid API key")
        
        with self.assertRaises(AuthenticationError):
            BedrockLangfuseClient(
                langfuse_secret_key="invalid",
                langfuse_public_key="invalid"
            )


class TestModelConfiguration(unittest.TestCase):
    """Test model configuration scenarios."""
    
    def test_model_config_creation(self):
        """Test ModelConfig creation and conversion."""
        config = ModelConfig(
            temperature=0.8,
            max_tokens=500,
            top_p=0.9,
            top_k=50,
            stop_sequences=["STOP", "END"]
        )
        
        config_dict = config.to_dict()
        
        self.assertEqual(config_dict["temperature"], 0.8)
        self.assertEqual(config_dict["max_tokens"], 500)
        self.assertEqual(config_dict["top_p"], 0.9)
        self.assertEqual(config_dict["top_k"], 50)
        self.assertEqual(config_dict["stop_sequences"], ["STOP", "END"])
    
    def test_model_config_defaults(self):
        """Test ModelConfig with default values."""
        config = ModelConfig()
        config_dict = config.to_dict()
        
        self.assertEqual(config_dict["temperature"], 0.7)
        self.assertEqual(config_dict["max_tokens"], 1000)
        self.assertEqual(config_dict["top_p"], 0.9)
        self.assertNotIn("top_k", config_dict)  # None values should be excluded
        self.assertNotIn("stop_sequences", config_dict)


if __name__ == "__main__":
    unittest.main()
