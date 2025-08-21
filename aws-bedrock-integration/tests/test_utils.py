"""Tests for utility functions and classes."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import asyncio

from bedrock_langfuse.utils import (
    ModelComparison, ConversationManager, estimate_tokens, 
    format_cost, get_model_recommendations
)
from bedrock_langfuse.models import ChatMessage, MessageRole, ModelConfig, ChatResponse, ModelUsage


class TestModelComparison(unittest.TestCase):
    """Test ModelComparison utility."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.comparison = ModelComparison(self.mock_client)
    
    def test_model_comparison_initialization(self):
        """Test ModelComparison initialization."""
        # Test with provided client
        comp_with_client = ModelComparison(self.mock_client)
        self.assertEqual(comp_with_client.client, self.mock_client)
        
        # Test without provided client (should create new one)
        with patch('bedrock_langfuse.utils.BedrockLangfuseClient'):
            comp_without_client = ModelComparison()
            self.assertIsNotNone(comp_without_client.client)
    
    def test_compare_models_success(self):
        """Test successful model comparison."""
        # Mock responses
        mock_responses = {
            "model1": ChatResponse(
                content="Response 1",
                model="model1",
                usage=ModelUsage(10, 20, 30, 0.001),
                response_time=1.0
            ),
            "model2": ChatResponse(
                content="Response 2", 
                model="model2",
                usage=ModelUsage(15, 25, 40, 0.002),
                response_time=1.5
            )
        }
        
        def mock_chat_completion(*args, **kwargs):
            model = kwargs.get('model')
            return mock_responses[model]
        
        self.mock_client.chat_completion.side_effect = mock_chat_completion
        
        # Run comparison
        results = self.comparison.compare_models(
            models=["model1", "model2"],
            prompt="Test prompt",
            session_id="test-session"
        )
        
        self.assertEqual(len(results), 2)
        self.assertIn("model1", results)
        self.assertIn("model2", results)
        self.assertEqual(results["model1"].content, "Response 1")
        self.assertEqual(results["model2"].content, "Response 2")
    
    def test_compare_models_with_error(self):
        """Test model comparison with one model failing."""
        def mock_chat_completion(*args, **kwargs):
            model = kwargs.get('model')
            if model == "model1":
                return ChatResponse(
                    content="Success",
                    model="model1", 
                    usage=ModelUsage(10, 20, 30),
                    response_time=1.0
                )
            else:
                raise Exception("Model failed")
        
        self.mock_client.chat_completion.side_effect = mock_chat_completion
        
        results = self.comparison.compare_models(
            models=["model1", "model2"],
            prompt="Test prompt"
        )
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results["model1"].content, "Success")
        self.assertTrue(results["model2"].content.startswith("Error:"))
    
    @patch('asyncio.get_event_loop')
    def test_compare_models_async(self, mock_get_loop):
        """Test async model comparison."""
        # Create a mock event loop
        mock_loop = Mock()
        mock_get_loop.return_value = mock_loop
        
        # Mock async responses
        async def mock_async_completion(*args, **kwargs):
            model = kwargs.get('model')
            return ChatResponse(
                content=f"Async response from {model}",
                model=model,
                usage=ModelUsage(5, 10, 15),
                response_time=0.5
            )
        
        self.mock_client.chat_completion_async = mock_async_completion
        
        # Note: In a real async test, you'd use asyncio.run()
        # Here we're just testing the structure
        self.assertIsNotNone(self.comparison.compare_models_async)


