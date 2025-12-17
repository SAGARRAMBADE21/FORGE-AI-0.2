"""
Quick setup script for Groq API
"""

import os
import sys

print("=" * 80)
print("🔑 GROQ API Setup")
print("=" * 80)
print()

# Check if GROQ_API_KEY is set
groq_key = os.getenv("GROQ_API_KEY")

if groq_key:
    print("✅ GROQ_API_KEY is already set!")
    print(f"   Key: {groq_key[:10]}...{groq_key[-5:]}")
else:
    print("⚠️  GROQ_API_KEY not found in environment")
    print()
    print("To set it up:")
    print()
    print("1. Get your free API key from: https://console.groq.com/keys")
    print()
    print("2. Set environment variable:")
    print()
    print("   Windows PowerShell:")
    print('   $env:GROQ_API_KEY="your_groq_api_key_here"')
    print()
    print("   Or create a .env file:")
    print("   GROQ_API_KEY=your_groq_api_key_here")
    print()
    
    # Prompt user
    try:
        key = input("\nPaste your Groq API key here (or press Enter to skip): ").strip()
        if key:
            # Save to .env file
            env_file = os.path.join(os.path.dirname(__file__), ".env")
            with open(env_file, "a") as f:
                f.write(f"\nGROQ_API_KEY={key}\n")
            print(f"\n✅ Saved to {env_file}")
            print("   Restart your terminal or run: source .env")
    except KeyboardInterrupt:
        print("\n\nSkipped.")

print()
print("=" * 80)
print("Testing LLM Factory...")
print("=" * 80)

try:
    sys.path.insert(0, os.path.dirname(__file__))
    from backend_agent.utils.llm_factory import create_llm, get_available_models
    
    print("\n✅ LLM Factory imported successfully")
    
    print("\n📋 Available Groq Models:")
    for model in get_available_models("groq"):
        print(f"   - {model}")
    
    print("\n📋 Available OpenAI Models:")
    for model in get_available_models("openai"):
        print(f"   - {model}")
    
    if groq_key:
        print("\n🧪 Testing Groq connection...")
        try:
            llm = create_llm({
                "provider": "groq",
                "model": "llama-3.3-70b-versatile",
                "temperature": 0.1
            })
            print("✅ Groq LLM created successfully!")
            print(f"   Model: llama-3.3-70b-versatile")
        except Exception as e:
            print(f"❌ Error: {e}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("Setup Summary")
print("=" * 80)
print()
print("Current Configuration:")
print(f"  Provider: Groq (default)")
print(f"  Model: llama-3.3-70b-versatile")
print(f"  Status: {'✅ Ready' if groq_key else '⚠️  API key needed'}")
print()
print("To switch to OpenAI in the future:")
print("  1. Get OpenAI key: https://platform.openai.com/api-keys")
print("  2. Set: $env:OPENAI_API_KEY='your_key'")
print("  3. Update backend-config.yaml: provider: 'openai'")
print()
print("=" * 80)
