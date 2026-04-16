import tkinter as tk
from tkinter import scrolledtext, filedialog, simpledialog
import threading
import os
from bot import ChatBot

class ChatbotUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini Chatbot UI")
        
        # Calculate half screen size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = screen_width // 2
        window_height = screen_height // 2
        
        # Set geometry to half the screen dimensions
        self.root.geometry(f"{window_width}x{window_height}")
        
        # Setup Menu
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Load System Prompt...", command=self.load_system_prompt)
        menubar.add_cascade(label="File", menu=filemenu)
        
        settingsmenu = tk.Menu(menubar, tearoff=0)
        settingsmenu.add_command(label="Memory Size...", command=self.set_memory_size)
        menubar.add_cascade(label="Settings", menu=settingsmenu)
        
        self.root.config(menu=menubar)
        
        # Layout using Place to respect the height requirements (8% for input, 92% for log)
        
        # Log area: 92% height
        self.log_frame = tk.Frame(self.root)
        self.log_frame.place(relwidth=1, relheight=0.92, relx=0, rely=0)
        
        self.chat_log = scrolledtext.ScrolledText(self.log_frame, state='disabled', wrap='word', font=("Arial", 11))
        self.chat_log.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Configure tags for colors
        self.chat_log.tag_config('user', foreground='red')
        self.chat_log.tag_config('bot', foreground='blue')
        self.chat_log.tag_config('system', foreground='gray')
        
        # Input area: 8% height
        self.input_frame = tk.Frame(self.root)
        self.input_frame.place(relwidth=1, relheight=0.08, relx=0, rely=0.92)
        
        self.prompt_entry = tk.Text(self.input_frame, font=("Arial", 11), wrap="word")
        self.prompt_entry.place(relwidth=0.70, relheight=1, relx=0, rely=0)
        self.prompt_entry.bind("<Return>", self.handle_return) # Bind Enter key to send
        
        self.radio_frame = tk.Frame(self.input_frame)
        self.radio_frame.place(relwidth=0.15, relheight=1, relx=0.70, rely=0)
        
        self.memory_var = tk.BooleanVar(value=True)
        tk.Radiobutton(self.radio_frame, text="Memory ON", variable=self.memory_var, value=True, command=self.toggle_memory).pack(anchor='w')
        tk.Radiobutton(self.radio_frame, text="Memory OFF", variable=self.memory_var, value=False, command=self.toggle_memory).pack(anchor='w')
        
        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.place(relwidth=0.15, relheight=1, relx=0.85, rely=0)
        
        # Initialize Bot
        self.bot = None
        self.append_log("System: Initializing chatbot...\n", "system")
        threading.Thread(target=self.init_bot, daemon=True).start()

    def handle_return(self, event):
        # Shift+Enter will insert a newline. Just Enter will send.
        if event.state & 0x0001:  # Shift pressed
            return None # let default behavior happen
        self.send_message()
        return "break" # prevent default behavior (newline insertion)

    def init_bot(self):
        try:
            self.bot = ChatBot()
            self.append_log("System: Chatbot ready!\n\n", "system")
        except Exception as e:
            self.append_log(f"System: Error initializing bot - {e}\n\n", "system")

    def toggle_memory(self):
        if self.bot:
            self.bot.memory_enabled = self.memory_var.get()
            state_str = "ON" if self.bot.memory_enabled else "OFF"
            self.append_log(f"System: Short Term Memory toggled {state_str}\n\n", "system")

    def set_memory_size(self):
        if not self.bot:
            return
        
        new_size = simpledialog.askinteger("Memory Size", "Enter number of previous conversations to remember:", initialvalue=self.bot.memory_size, minvalue=1, maxvalue=50)
        if new_size is not None:
            self.bot.memory_size = new_size
            self.append_log(f"System: Memory size set to {new_size} conversations\n\n", "system")

    def load_system_prompt(self):
        filename = filedialog.askopenfilename(title="Select System Prompt File", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    sys_prompt = f.read()
                
                if self.bot:
                    self.bot.reset_chat(sys_prompt)
                    
                # Reset display
                self.chat_log.config(state='normal')
                self.chat_log.delete('1.0', tk.END)
                self.chat_log.config(state='disabled')
                
                base_name = os.path.basename(filename)
                self.append_log(f"System: {base_name} loaded successfully.\n\n", "system")
                
            except Exception as e:
                self.append_log(f"System: Error loading file - {e}\n\n", "system")

    def append_log(self, text, tag):
        self.chat_log.config(state='normal')
        self.chat_log.insert(tk.END, text, tag)
        self.chat_log.config(state='disabled')
        self.chat_log.yview(tk.END)

    def send_message(self):
        if not self.bot:
            self.append_log("System: Bot is not ready yet.\n\n", "system")
            return
            
        user_text = self.prompt_entry.get("1.0", tk.END).strip()
        if not user_text:
            return
            
        # Log user message
        self.append_log(f"You: {user_text}\n", "user")
        self.prompt_entry.delete("1.0", tk.END)
        
        # Disable button and start model processing thread
        self.send_button.config(state='disabled')
        self.append_log("Bot: ", "bot")
        threading.Thread(target=self.fetch_response, args=(user_text,), daemon=True).start()

    def fetch_response(self, user_text):
        try:
            # We iterate through the stream and push UI updates back to the main thread securely.
            for chunk in self.bot.send_message_stream(user_text):
                if chunk.text:
                    self.root.after(0, self.append_chunk, chunk.text)
                    
            # After completing the message stream, insert double newline for spacing
            self.root.after(0, self.append_chunk, "\n\n")
            
        except Exception as e:
            self.root.after(0, self.append_log, f"\nSystem: Error - {e}\n\n", "system")
        finally:
            self.root.after(0, lambda: self.send_button.config(state='normal'))
            
    def append_chunk(self, text):
        self.chat_log.config(state='normal')
        self.chat_log.insert(tk.END, text, "bot")
        self.chat_log.config(state='disabled')
        self.chat_log.yview(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotUI(root)
    root.mainloop()
