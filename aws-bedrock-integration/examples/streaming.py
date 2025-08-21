"""Streaming responses example (simulated) with AWS Bedrock and Langfuse."""

import time
import random
from dotenv import load_dotenv
from bedrock_langfuse import BedrockLangfuseClient, ChatMessage, MessageRole, ModelConfig

# Load environment variables
load_dotenv()

def simulate_streaming_response(full_response: str, chunk_size: int = 20, delay: float = 0.1):
    """
    Simulate streaming response by yielding chunks of the full response.
    Note: AWS Bedrock doesn't support true streaming in the same way as OpenAI,
    but this demonstrates how you might handle streaming-like behavior.
    """
    words = full_response.split()
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        if i + chunk_size < len(words):
            chunk += " "
        yield chunk
        time.sleep(delay)

def simulated_streaming_example():
    """Demonstrate simulated streaming with chunked responses."""
    print("🌊 Simulated Streaming Response Example")
    print("=" * 50)
    
    client = BedrockLangfuseClient(debug=True)
    
    try:
        # Get the full response first
        response = client.chat_completion(
            model="anthropic.claude-3-haiku-20240307-v1:0",
            messages=[
                ChatMessage(
                    role=MessageRole.USER,
                    content="Write a short story about a robot learning to paint. Make it about 200 words."
                )
            ],
            config=ModelConfig(temperature=0.8, max_tokens=400),
            session_id="streaming-simulation-session",
            user_id="demo-user",
            metadata={
                "response_type": "simulated_streaming",
                "story_topic": "robot_painting"
            },
            tags=["demo", "streaming", "creative", "story"]
        )
        
        print("🤖 Streaming response (simulated):")
        print("-" * 40)
        
        # Simulate streaming by displaying chunks
        full_text = ""
        chunk_count = 0
        start_time = time.time()
        
        for chunk in simulate_streaming_response(response.content, chunk_size=15, delay=0.2):
            full_text += chunk
            chunk_count += 1
            print(chunk, end="", flush=True)
        
        streaming_time = time.time() - start_time
        
        print("\n" + "-" * 40)
        print(f"📊 Streaming Summary:")
        print(f"   Total chunks: {chunk_count}")
        print(f"   Streaming time: {streaming_time:.2f}s")
        print(f"   Original response time: {response.response_time:.2f}s")
        print(f"   Total tokens: {response.usage.total_tokens}")
        print(f"   Cost: ${response.usage.estimated_cost:.6f}")
        print(f"   Trace ID: {response.trace_id}")
        
    except Exception as e:
        print(f"Error in streaming simulation: {str(e)}")

def progressive_response_example():
    """Demonstrate progressive response building with multiple API calls."""
    print("\n🔄 Progressive Response Building Example")
    print("=" * 50)
    
    client = BedrockLangfuseClient(debug=True)
    session_id = "progressive-response-session"
    
    # Break down a complex request into smaller parts
    parts = [
        {
            "prompt": "Start explaining machine learning. Give me just the basic definition.",
            "step": "definition"
        },
        {
            "prompt": "Now add information about the main types of machine learning (supervised, unsupervised, reinforcement).",
            "step": "types"
        },
        {
            "prompt": "Finally, provide a simple real-world example of machine learning in action.",
            "step": "example"
        }
    ]
    
    try:
        print("🔨 Building response progressively:")
        print("-" * 40)
        
        full_response = ""
        total_tokens = 0
        total_cost = 0.0
        responses = []
        
        for i, part in enumerate(parts, 1):
            print(f"\n🔹 Step {i}: {part['step'].title()}")
            
            response = client.chat_completion(
                model="anthropic.claude-3-haiku-20240307-v1:0",
                messages=[
                    ChatMessage(role=MessageRole.USER, content=part["prompt"])
                ],
                config=ModelConfig(temperature=0.4, max_tokens=200),
                session_id=session_id,
                user_id="demo-user",
                metadata={
                    "response_type": "progressive",
                    "step": part["step"],
                    "step_number": i,
                    "total_steps": len(parts)
                },
                tags=["demo", "progressive", "machine_learning", part["step"]]
            )
            
            # Add to progressive response
            full_response += response.content + "\n\n"
            total_tokens += response.usage.total_tokens
            total_cost += response.usage.estimated_cost or 0
            responses.append(response)
            
            print(f"Response chunk: {response.content[:100]}...")
            print(f"Tokens: {response.usage.total_tokens}, Time: {response.response_time:.2f}s")
            
            # Simulate some processing time
            time.sleep(0.5)
        
        print("\n" + "=" * 40)
        print("📄 Complete Progressive Response:")
        print("-" * 40)
        print(full_response)
        
        print(f"📊 Progressive Response Summary:")
        print(f"   Total steps: {len(parts)}")
        print(f"   Total tokens: {total_tokens}")
        print(f"   Total cost: ${total_cost:.6f}")
        print(f"   Total response length: {len(full_response)} characters")
        
    except Exception as e:
        print(f"Error in progressive response: {str(e)}")

