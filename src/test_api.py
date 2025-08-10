from api import RidgeAPI
from agents import AgentManager

def test_api_integration():
    """Test API with agent system"""
    
    # Load agents
    agent_manager = AgentManager()
    
    # Initialize API
    try:
        api = RidgeAPI()
    except ValueError as e:
        print(f"🔴 {e}")
        print("Please add your Anthropic API key to .env file")
        return
    
    # Test basic connection
    if not api.test_connection():
        return
    
    # Test with different agents
    debug_agent = agent_manager.get_agent('debug')
    partner_agent = agent_manager.get_agent('partner')
    
    # Test debug agent
    debug_flags = {'debug': True, 'quick': True}
    test_message = "I have a Python script that's throwing a 'list index out of range' error. What should I check?"
    
    print(f"\n🔧 Testing {debug_agent.name} agent...")
    response = api.chat_with_agent(debug_agent, test_message, debug_flags)
    print(f"Response: {response[:200]}...")
    
    # Test partner agent  
    partner_flags = {'quick': True}
    test_message2 = "How should I structure a new Python CLI project?"
    
    print(f"\n🤝 Testing {partner_agent.name} agent...")
    response2 = api.chat_with_agent(partner_agent, test_message2, partner_flags)
    print(f"Response: {response2[:200]}...")

if __name__ == '__main__':
    test_api_integration()