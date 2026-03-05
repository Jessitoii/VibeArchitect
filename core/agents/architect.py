from core.agents.base import BaseAgent
from core.schema import Manifest


class ArchitectAgent(BaseAgent):
    def __init__(self, manifest: Manifest):
        super().__init__("Architect", manifest)
        self.system_prompt = """
        You are 'The UI/UX Architect'.
        Your goal is to take the Product Scope and break it into screens and components.
        
        OUTPUT FORMAT:
        You must output valid JSON matching the 'UIMap' model:
        {
            "screens": [
                {
                    "name": "Screen Name",
                    "components": [
                        {"name": "Component Name", "description": "...", "logic": "...", "data_source_id": "X_ID"}
                    ],
                    "user_journey": "..."
                }
            ],
            "theme": {"primary": "...", "secondary": "..."}
        }
        
        RULES:
        1. Atomic Breakdown. Every screen must list its primary components.
        2. Logic Mapping. Define 'What happens if X button is clicked' in the logic field.
        3. Cross-Ref IDs. Every component needs a 'data_source_id' that the System Engineer can use.
        """

    def get_prompt(self, vibe: str) -> str:
        scope = (
            self.manifest.product_scope.model_dump_json(indent=2)
            if self.manifest.product_scope
            else "{} "
        )
        return f"Product Scope: {scope}\n\nMap the UI components and user journeys."
