import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RidgeAPI:
    """Handles communication with Anthropic's Claude API"""
    
    def __init__(self):
        self.client = None
        self._setup_client()
        
        # Model selection based on flags
        self.model_map = {
            'quick': 'claude-3-5-haiku-20241022',
            'default': 'claude-3-5-sonnet-20241022', 
            'deep': 'claude-3-5-sonnet-20241022',
            'ultra_deep': 'claude-3-opus-20240229'
        }
    
    def _setup_client(self):
        """Initialize Anthropic client with API key"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        self.client = Anthropic(api_key=api_key)
        print("✅ Anthropic API client initialized")
    
    def select_model(self, mode_flags):
        """Select appropriate model based on flags"""
        if mode_flags.get('ultra') and mode_flags.get('deep'):
            return self.model_map['ultra_deep']
        elif mode_flags.get('deep'):
            return self.model_map['deep']
        elif mode_flags.get('quick'):
            return self.model_map['quick']
        else:
            return self.model_map['default']
    
    def chat_with_agent(self, agent, user_message, mode_flags, context=None):
        """Send message to Claude with agent personality"""
        try:
            # Get agent's system prompt
            system_prompt = agent.get_system_prompt()
            
            # Add context if provided
            if context:
                system_prompt += f"\n\nProject Context:\n{context}"
            
            # Select appropriate model
            model = self.select_model(mode_flags)
            
            # Build message for Claude
            messages = [
                {
                    "role": "user", 
                    "content": user_message
                }
            ]
            
            print(f"🤖 Using {agent.name} agent with {model}")
            
            # Send to Claude
            response = self.client.messages.create(
                model=model,
                max_tokens=4000,
                system=system_prompt,
                messages=messages
            )
            
            return response.content[0].text
            
        except Exception as e:
            return f"Error communicating with Claude: {str(e)}"
    
    def test_connection(self):
        """Test basic API connection"""
        try:
            response = self.client.messages.create(
                model=self.model_map['quick'],
                max_tokens=100,
                system="You are a helpful assistant.",
                messages=[{"role": "user", "content": "Say hello and confirm you're working."}]
            )
            
            print("✅ API connection test successful")
            print(f"Response: {response.content[0].text}")
            return True
            
        except Exception as e:
            print(f"❌ API connection failed: {e}")
            return False