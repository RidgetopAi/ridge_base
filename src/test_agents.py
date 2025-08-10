from agents import AgentManager

def test_agents():
    """Test agent loading and selection"""
    manager = AgentManager()
    
    print(f"Available agents: {manager.list_agents()}")
    
    # Test default agent
    default = manager.get_agent()
    print(f"\nDefault agent: {default.name}")
    print(f"Role: {default.role[:100]}...")
    
    # Test agent selection from flags
    debug_flags = {'debug': True, 'interactive': False}
    debug_agent = manager.select_agent_from_flags(debug_flags)
    print(f"\nDebug agent selected: {debug_agent.name}")
    
    # Test system prompt generation
    prompt = debug_agent.get_system_prompt()
    print(f"\nSystem prompt preview: {prompt[:200]}...")

if __name__ == '__main__':
    test_agents()