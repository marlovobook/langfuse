"""Async chat completion example with AWS Bedrock and Langfuse."""

import asyncio
import time
from dotenv import load_dotenv
from bedrock_langfuse import BedrockLangfuseClient, ChatMessage, MessageRole, ModelConfig

# Load environment variables
load_dotenv()

async def single_async_chat(client: BedrockLangfuseClient):
    """Demonstrate a single async chat completion."""
    print("🚀 Single Async Chat Completion")
    print("=" * 40)
    
    try:
        response = await client.chat_completion_async(
            model="anthropic.claude-3-haiku-20240307-v1:0",
            messages=[
                ChatMessage(role=MessageRole.USER, content="Explain quantum computing in one paragraph.")
            ],
            session_id="async-single-session",
            user_id="demo-user",
            metadata={"example_type": "async_single", "topic": "quantum_computing"},
            tags=["demo", "async", "quantum"]
        )
        
        print(f"Model: {response.model}")
        print(f"Response: {response.content}")
        print(f"Tokens: {response.usage.total_tokens}")
        print(f"Cost: ${response.usage.estimated_cost:.6f}")
        print(f"Time: {response.response_time:.2f}s")
        
    except Exception as e:
        print(f"Error: {str(e)}")

async def concurrent_async_chats(client: BedrockLangfuseClient):
    """Demonstrate concurrent async chat completions."""
    print("\n🔄 Concurrent Async Chat Completions")
    print("=" * 40)
    
    questions = [
        "What is artificial intelligence?",
        "Explain blockchain technology.",
        "What are the benefits of renewable energy?",
        "How does photosynthesis work?",
        "What is the theory of relativity?"
    ]
    
    start_time = time.time()
    
    try:
        # Create tasks for concurrent execution
        tasks = []
        for i, question in enumerate(questions):
            task = client.chat_completion_async(
                model="anthropic.claude-3-haiku-20240307-v1:0",
                messages=[
                    ChatMessage(role=MessageRole.USER, content=question)
                ],
                session_id=f"async-concurrent-session-{i}",
                user_id="demo-user",
                metadata={
                    "example_type": "async_concurrent",
                    "question_index": i,
                    "total_questions": len(questions)
                },
                tags=["demo", "async", "concurrent", f"question_{i}"]
            )
            tasks.append((question, task))
        
        # Execute all tasks concurrently
        results = []
        for question, task in tasks:
            try:
                response = await task
                results.append((question, response))
            except Exception as e:
                print(f"Error for question '{question}': {str(e)}")
                continue
        
        total_time = time.time() - start_time
        
        # Display results
        total_tokens = 0
        total_cost = 0.0
        
        for i, (question, response) in enumerate(results, 1):
            print(f"\n{i}. Question: {question}")
            print(f"   Answer: {response.content[:100]}...")
            print(f"   Tokens: {response.usage.total_tokens}")
            print(f"   Cost: ${response.usage.estimated_cost:.6f}")
            print(f"   Time: {response.response_time:.2f}s")
            
            total_tokens += response.usage.total_tokens
            total_cost += response.usage.estimated_cost or 0
        
        print(f"\n📊 Summary:")
        print(f"   Total questions: {len(results)}")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Total tokens: {total_tokens}")
        print(f"   Total cost: ${total_cost:.6f}")
        print(f"   Average time per question: {total_time/len(results):.2f}s")
        
    except Exception as e:
        print(f"Error in concurrent execution: {str(e)}")

async def async_conversation_flow(client: BedrockLangfuseClient):
    """Demonstrate an async conversation flow."""
    print("\n💬 Async Conversation Flow")
    print("=" * 40)
    
    session_id = "async-conversation-session"
    
    # Conversation steps
    conversation_steps = [
        {
            "messages": [
                ChatMessage(role=MessageRole.SYSTEM, content="You are a helpful travel assistant."),
                ChatMessage(role=MessageRole.USER, content="I want to plan a trip to Japan. What should I know?")
            ],
            "step": "initial_planning"
        },
        {
            "messages": [
                ChatMessage(role=MessageRole.SYSTEM, content="You are a helpful travel assistant."),
                ChatMessage(role=MessageRole.USER, content="I want to plan a trip to Japan. What should I know?"),
                ChatMessage(role=MessageRole.ASSISTANT, content="[Previous response would be here]"),
                ChatMessage(role=MessageRole.USER, content="What's the best time to visit for cherry blossoms?")
            ],
            "step": "cherry_blossom_timing"
        },
        {
            "messages": [
                ChatMessage(role=MessageRole.SYSTEM, content="You are a helpful travel assistant."),
                ChatMessage(role=MessageRole.USER, content="I want to plan a trip to Japan. What should I know?"),
                ChatMessage(role=MessageRole.ASSISTANT, content="[Previous response would be here]"),
                ChatMessage(role=MessageRole.USER, content="What's the best time to visit for cherry blossoms?"),
                ChatMessage(role=MessageRole.ASSISTANT, content="[Previous response would be here]"),
                ChatMessage(role=MessageRole.USER, content="What are the must-visit cities for first-time visitors?")
            ],
            "step": "city_recommendations"
        }
    ]
    
    try:
        for i, step_data in enumerate(conversation_steps, 1):
            print(f"\n🔹 Conversation Step {i}: {step_data['step']}")
            
            response = await client.chat_completion_async(
                model="anthropic.claude-3-sonnet-20240229-v1:0",
                messages=step_data["messages"],
                session_id=session_id,
                user_id="demo-user",
                metadata={
                    "example_type": "async_conversation",
                    "conversation_step": step_data["step"],
                    "step_number": i
                },
                tags=["demo", "async", "conversation", "travel", step_data["step"]]
            )
            
            print(f"Response: {response.content[:150]}...")
            print(f"Tokens: {response.usage.total_tokens}")
            print(f"Cost: ${response.usage.estimated_cost:.6f}")
            print(f"Time: {response.response_time:.2f}s")
            
            # Add a small delay to simulate real conversation pacing
            await asyncio.sleep(0.5)
            
    except Exception as e:
        print(f"Error in conversation flow: {str(e)}")

async def main():
    """Main async function to run all examples."""
    print("🚀 AWS Bedrock + Langfuse Async Examples")
    print("=" * 50)
    
    # Initialize the client
    client = BedrockLangfuseClient(debug=True)
    
    # Run all async examples
    await single_async_chat(client)
    await concurrent_async_chats(client)
    await async_conversation_flow(client)
    
    # Flush Langfuse data
    client.flush()
    print("\n✅ All async interactions have been logged to Langfuse!")

if __name__ == "__main__":
    asyncio.run(main())
