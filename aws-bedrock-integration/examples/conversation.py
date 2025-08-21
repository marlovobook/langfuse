"""Multi-turn conversation example with AWS Bedrock and Langfuse."""

from dotenv import load_dotenv
from bedrock_langfuse import BedrockLangfuseClient, ChatMessage, MessageRole, ModelConfig
from bedrock_langfuse.utils import ConversationManager

# Load environment variables
load_dotenv()

def manual_conversation_example():
    """Demonstrate a manual multi-turn conversation."""
    print("💬 Manual Multi-Turn Conversation")
    print("=" * 50)
    
    client = BedrockLangfuseClient(debug=True)
    session_id = "manual-conversation-session"
    
    # Keep track of conversation manually
    conversation_history = []
    
    # Step 1: Initial query about cooking
    print("\n🔹 Turn 1: User asks about cooking")
    messages = [
        ChatMessage(role=MessageRole.SYSTEM, content="You are a helpful cooking assistant."),
        ChatMessage(role=MessageRole.USER, content="I want to learn how to cook pasta. Can you help me?")
    ]
    conversation_history.extend(messages)
    
    try:
        response1 = client.chat_completion(
            model="anthropic.claude-3-haiku-20240307-v1:0",
            messages=conversation_history,
            session_id=session_id,
            user_id="demo-user",
            metadata={
                "conversation_turn": 1,
                "topic": "cooking_pasta",
                "conversation_type": "manual"
            },
            tags=["demo", "conversation", "cooking", "turn_1"]
        )
        
        print(f"Assistant: {response1.content[:200]}...")
        print(f"Tokens: {response1.usage.total_tokens}, Cost: ${response1.usage.estimated_cost:.6f}")
        
        # Add assistant response to history
        conversation_history.append(
            ChatMessage(role=MessageRole.ASSISTANT, content=response1.content)
        )
        
    except Exception as e:
        print(f"Error in turn 1: {str(e)}")
        return
    
    # Step 2: Follow-up question
    print("\n🔹 Turn 2: User asks for specific recipe")
    user_message_2 = ChatMessage(
        role=MessageRole.USER, 
        content="That's helpful! Can you give me a specific recipe for spaghetti carbonara?"
    )
    conversation_history.append(user_message_2)
    
    try:
        response2 = client.chat_completion(
            model="anthropic.claude-3-haiku-20240307-v1:0",
            messages=conversation_history,
            session_id=session_id,
            user_id="demo-user",
            metadata={
                "conversation_turn": 2,
                "topic": "carbonara_recipe",
                "conversation_type": "manual"
            },
            tags=["demo", "conversation", "cooking", "carbonara", "turn_2"]
        )
        
        print(f"Assistant: {response2.content[:200]}...")
        print(f"Tokens: {response2.usage.total_tokens}, Cost: ${response2.usage.estimated_cost:.6f}")
        
        conversation_history.append(
            ChatMessage(role=MessageRole.ASSISTANT, content=response2.content)
        )
        
    except Exception as e:
        print(f"Error in turn 2: {str(e)}")
        return
    
    # Step 3: Final question
    print("\n🔹 Turn 3: User asks about wine pairing")
    user_message_3 = ChatMessage(
        role=MessageRole.USER,
        content="What wine would pair well with this carbonara dish?"
    )
    conversation_history.append(user_message_3)
    
    try:
        response3 = client.chat_completion(
            model="anthropic.claude-3-haiku-20240307-v1:0",
            messages=conversation_history,
            session_id=session_id,
            user_id="demo-user",
            metadata={
                "conversation_turn": 3,
                "topic": "wine_pairing",
                "conversation_type": "manual"
            },
            tags=["demo", "conversation", "cooking", "wine", "turn_3"]
        )
        
        print(f"Assistant: {response3.content[:200]}...")
        print(f"Tokens: {response3.usage.total_tokens}, Cost: ${response3.usage.estimated_cost:.6f}")
        
        # Calculate totals
        total_tokens = response1.usage.total_tokens + response2.usage.total_tokens + response3.usage.total_tokens
        total_cost = (response1.usage.estimated_cost or 0) + (response2.usage.estimated_cost or 0) + (response3.usage.estimated_cost or 0)
        
        print(f"\n📊 Conversation Summary:")
        print(f"   Total turns: 3")
        print(f"   Total tokens: {total_tokens}")
        print(f"   Total cost: ${total_cost:.6f}")
        
    except Exception as e:
        print(f"Error in turn 3: {str(e)}")

