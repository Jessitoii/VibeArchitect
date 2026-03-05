from core.agents.base import BaseAgent
from core.schema import Manifest


class ExpertAgent(BaseAgent):
    def __init__(self, manifest: Manifest):
        super().__init__("Expert", manifest)
        self.system_prompt = """
        You are 'The Antigravity Expert'.
        Your job is to translate the entire blueprint into a highly structured `.agent` Instructional Brain to be consumed by an execution agent.
        
        OUTPUT FORMAT:
        You must output valid JSON matching the 'InstructionalBrain' model:
        {
            "gemini_md": "The master index markdown string, acting as the DNA of the project...",
            "metadata_json": {"version": 1, "index": ["lists", "of", "links"]},
            "rules": [
                {"filename": "naming_conventions.md", "content": "...", "description": "Names"}
            ],
            "workflows": [
                {
                    "filename": "phase_1_setup.md", 
                    "content": "Actionable Prompt for the Antigravity Agent...", 
                    "success_criteria": ["1. Database connected", "2. Auth works"]
                }
            ],
            "docs": [
                {"filename": "API_Specs.md", "content": "..."}
            ],
            "skills": [
                {"filename": "snippet.py", "content": "..."}
            ]
        }
        
        RULES:
        1. Context-Aware Rules. Generate specific `.md` rules files based on the "vibe" (e.g., trading_security.md for finance apps).
        2. Verification Hooks. For every workflow file, you MUST determine clear, testable success criteria.
        3. Cross-Linking. `gemini_md` must explicitly use markdown links to reference the files in `rules/`, `workflows/`, and `docs/`.
        4. Technical Docs. Create detailed specs like `API_Specs.md` and `Data_Models.md` (with Mermaid diagrams) if applicable.
        """

    def get_prompt(self, vibe: str) -> str:
        manifest_data = self.manifest.model_dump_json(
            indent=2, exclude={"audit_log", "instructional_brain"}
        )
        return f"Full Blueprint Manifest: {manifest_data}\n\nGenerate the complete `.agent` Instructional Brain structure."
