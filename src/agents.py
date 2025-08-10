import os
from pathlib import Path

class Agent:
    """Represents a single AI agent with personality and instructions"""
    
    def __init__(self, name, filepath):
        self.name = name
        self.filepath = filepath
        self.content = ""
        self.role = ""
        self.personality = ""
        self.response_style = ""
        self.specialties = ""
        
        # Load and parse the agent file
        self._load_agent_file()
    
    def _load_agent_file(self):
        """Load and parse the .md agent configuration"""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self.content = f.read()
            
            # Parse sections (basic parsing for now)
            self._parse_sections()
            
        except Exception as e:
            print(f"Error loading agent {self.name}: {e}")
    
    def _parse_sections(self):
        """Extract key sections from markdown content"""
        lines = self.content.split('\n')
        current_section = None
        section_content = []
        
        for line in lines:
            if line.startswith('## Role'):
                current_section = 'role'
                section_content = []
            elif line.startswith('## Personality'):
                current_section = 'personality'
                section_content = []
            elif line.startswith('## Response Style'):
                current_section = 'response_style'
                section_content = []
            elif line.startswith('## Specialties'):
                current_section = 'specialties'
                section_content = []
            elif line.startswith('##'):
                # End current section
                if current_section:
                    self._set_section_content(current_section, '\n'.join(section_content))
                current_section = None
                section_content = []
            elif current_section and line.strip():
                section_content.append(line)
        
        # Handle last section
        if current_section:
            self._set_section_content(current_section, '\n'.join(section_content))
    
    def _set_section_content(self, section, content):
        """Set parsed section content"""
        setattr(self, section, content.strip())
    
    def get_system_prompt(self):
        """Generate system prompt for this agent"""
        return f"""You are the {self.name} agent.

{self.role}

Personality: {self.personality}

Response Style: {self.response_style}

Specialties: {self.specialties}

Always embody this personality and approach in your responses."""

class AgentManager:
    """Manages loading and selection of AI agents"""
    
    def __init__(self, agents_dir="agents"):
        self.agents_dir = Path(agents_dir)
        self.agents = {}
        self.default_agent = "partner"
        
        # Load all available agents
        self._load_agents()
    
    def _load_agents(self):
        """Load all .md agent files from agents directory"""
        if not self.agents_dir.exists():
            print(f"Agents directory {self.agents_dir} not found")
            return
        
        for agent_file in self.agents_dir.glob("*.md"):
            agent_name = agent_file.stem  # filename without extension
            agent = Agent(agent_name, agent_file)
            self.agents[agent_name] = agent
            print(f"Loaded agent: {agent_name}")
    
    def get_agent(self, agent_name=None):
        """Get agent by name, fallback to default"""
        if agent_name is None:
            agent_name = self.default_agent
        
        return self.agents.get(agent_name, self.agents.get(self.default_agent))
    
    def list_agents(self):
        """List all available agents"""
        return list(self.agents.keys())
    
    def select_agent_from_flags(self, mode_flags):
        """Select appropriate agent based on CLI flags"""
        # Priority order for agent selection
        if mode_flags.get('debug'):
            return self.get_agent('debug')
        elif mode_flags.get('explain'):
            return self.get_agent('professor')
        elif mode_flags.get('manager'):
            return self.get_agent('manager')
        elif mode_flags.get('code'):
            return self.get_agent('code')
        else:
            return self.get_agent('partner')  # default