def managed_conversation_example():
    """Demonstrate using the ConversationManager utility."""
    print("\n🤖 Managed Multi-Turn Conversation")
    print("=" * 50)
    
    # Initialize conversation manager
    conv_manager = ConversationManager()
    session_id = "managed-conversation-session"
    
    # Start conversation with system message
    conv_manager.start_conversation(
        session_id=session_id,
        system_message="You are a helpful travel planning assistant. Be concise but informative."
    )
    
    # Conversation flow
    conversation_steps = [
        "I want to plan a 5-day trip to Tokyo. What should I prioritize?",
        "That sounds great! What's the best way to get around the city?",
        "Perfect! Can you recommend some must-try local foods?",
        "Excellent recommendations! What about cultural etiquette I should know?"
    ]
    
    try:
        for i, user_message in enumerate(conversation_steps, 1):
            print(f"\n🔹 Turn {i}")
            print(f"User: {user_message}")
            
            # Add user message to conversation
            conv_manager.add_user_message(session_id, user_message)
            
            # Get response from the model
            response = conv_manager.get_response(
                session_id=session_id,
                model="anthropic.claude-3-sonnet-20240229-v1:0",
                user_id="demo-user",
                metadata={
                    "conversation_turn": i,
                    "topic": "tokyo_travel",
                    "conversation_type": "managed"
                }
            )
            
            print(f"Assistant: {response.content[:150]}...")
            print(f"Tokens: {response.usage.total_tokens}, Cost: ${response.usage.estimated_cost:.6f}")
        
        # Export conversation
        conversation_export = conv_manager.export_conversation(session_id)
        print(f"\n📄 Conversation Export:")
        print(f"   Session ID: {conversation_export['session_id']}")
        print(f"   Total messages: {conversation_export['message_count']}")
        
        # Show conversation history
        print(f"\n📝 Full Conversation History:")
        history = conv_manager.get_conversation_history(session_id)
        for i, message in enumerate(history):
            role_emoji = {"system": "⚙️", "user": "👤", "assistant": "🤖"}
            emoji = role_emoji.get(message.role.value, "❓")
            print(f"   {emoji} {message.role.value.title()}: {message.content[:100]}...")
        
    except Exception as e:
        print(f"Error in managed conversation: {str(e)}")

def conversation_with_different_models():
    """Demonstrate conversation with different models for comparison."""
    print("\n🔄 Conversation with Different Models")
    print("=" * 50)
    
    conv_manager = ConversationManager()
    
    # Models to compare in conversation
    models_to_test = [
        "anthropic.claude-3-haiku-20240307-v1:0",
        "amazon.titan-text-express-v1"
    ]
    
    base_question = "Explain quantum computing in simple terms suitable for a beginner."
    
    try:
        for model in models_to_test:
            session_id = f"model-conversation-{model.split('.')[-1]}"
            
            print(f"\n🤖 Testing with: {model}")
            
            # Start fresh conversation for each model
            conv_manager.start_conversation(
                session_id=session_id,
                system_message="You are an educational assistant. Explain complex topics simply."
            )
            
            # Add the question
            conv_manager.add_user_message(session_id, base_question)
            
            # Get response
            response = conv_manager.get_response(
                session_id=session_id,
                model=model,
                config=ModelConfig(temperature=0.5, max_tokens=300),
                user_id="demo-user",
                metadata={
                    "comparison_type": "model_conversation",
                    "model_under_test": model,
                    "question_type": "educational"
                }
            )
            
            print(f"Response: {response.content[:200]}...")
            print(f"Tokens: {response.usage.total_tokens}")
            print(f"Cost: ${response.usage.estimated_cost:.6f}")
            print(f"Time: {response.response_time:.2f}s")
            
            # Follow up question
            follow_up = "Can you give me a practical example of how quantum computing might be used?"
            conv_manager.add_user_message(session_id, follow_up)
            
            response2 = conv_manager.get_response(
                session_id=session_id,
                model=model,
                config=ModelConfig(temperature=0.5, max_tokens=300),
                user_id="demo-user",
                metadata={
                    "comparison_type": "model_conversation_followup",
                    "model_under_test": model,
                    "question_type": "practical_example"
                }
            )
            
            print(f"Follow-up response: {response2.content[:200]}...")
            print(f"Follow-up tokens: {response2.usage.total_tokens}")
            print(f"Follow-up cost: ${response2.usage.estimated_cost:.6f}")
            
            # Calculate conversation totals
            total_tokens = response.usage.total_tokens + response2.usage.total_tokens
            total_cost = (response.usage.estimated_cost or 0) + (response2.usage.estimated_cost or 0)
            print(f"Total for this model: {total_tokens} tokens, ${total_cost:.6f}")
            
    except Exception as e:
        print(f"Error in model comparison conversation: {str(e)}")

def main():
    """Run all conversation examples."""
    print("💬 AWS Bedrock Multi-Turn Conversation Examples")
    print("=" * 60)
    
    manual_conversation_example()
    managed_conversation_example()
    conversation_with_different_models()
    
    print("\n✅ All conversations have been logged to Langfuse!")

if __name__ == "__main__":
    main()