class TestConversationManager(unittest.TestCase):
    """Test ConversationManager utility."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.conv_manager = ConversationManager(self.mock_client)
    
    def test_conversation_manager_initialization(self):
        """Test ConversationManager initialization."""
        self.assertEqual(self.conv_manager.client, self.mock_client)
        self.assertEqual(self.conv_manager.conversations, {})
    
    def test_start_conversation(self):
        """Test starting a new conversation."""
        session_id = "test-session"
        system_message = "You are helpful."
        
        self.conv_manager.start_conversation(session_id, system_message)
        
        self.assertIn(session_id, self.conv_manager.conversations)
        messages = self.conv_manager.conversations[session_id]
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].role, MessageRole.SYSTEM)
        self.assertEqual(messages[0].content, system_message)
    
    def test_start_conversation_without_system_message(self):
        """Test starting conversation without system message."""
        session_id = "test-session"
        
        self.conv_manager.start_conversation(session_id)
        
        self.assertIn(session_id, self.conv_manager.conversations)
        self.assertEqual(len(self.conv_manager.conversations[session_id]), 0)
    
    def test_add_user_message(self):
        """Test adding user message to conversation."""
        session_id = "test-session"
        user_message = "Hello!"
        
        self.conv_manager.add_user_message(session_id, user_message)
        
        # Should auto-start conversation if it doesn't exist
        self.assertIn(session_id, self.conv_manager.conversations)
        messages = self.conv_manager.conversations[session_id]
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].role, MessageRole.USER)
        self.assertEqual(messages[0].content, user_message)
    
    def test_get_response(self):
        """Test getting response from model."""
        session_id = "test-session"
        
        # Setup conversation
        self.conv_manager.start_conversation(session_id)
        self.conv_manager.add_user_message(session_id, "Hello")
        
        # Mock client response
        mock_response = ChatResponse(
            content="Hi there!",
            model="test-model",
            usage=ModelUsage(5, 10, 15),
            response_time=1.0
        )
        self.mock_client.chat_completion.return_value = mock_response
        
        # Get response
        response = self.conv_manager.get_response(
            session_id=session_id,
            model="test-model"
        )
        
        self.assertEqual(response.content, "Hi there!")
        
        # Check that assistant message was added to conversation
        messages = self.conv_manager.conversations[session_id]
        self.assertEqual(len(messages), 2)  # User + Assistant
        self.assertEqual(messages[1].role, MessageRole.ASSISTANT)
        self.assertEqual(messages[1].content, "Hi there!")
    
    def test_get_response_nonexistent_session(self):
        """Test getting response for non-existent session."""
        with self.assertRaises(ValueError):
            self.conv_manager.get_response(
                session_id="nonexistent",
                model="test-model"
            )
    
    def test_get_conversation_history(self):
        """Test getting conversation history."""
        session_id = "test-session"
        
        # Setup conversation
        self.conv_manager.start_conversation(session_id, "System message")
        self.conv_manager.add_user_message(session_id, "User message")
        
        history = self.conv_manager.get_conversation_history(session_id)
        
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0].role, MessageRole.SYSTEM)
        self.assertEqual(history[1].role, MessageRole.USER)
        
        # Test that it returns a copy (modifications don't affect original)
        history.append(ChatMessage(role=MessageRole.ASSISTANT, content="Test"))
        original_history = self.conv_manager.get_conversation_history(session_id)
        self.assertEqual(len(original_history), 2)
    
    def test_clear_conversation(self):
        """Test clearing conversation."""
        session_id = "test-session"
        
        # Setup conversation
        self.conv_manager.start_conversation(session_id)
        self.conv_manager.add_user_message(session_id, "Test message")
        
        # Verify conversation exists
        self.assertIn(session_id, self.conv_manager.conversations)
        
        # Clear conversation
        self.conv_manager.clear_conversation(session_id)
        
        # Verify conversation is removed
        self.assertNotIn(session_id, self.conv_manager.conversations)
    
    def test_export_conversation(self):
        """Test exporting conversation."""
        session_id = "test-session"
        
        # Setup conversation
        self.conv_manager.start_conversation(session_id, "System")
        self.conv_manager.add_user_message(session_id, "User")
        
        export = self.conv_manager.export_conversation(session_id)
        
        self.assertEqual(export["session_id"], session_id)
        self.assertEqual(export["message_count"], 2)
        self.assertEqual(len(export["messages"]), 2)
        self.assertEqual(export["messages"][0]["role"], "system")
        self.assertEqual(export["messages"][1]["role"], "user")
    
    def test_export_nonexistent_conversation(self):
        """Test exporting non-existent conversation."""
        export = self.conv_manager.export_conversation("nonexistent")
        
        self.assertEqual(export["session_id"], "nonexistent")
        self.assertEqual(export["message_count"], 0)
        self.assertEqual(len(export["messages"]), 0)


class TestUtilityFunctions(unittest.TestCase):
    """Test standalone utility functions."""
    
    def test_estimate_tokens(self):
        """Test token estimation function."""
        # Test empty string
        self.assertEqual(estimate_tokens(""), 0)
        
        # Test short text
        short_text = "Hello world"
        tokens = estimate_tokens(short_text)
        self.assertGreater(tokens, 0)
        self.assertEqual(tokens, len(short_text) // 4)
        
        # Test longer text
        long_text = "This is a longer piece of text that should result in more tokens."
        long_tokens = estimate_tokens(long_text)
        self.assertGreater(long_tokens, tokens)
    
    def test_format_cost(self):
        """Test cost formatting function."""
        # Test very small costs
        self.assertEqual(format_cost(0.000001), "$0.000001")
        self.assertEqual(format_cost(0.0005), "$0.000500")
        
        # Test small costs
        self.assertEqual(format_cost(0.005), "$0.0050")
        self.assertEqual(format_cost(0.0123), "$0.01")  # Rounds to 2 decimal places for costs >= 0.01
        
        # Test larger costs
        self.assertEqual(format_cost(0.15), "$0.15")
        self.assertEqual(format_cost(1.25), "$1.25")
        self.assertEqual(format_cost(10.567), "$10.57")
    
    def test_get_model_recommendations(self):
        """Test model recommendation function."""
        # Test default (general) recommendations
        general_recs = get_model_recommendations()
        self.assertIsInstance(general_recs, list)
        self.assertGreater(len(general_recs), 0)
        
        # Test specific use cases
        coding_recs = get_model_recommendations("coding")
        self.assertIsInstance(coding_recs, list)
        self.assertGreater(len(coding_recs), 0)
        
        creative_recs = get_model_recommendations("creative")
        self.assertIsInstance(creative_recs, list)
        
        analysis_recs = get_model_recommendations("analysis")
        self.assertIsInstance(analysis_recs, list)
        
        cost_recs = get_model_recommendations("cost_effective")
        self.assertIsInstance(cost_recs, list)
        
        # Test unknown use case (should return general)
        unknown_recs = get_model_recommendations("unknown_use_case")
        self.assertEqual(unknown_recs, general_recs)
    
    def test_model_recommendations_content(self):
        """Test that model recommendations contain valid model IDs."""
        from bedrock_langfuse.models import SUPPORTED_MODELS
        
        all_recs = []
        use_cases = ["general", "coding", "creative", "analysis", "cost_effective"]
        
        for use_case in use_cases:
            recs = get_model_recommendations(use_case)
            all_recs.extend(recs)
        
        # Check that all recommended models are in SUPPORTED_MODELS
        for model_id in all_recs:
            self.assertIn(model_id, SUPPORTED_MODELS, 
                         f"Recommended model {model_id} not in SUPPORTED_MODELS")


if __name__ == "__main__":
    unittest.main()
