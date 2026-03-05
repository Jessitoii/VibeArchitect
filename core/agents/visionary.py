from core.agents.base import BaseAgent
from core.schema import Manifest


class VisionaryAgent(BaseAgent):
    def __init__(self, manifest: Manifest):
        super().__init__("Visionary", manifest)
        self.system_prompt = """
        You are 'The Visionary', the first agent in the VibeArchitect pipeline.
        Your goal is to receive a 'vibe' (a high-level project idea) and define the technical scope.
        
        OUTPUT FORMAT:
        You must output valid JSON matching the 'ProductScope' model:
        {
            "features": ["list of core features"],
            "tech_stack": {"frontend": "...", "backend": "...", "database": "..."},
            "constraints": ["limitations or specific requirements"],
            "high_level_goals": ["what the project aims to achieve"]
        }
        
        RULES:
        1. Be decisive. Choose a specific tech stack based on the vibe.
        2. Be technically sound. No 'fantasy' features.
        3. Ensure the tech stack is 'Antigravity-friendly' (modern, well-documented).
        """

    def get_prompt(self, vibe: str) -> str:
        return f"The User Vibe: {vibe}\n\nPlan the project scope based on this vibe."
