from typing import Dict, Any, List
import os

try:
    from memori import Memori
except Exception:
    Memori = None

class MemoryAgent:
    def __init__(self):
        self.enabled = False

        if Memori is None:
            print("Memory Agent: memori not installed. Memory features are disabled.")
            return

        try:
            # Safely initialize Memori
            self.memori_client = Memori() 
            # Note: Assuming Memori config from environment or default
            # We skip 'database_connect' as it caused issues previously, relying on defaults
            self.memori_client.enable()
            self.enabled = True
        except Exception as e:
            print(f"Memory Agent failed to initialize: {e}")

    def get_context(self, query: str) -> str:
        if not self.enabled:
            return ""
        
        try:
            results = self.memori_client.search(query, limit=3)
            if results:
                return "\n".join([f"- {r}" for r in results])
        except Exception:
            return ""
        return ""

    def save_interaction(self, user_query: str, system_response: str):
        if not self.enabled:
            return
        
        try:
            self.memori_client.record_conversation(
                user_input=user_query,
                ai_output=system_response
            )
        except Exception:
            pass
