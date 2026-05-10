import os
import json
import re
import datetime
from google.genai import types

class MemoryOrchestrator:
    def __init__(self, profile_path="memory/user_profile.json"):
        self.profile_path = profile_path
        self.memory_enabled = True
        self.memory_size = 5
        self._all_history = []
        self.current_user = None
        self.user_profiles = self._load_profiles()
        
    def _load_profiles(self):
        if os.path.exists(self.profile_path):
            with open(self.profile_path, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return {}
        return {}
        
    def _save_profiles(self):
        os.makedirs(os.path.dirname(self.profile_path), exist_ok=True)
        with open(self.profile_path, 'w') as f:
            json.dump(self.user_profiles, f, indent=4)
            
    def set_user(self, name):
        self.current_user = name
        if name not in self.user_profiles:
            self.user_profiles[name] = {"preferences": []}
            self._save_profiles()
            
    def get_user_preferences(self):
        if self.current_user and self.current_user in self.user_profiles:
            return self.user_profiles[self.current_user].get("preferences", [])
        return []
        
    def extract_and_save_preferences(self, user_message):
        if not self.current_user:
            return
            
        pattern = r"(?i)(?:my choice is|i like|i want|i love|i am found of|i am fond of)\s+([^.]+)"
        matches = re.findall(pattern, user_message)
        if matches:
            prefs = self.user_profiles[self.current_user].get("preferences", [])
            for match in matches:
                pref = match.strip()
                if pref not in prefs:
                    prefs.append(pref)
            self.user_profiles[self.current_user]["preferences"] = prefs
            self._save_profiles()
            
    def add_to_history(self, content_obj):
        self._all_history.append(content_obj)
        
    def get_context(self):
        if self.memory_enabled and self.memory_size > 0:
            limit = self.memory_size * 2
            return self._all_history[-limit:] if len(self._all_history) > limit else self._all_history
        return []
        
    def clear_history(self):
        self._all_history = []
        self.current_user = None

    def save_conversation(self):
        if not self._all_history:
            return
            
        username = self.current_user if self.current_user else "guest"
        base_dir = os.path.join("memory", "conversations", username)
        os.makedirs(base_dir, exist_ok=True)
        
        now = datetime.datetime.now()
        filename = now.strftime("%H%M%S_%d%m%Y.json")
        filepath = os.path.join(base_dir, filename)
        
        history_to_save = []
        for item in self._all_history:
            parts = [{"text": part.text} for part in item.parts if part.text]
            history_to_save.append({
                "role": item.role,
                "parts": parts
            })
            
        with open(filepath, "w") as f:
            json.dump(history_to_save, f, indent=4)
            
    def load_conversation(self, filepath):
        if not os.path.exists(filepath):
            return False
            
        with open(filepath, "r") as f:
            history_data = json.load(f)
            
        self._all_history = []
        for item in history_data:
            parts = [types.Part.from_text(text=part["text"]) for part in item["parts"]]
            content = types.Content(role=item["role"], parts=parts)
            self._all_history.append(content)
            
        parts = os.path.normpath(filepath).split(os.sep)
        if len(parts) >= 3 and parts[-3] == "conversations":
            username = parts[-2]
            if username != "guest":
                self.set_user(username)
            else:
                self.current_user = None
                
        return True
