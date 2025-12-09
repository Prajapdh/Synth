import os
import yaml
from typing import Dict, Any, Optional

class KnowledgeManager:
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.project_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'projects', project_name)
        
        if not os.path.exists(self.project_root):
            raise ValueError(f"Project '{project_name}' does not exist at {self.project_root}")
            
        self.config_path = os.path.join(self.project_root, 'config.yaml')
        self.knowledge_path = os.path.join(self.project_root, 'knowledge.md')
        
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            return {}
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f) or {}

    def get_knowledge(self) -> str:
        """Returns the content of the knowledge.md file."""
        if not os.path.exists(self.knowledge_path):
            return ""
        with open(self.knowledge_path, 'r') as f:
            return f.read()

    def append_knowledge(self, content: str):
        """Appends new insights to the knowledge.md file."""
        with open(self.knowledge_path, 'a') as f:
            f.write(f"\n\n{content}")

    def get_base_url(self) -> Optional[str]:
        return self.config.get('base_url')

    def get_credentials(self, user_role: str = 'default') -> Optional[Dict[str, str]]:
        """Retrieves credentials for a specific role from config."""
        creds = self.config.get('credentials', {})
        return creds.get(user_role)
