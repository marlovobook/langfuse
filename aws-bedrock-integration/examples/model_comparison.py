"""Model comparison example using AWS Bedrock and Langfuse."""

from dotenv import load_dotenv
from bedrock_langfuse import BedrockLangfuseClient, ModelConfig
from bedrock_langfuse.utils import ModelComparison, format_cost

# Load environment variables
load_dotenv()

def basic_model_comparison():
    """Compare responses from multiple models for the same prompt."""
    print("🔬 Basic Model Comparison")
    print("=" * 50)
    
    # Initialize the comparison utility
    comparison = ModelComparison()
    
    # Models to compare (using cost-effective options for demo)
    models_to_compare = [
        "anthropic.claude-3-haiku-20240307-v1:0",
        "amazon.titan-text-express-v1",
        "cohere.command-light-text-v14"
    ]
    
    prompt = "Explain the concept of machine learning and provide a simple example."
    
    try:
        # Run the comparison
        results = comparison.compare_models(
            models=models_to_compare,
            prompt=prompt,
            session_id="model-comparison-basic",
            user_id="demo-user",
            metadata={
                "comparison_type": "basic",
                "prompt_category": "educational",
                "topic": "machine_learning"
            }
        )
        
        print(f"Prompt: {prompt}\n")
        
        # Display results
        for model, response in results.items():
            print(f"🤖 Model: {model}")
            print(f"📝 Response: {response.content[:200]}...")
            print(f"📊 Tokens: {response.usage.total_tokens}")
            print(f"💰 Cost: {format_cost(response.usage.estimated_cost or 0)}")
            print(f"⏱️  Time: {response.response_time:.2f}s")
            print(f"🆔 Trace: {response.trace_id}")
            print("-" * 40)
        
        # Calculate totals
        total_tokens = sum(r.usage.total_tokens for r in results.values())
        total_cost = sum(r.usage.estimated_cost or 0 for r in results.values())
        total_time = sum(r.response_time or 0 for r in results.values())
        
        print(f"📈 Comparison Summary:")
        print(f"   Models compared: {len(results)}")
        print(f"   Total tokens: {total_tokens}")
        print(f"   Total cost: {format_cost(total_cost)}")
        print(f"   Total time: {total_time:.2f}s")
        
    except Exception as e:
        print(f"Error in basic comparison: {str(e)}")

def advanced_model_comparison():
    """Advanced model comparison with different configurations."""
    print("\n🔬 Advanced Model Comparison")
    print("=" * 50)
    
    client = BedrockLangfuseClient(debug=True)
    comparison = ModelComparison(client)
    
    # Different configurations for comparison
    configs = {
        "creative": ModelConfig(temperature=0.9, max_tokens=300, top_p=0.95),
        "balanced": ModelConfig(temperature=0.7, max_tokens=300, top_p=0.9),
        "focused": ModelConfig(temperature=0.3, max_tokens=300, top_p=0.8)
    }
    
    # Different prompts for different use cases
    prompts = {
        "creative": "Write a creative short story about a robot discovering emotions.",
        "analytical": "Analyze the pros and cons of remote work vs office work.",
        "technical": "Explain how a neural network learns and makes predictions."
    }
    
    models = [
        "anthropic.claude-3-haiku-20240307-v1:0",
        "amazon.titan-text-express-v1"
    ]
    
    try:
        for prompt_type, prompt in prompts.items():
            print(f"\n📝 Prompt Type: {prompt_type.title()}")
            print(f"Prompt: {prompt}")
            print("-" * 40)
            
            for config_type, config in configs.items():
                print(f"\n⚙️  Configuration: {config_type.title()}")
                
                results = comparison.compare_models(
                    models=models,
                    prompt=prompt,
                    config=config,
                    session_id=f"advanced-comparison-{prompt_type}-{config_type}",
                    user_id="demo-user",
                    metadata={
                        "comparison_type": "advanced",
                        "prompt_type": prompt_type,
                        "config_type": config_type,
                        "temperature": config.temperature,
                        "max_tokens": config.max_tokens
                    }
                )
                
                # Quick summary for each model
                for model, response in results.items():
                    model_short = model.split('.')[-1]
                    print(f"  {model_short}: {response.usage.total_tokens} tokens, "
                          f"{format_cost(response.usage.estimated_cost or 0)}, "
                          f"{response.response_time:.1f}s")
                
    except Exception as e:
        print(f"Error in advanced comparison: {str(e)}")

def cost_effectiveness_analysis():
    """Analyze cost-effectiveness of different models."""
    print("\n💰 Cost-Effectiveness Analysis")
    print("=" * 50)
    
    comparison = ModelComparison()
    
    # Cost-focused model selection
    cost_effective_models = [
        "anthropic.claude-3-haiku-20240307-v1:0",  # Cheapest Anthropic
        "amazon.titan-text-lite-v1",               # Cheapest Amazon
        "cohere.command-light-text-v14"            # Cheapest Cohere
    ]
    
    # Standard prompt for cost comparison
    prompt = "Summarize the benefits of renewable energy in 3 bullet points."
    
    try:
        results = comparison.compare_models(
            models=cost_effective_models,
            prompt=prompt,
            session_id="cost-effectiveness-analysis",
            user_id="demo-user",
            metadata={
                "comparison_type": "cost_effectiveness",
                "analysis_focus": "cost_per_response"
            }
        )
        
        print(f"Prompt: {prompt}\n")
        
        # Analyze cost-effectiveness
        model_metrics = []
        for model, response in results.items():
            cost_per_token = (response.usage.estimated_cost or 0) / max(response.usage.total_tokens, 1)
            response_quality_score = len(response.content.split())  # Simple quality metric
            cost_effectiveness = response_quality_score / max(response.usage.estimated_cost or 0.001, 0.001)
            
            model_metrics.append({
                "model": model,
                "total_cost": response.usage.estimated_cost or 0,
                "total_tokens": response.usage.total_tokens,
                "cost_per_token": cost_per_token,
                "response_length": len(response.content),
                "response_words": response_quality_score,
                "cost_effectiveness": cost_effectiveness,
                "response_time": response.response_time or 0
            })
        
        # Sort by cost-effectiveness (higher is better)
        model_metrics.sort(key=lambda x: x["cost_effectiveness"], reverse=True)
        
        print("📊 Cost-Effectiveness Ranking:")
        for i, metrics in enumerate(model_metrics, 1):
            print(f"\n{i}. {metrics['model'].split('.')[-1]}")
            print(f"   💰 Total cost: {format_cost(metrics['total_cost'])}")
            print(f"   🔢 Tokens: {metrics['total_tokens']}")
            print(f"   📏 Response length: {metrics['response_length']} chars")
            print(f"   📈 Cost-effectiveness score: {metrics['cost_effectiveness']:.2f}")
            print(f"   ⏱️  Response time: {metrics['response_time']:.2f}s")
        
    except Exception as e:
        print(f"Error in cost-effectiveness analysis: {str(e)}")

def main():
    """Run all model comparison examples."""
    print("🔬 AWS Bedrock Model Comparison Examples")
    print("=" * 60)
    
    basic_model_comparison()
    advanced_model_comparison()
    cost_effectiveness_analysis()
    
    print("\n✅ All model comparisons have been logged to Langfuse!")

if __name__ == "__main__":
    main()
