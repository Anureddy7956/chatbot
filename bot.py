import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

class ChatBot:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found. Please set it in the .env file.")

        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.5-flash-lite"
        self.memory_enabled = True
        self.memory_size = 5
        self.system_instruction = None
        self._all_history = []
        self.reset_chat()

    def reset_chat(self, system_instruction=None):
        if system_instruction is not None:
            self.system_instruction = system_instruction
        self._all_history = []
        
        kwargs = {
            "thinking_config": types.ThinkingConfig(thinking_budget=0)
        }
        if self.system_instruction:
            kwargs["system_instruction"] = self.system_instruction
            
        self.generate_content_config = types.GenerateContentConfig(**kwargs)

    def send_message_stream(self, message):
        context = []
        if self.memory_enabled and self.memory_size > 0:
            limit = self.memory_size * 2
            context = self._all_history[-limit:] if len(self._all_history) > limit else self._all_history
            
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
            
        self._all_history.append(types.Content(role="user", parts=[types.Part.from_text(text=message)]))
        self._all_history.append(types.Content(role="model", parts=[types.Part.from_text(text=response_text)]))
        
    def send_message(self, message):
        response = self.chat.send_message(message)
        return response.text

def generate():
    try:
        bot = ChatBot()
    except ValueError as e:
        print(f"Error: {e}")
        return

    print("Chatbot started. Type 'quit' to exit.")
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
