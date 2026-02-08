import json
import os
from pathlib import Path

MEMORY_FILE = "storage/studio_memory.json"

class MemoryService:
    def __init__(self):
        self.memory_path = Path(MEMORY_FILE)
        if not self.memory_path.exists():
            self._save_memory({"directives": [], "feedback_history": []})

    def _load_memory(self) -> dict:
        try:
            with open(self.memory_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"directives": [], "feedback_history": []}

    def _save_memory(self, data: dict):
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.memory_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def get_context(self) -> str:
        """Returns a string of learned preferences to inject into Agent prompts."""
        data = self._load_memory()
        directives = data.get("directives", [])
        if not directives:
            return ""
        
        return "\n**STUDIO MEMORY (User Preferences - DO NOT IGNORE):**\n" + "\n".join([f"- {d}" for d in directives])

    def add_feedback(self, feedback: str):
        """Extracts potential persistent preferences from feedback."""
        data = self._load_memory()
        data["feedback_history"].append(feedback)
        
        # Simple heuristic: If feedback contains "always" or "never", treat as a directive
        if "always" in feedback.lower() or "never" in feedback.lower():
            # In a real system, an LLM would extract the core rule. 
            # Here we just save the raw feedback as a directive for now.
            data["directives"].append(feedback)
        
        # Keep last 10 directives
        if len(data["directives"]) > 10:
            data["directives"] = data["directives"][-10:]
            
        self._save_memory(data)

memory_service = MemoryService()
