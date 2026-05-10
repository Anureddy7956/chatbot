import os
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types
from memory_orchestrator import MemoryOrchestrator

class ChatBot:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found. Please set it in the .env file.")

        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.5-flash-lite"
        self.orchestrator = MemoryOrchestrator()
        self.system_instruction = None
        
        prompt_path = "system_prompt/receptionist_prompt.txt"
        if os.path.exists(prompt_path):
            with open(prompt_path, "r") as f:
                self.system_instruction = f.read()
                
        self.reset_chat()

    @property
    def memory_enabled(self):
        return self.orchestrator.memory_enabled

    @memory_enabled.setter
    def memory_enabled(self, value):
        self.orchestrator.memory_enabled = value

    @property
    def memory_size(self):
        return self.orchestrator.memory_size

    @memory_size.setter
    def memory_size(self, value):
        self.orchestrator.memory_size = value

    def reset_chat(self, system_instruction=None):
        if system_instruction is not None:
            self.system_instruction = system_instruction
        self.orchestrator.clear_history()
        self.update_config()

    def start_conversation(self):
        self.reset_chat()
        greeting = "Hello! I am your receptionist. May I know your name?"
        # Gemini API requires history to start with a 'user' message, so we add a dummy user prompt.
        self.orchestrator.add_to_history(types.Content(role="user", parts=[types.Part.from_text(text="Hi")]))
        self.orchestrator.add_to_history(types.Content(role="model", parts=[types.Part.from_text(text=greeting)]))
        return greeting

    def update_config(self):
        kwargs = {
            "thinking_config": types.ThinkingConfig(thinking_budget=0)
        }
        
        sys_prompt = self.system_instruction or "You are a receptionist."
        
        if self.orchestrator.current_user:
            sys_prompt += f"\n\nUser's name is {self.orchestrator.current_user}."
            prefs = self.orchestrator.get_user_preferences()
            if prefs:
                sys_prompt += f"\nUser's past preferences: {', '.join(prefs)}."
                
        kwargs["system_instruction"] = sys_prompt
        self.generate_content_config = types.GenerateContentConfig(**kwargs)

    def extract_name(self, message):
        match = re.search(r"(?i)(?:my name is|i am|i'm|this is|call me)\s+([a-zA-Z]+)", message)
        if match:
            return match.group(1).title()
        words = message.split()
        if len(words) <= 2:
            return words[0].title()
        return None

    def send_message_stream(self, message):
        if not self.orchestrator.current_user:
            name = self.extract_name(message)
            if name:
                self.orchestrator.set_user(name)
                self.update_config()
        else:
            self.orchestrator.extract_and_save_preferences(message)

        context = self.orchestrator.get_context()
        
        chat = self.client.chats.create(
            model=self.model,
            config=self.generate_content_config,
            history=context
        )
        
        response_text = ""
        for chunk in chat.send_message_stream(message):
            if chunk.text:
                response_text += chunk.text
            yield chunk
            
        self.orchestrator.add_to_history(types.Content(role="user", parts=[types.Part.from_text(text=message)]))
        self.orchestrator.add_to_history(types.Content(role="model", parts=[types.Part.from_text(text=response_text)]))

        if re.search(r"(?i)\bbye\b", message):
            self.orchestrator.save_conversation()
            self.reset_chat()

    def send_message(self, message):
        chat = self.client.chats.create(
            model=self.model,
            config=self.generate_content_config,
            history=self.orchestrator.get_context()
        )
        response = chat.send_message(message)
        
        if not self.orchestrator.current_user:
            name = self.extract_name(message)
            if name:
                self.orchestrator.set_user(name)
                self.update_config()
        else:
            self.orchestrator.extract_and_save_preferences(message)
            
        self.orchestrator.add_to_history(types.Content(role="user", parts=[types.Part.from_text(text=message)]))
        self.orchestrator.add_to_history(types.Content(role="model", parts=[types.Part.from_text(text=response.text)]))

        if re.search(r"(?i)\bbye\b", message):
            self.orchestrator.save_conversation()
            self.reset_chat()

        return response.text

    def load_conversation(self, filepath):
        if self.orchestrator.load_conversation(filepath):
            self.update_config()
            return True
        return False

def generate():
    try:
        bot = ChatBot()
    except ValueError as e:
        print(f"Error: {e}")
        return

    print("Chatbot started. Type 'quit' to exit.")
    greeting = bot.start_conversation()
    print(f"Bot: {greeting}")
    
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.strip().lower() == "quit":
                print("Exiting...")
                break

            if not user_input.strip():
                continue

            print("Bot: ", end="", flush=True)
            for chunk in bot.send_message_stream(user_input):
                if text := chunk.text:
                    print(text, end="", flush=True)
            print()
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    generate()