def real_time_interaction_simulation():
    """Simulate a real-time interaction with quick responses."""
    print("\n⚡ Real-Time Interaction Simulation")
    print("=" * 50)
    
    client = BedrockLangfuseClient(debug=True)
    session_id = "realtime-interaction-session"
    
    # Quick interaction scenarios
    interactions = [
        "Hi there!",
        "What's the weather like?",
        "Can you help me with math?",
        "What's 25 * 16?",
        "Thanks!",
        "Goodbye!"
    ]
    
    try:
        print("💬 Simulating real-time chat:")
        print("-" * 40)
        
        conversation_history = [
            ChatMessage(
                role=MessageRole.SYSTEM,
                content="You are a helpful assistant. Keep responses brief and friendly."
            )
        ]
        
        for i, user_input in enumerate(interactions, 1):
            print(f"\n👤 User: {user_input}")
            
            # Add user message to history
            conversation_history.append(
                ChatMessage(role=MessageRole.USER, content=user_input)
            )
            
            # Get quick response
            start_time = time.time()
            response = client.chat_completion(
                model="anthropic.claude-3-haiku-20240307-v1:0",  # Fast, cost-effective model
                messages=conversation_history,
                config=ModelConfig(temperature=0.3, max_tokens=50),  # Short responses
                session_id=session_id,
                user_id="demo-user",
                metadata={
                    "interaction_type": "realtime_simulation",
                    "interaction_number": i,
                    "total_interactions": len(interactions)
                },
                tags=["demo", "realtime", "quick_response", f"interaction_{i}"]
            )
            
            # Add assistant response to history
            conversation_history.append(
                ChatMessage(role=MessageRole.ASSISTANT, content=response.content)
            )
            
            response_time = time.time() - start_time
            
            print(f"🤖 Assistant: {response.content}")
            print(f"   ⏱️  Response time: {response_time:.2f}s")
            print(f"   🔢 Tokens: {response.usage.total_tokens}")
            print(f"   💰 Cost: ${response.usage.estimated_cost:.6f}")
            
            # Simulate user thinking/typing time
            time.sleep(random.uniform(0.5, 1.5))
        
        # Calculate conversation totals
        total_interactions = len(interactions)
        print(f"\n📊 Real-Time Conversation Summary:")
        print(f"   Total interactions: {total_interactions}")
        print(f"   Average response time: {sum(r.response_time or 0 for r in [response]):.2f}s")
        
    except Exception as e:
        print(f"Error in real-time simulation: {str(e)}")

def batched_streaming_example():
    """Demonstrate batched processing to simulate streaming behavior."""
    print("\n📦 Batched Streaming Example")
    print("=" * 50)
    
    client = BedrockLangfuseClient(debug=True)
    
    # Create multiple related prompts that build on each other
    story_prompts = [
        "Write the opening paragraph of a mystery story set in a library.",
        "Continue the story. The protagonist discovers something unusual.",
        "Add more suspense. What did they find?",
        "Build towards the climax of the mystery.",
        "Write the resolution and conclusion."
    ]
    
    try:
        print("📚 Creating story through batched streaming:")
        print("-" * 40)
        
        complete_story = ""
        session_id = "batched-streaming-session"
        
        for i, prompt in enumerate(story_prompts, 1):
            print(f"\n📝 Generating part {i}/5...")
            
            # Include previous parts for context
            context_messages = [
                ChatMessage(
                    role=MessageRole.SYSTEM,
                    content="You are a creative writer. Continue the story smoothly from where it left off."
                )
            ]
            
            if complete_story:
                context_messages.append(
                    ChatMessage(
                        role=MessageRole.USER,
                        content=f"Here's the story so far:\n{complete_story}\n\nNow: {prompt}"
                    )
                )
            else:
                context_messages.append(
                    ChatMessage(role=MessageRole.USER, content=prompt)
                )
            
            response = client.chat_completion(
                model="anthropic.claude-3-haiku-20240307-v1:0",
                messages=context_messages,
                config=ModelConfig(temperature=0.7, max_tokens=150),
                session_id=session_id,
                user_id="demo-user",
                metadata={
                    "streaming_type": "batched",
                    "story_part": i,
                    "total_parts": len(story_prompts),
                    "story_genre": "mystery"
                },
                tags=["demo", "batched_streaming", "creative", "mystery", f"part_{i}"]
            )
            
            # Add the new part to the complete story
            story_part = response.content.strip()
            complete_story += story_part + "\n\n"
            
            # Simulate streaming by displaying the new part
            print(f"📖 Part {i}: {story_part[:100]}...")
            print(f"   Tokens: {response.usage.total_tokens}")
            print(f"   Cost: ${response.usage.estimated_cost:.6f}")
            
            # Simulate processing time between parts
            time.sleep(1)
        
        print("\n" + "=" * 50)
        print("📖 Complete Story:")
        print("-" * 50)
        print(complete_story)
        
    except Exception as e:
        print(f"Error in batched streaming: {str(e)}")

def main():
    """Run all streaming and real-time examples."""
    print("🌊 AWS Bedrock Streaming & Real-Time Examples")
    print("=" * 60)
    
    simulated_streaming_example()
    progressive_response_example()
    real_time_interaction_simulation()
    batched_streaming_example()
    
    print("\n✅ All streaming examples have been logged to Langfuse!")

if __name__ == "__main__":
    main()
