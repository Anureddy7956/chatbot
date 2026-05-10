import tkinter as tk
from tkinter import scrolledtext
import threading
import os
from bot import ChatBot

class CustomInputDialog(tk.Toplevel):
    def __init__(self, parent, title, prompt, initialvalue):
        super().__init__(parent)
        self.title(title)
        self.config(bg="#050505")
        self.result = None
        self.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        tk.Label(self, text=prompt, bg="#050505", fg="#FFD700", font=("Consolas", 12)).pack(padx=20, pady=10)
        self.entry = tk.Entry(self, bg="#121212", fg="#FFF200", insertbackground="#FFD700", font=("Consolas", 12), justify='center', borderwidth=0, highlightthickness=1, highlightbackground="#333300")
        self.entry.insert(0, str(initialvalue))
        self.entry.pack(padx=20, pady=5)
        self.entry.focus_set()
        
        btn_frame = tk.Frame(self, bg="#050505")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="OK", command=self.on_ok, bg="#1A1A00", fg="#FFD700", activebackground="#333300", activeforeground="#FFD700", font=("Consolas", 11, "bold"), borderwidth=0, cursor="hand2").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.destroy, bg="#1A1A00", fg="#FFD700", activebackground="#333300", activeforeground="#FFD700", font=("Consolas", 11, "bold"), borderwidth=0, cursor="hand2").pack(side="left", padx=5)
        
        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)

    def on_ok(self):
        try:
            self.result = int(self.entry.get())
            self.destroy()
        except ValueError:
            pass

class CustomFileDialog(tk.Toplevel):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x300+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        self.config(bg="#050505")
        self.result = None
        
        tk.Label(self, text="Select a Text File:", bg="#050505", fg="#FFD700", font=("Consolas", 12)).pack(padx=10, pady=(10, 0), anchor='w')
        
        self.listbox = tk.Listbox(self, bg="#121212", fg="#FFF200", font=("Consolas", 11), selectbackground="#333300", selectforeground="#FFD700", borderwidth=0, highlightthickness=1, highlightbackground="#333300")
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.files = []
        for root_dir, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            for file in files:
                if file.endswith('.txt'):
                    path = os.path.normpath(os.path.join(root_dir, file))
                    self.files.append(path)
                    self.listbox.insert(tk.END, path)
                    
        btn_frame = tk.Frame(self, bg="#050505")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Select", command=self.on_select, bg="#1A1A00", fg="#FFD700", activebackground="#333300", activeforeground="#FFD700", font=("Consolas", 11, "bold"), borderwidth=0, cursor="hand2").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.destroy, bg="#1A1A00", fg="#FFD700", activebackground="#333300", activeforeground="#FFD700", font=("Consolas", 11, "bold"), borderwidth=0, cursor="hand2").pack(side="left", padx=5)
        
        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)
        
    def on_select(self):
        selection = self.listbox.curselection()
        if selection:
            self.result = self.files[selection[0]]
            self.destroy()

class CustomConversationDialog(tk.Toplevel):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.title(title)
        self.geometry("500x400+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        self.config(bg="#050505")
        self.result = None
        
        tk.Label(self, text="Select a Saved Conversation:", bg="#050505", fg="#FFD700", font=("Consolas", 12)).pack(padx=10, pady=(10, 0), anchor='w')
        
        self.listbox = tk.Listbox(self, bg="#121212", fg="#FFF200", font=("Consolas", 10), selectbackground="#333300", selectforeground="#FFD700", borderwidth=0, highlightthickness=1, highlightbackground="#333300")
        self.listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.files = []
        conv_dir = os.path.join("memory", "conversations")
        if os.path.exists(conv_dir):
            for root_dir, dirs, files in os.walk(conv_dir):
                for file in files:
                    if file.endswith('.json'):
                        path = os.path.normpath(os.path.join(root_dir, file))
                        self.files.append(path)
                        # Display path relative to conversations folder for readability
                        display_path = os.path.relpath(path, conv_dir)
                        self.listbox.insert(tk.END, display_path)
                    
        btn_frame = tk.Frame(self, bg="#050505")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Load", command=self.on_select, bg="#1A1A00", fg="#FFD700", activebackground="#333300", activeforeground="#FFD700", font=("Consolas", 11, "bold"), borderwidth=0, cursor="hand2").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.destroy, bg="#1A1A00", fg="#FFD700", activebackground="#333300", activeforeground="#FFD700", font=("Consolas", 11, "bold"), borderwidth=0, cursor="hand2").pack(side="left", padx=5)
        
        self.transient(parent)
        self.grab_set()
        parent.wait_window(self)
        
    def on_select(self):
        selection = self.listbox.curselection()
        if selection:
            self.result = self.files[selection[0]]
            self.destroy()

class ChatbotUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gemini Chatbot - Ultra Edition")
        
        # --- UI Theme Colors & Fonts ---
        self.BG_COLOR = "#050505"      # Deep Black
        self.TEXT_BG = "#0A0A0A"       # Slightly lighter black for text areas
        self.INPUT_BG = "#121212"      # Dark gray-black for input
        self.FG_COLOR = "#FFD700"      # Gold / Yellow
        self.USER_FG = "#FFF200"       # Bright Yellow for User
        self.BOT_FG = "#FFC800"        # Warm Yellow for Bot
        self.SYS_FG = "#8A8A00"        # Dark Yellow/Olive for System
        self.BTN_BG = "#1A1A00"        # Dark yellow-tinted background for buttons
        
        self.FONT_MAIN = ("Consolas", 15)
        self.FONT_BOLD = ("Consolas", 15, "bold")
        self.FONT_SYS = ("Consolas", 13, "italic")
        self.FONT_BTN = ("Consolas", 14, "bold")
        
        # Calculate half screen size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.6)
        window_height = int(screen_height * 0.7)
        
        # Set geometry to centered dimensions
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.configure(bg=self.BG_COLOR)
        
        # Setup Menu (Dark themed if OS supports)
        menubar = tk.Menu(self.root, bg=self.BG_COLOR, fg=self.FG_COLOR, activebackground=self.FG_COLOR, activeforeground=self.BG_COLOR)
        filemenu = tk.Menu(menubar, tearoff=0, bg=self.BG_COLOR, fg=self.FG_COLOR)
        filemenu.add_command(label="Load System Prompt...", command=self.load_system_prompt)
        filemenu.add_command(label="Load Conversation...", command=self.load_conversation)
        filemenu.add_command(label="Restart Conversation", command=self.restart_conversation)
        menubar.add_cascade(label="File", menu=filemenu)
        
        settingsmenu = tk.Menu(menubar, tearoff=0, bg=self.BG_COLOR, fg=self.FG_COLOR)
        settingsmenu.add_command(label="Memory Size...", command=self.set_memory_size)
        menubar.add_cascade(label="Settings", menu=settingsmenu)
        
        self.root.config(menu=menubar)
        
        # Layout using Place to respect the height requirements (12% for input, 88% for log)
        
        # Log area
        self.log_frame = tk.Frame(self.root, bg=self.BG_COLOR)
        self.log_frame.place(relwidth=1, relheight=0.86, relx=0, rely=0)
        
        self.chat_log = scrolledtext.ScrolledText(
            self.log_frame, state='disabled', wrap='word', 
            font=self.FONT_MAIN, bg=self.TEXT_BG, fg=self.BOT_FG,
            insertbackground=self.FG_COLOR, borderwidth=0,
            highlightthickness=2, highlightbackground="#222200", highlightcolor=self.FG_COLOR
        )
        self.chat_log.pack(fill='both', expand=True, padx=15, pady=(15, 5))
        
        # Configure tags for colors
        self.chat_log.tag_config('user', foreground=self.USER_FG, font=self.FONT_BOLD, spacing1=10, spacing3=10)
        self.chat_log.tag_config('bot', foreground=self.BOT_FG, spacing1=5, spacing3=10)
        self.chat_log.tag_config('system', foreground=self.SYS_FG, font=self.FONT_SYS, justify='center')
        
        # Input area
        self.input_frame = tk.Frame(self.root, bg=self.BG_COLOR)
        self.input_frame.place(relwidth=1, relheight=0.14, relx=0, rely=0.86)
        
        self.prompt_entry = tk.Text(
            self.input_frame, font=self.FONT_MAIN, wrap="word", 
            bg=self.INPUT_BG, fg=self.FG_COLOR, insertbackground=self.FG_COLOR,
            borderwidth=0, highlightthickness=2, highlightbackground="#333300", highlightcolor=self.FG_COLOR
        )
        self.prompt_entry.place(relwidth=0.72, relheight=0.7, relx=0.02, rely=0.15)
        self.prompt_entry.bind("<Return>", self.handle_return) # Bind Enter key to send
        
        self.radio_frame = tk.Frame(self.input_frame, bg=self.BG_COLOR)
        self.radio_frame.place(relwidth=0.12, relheight=0.7, relx=0.75, rely=0.15)
        
        self.memory_var = tk.BooleanVar(value=True)
        tk.Radiobutton(self.radio_frame, text="Mem ON", variable=self.memory_var, value=True, command=self.toggle_memory, 
                       bg=self.BG_COLOR, fg=self.FG_COLOR, selectcolor="#222", activebackground=self.BG_COLOR, 
                       activeforeground=self.USER_FG, font=("Consolas", 11)).pack(anchor='w', pady=2)
        tk.Radiobutton(self.radio_frame, text="Mem OFF", variable=self.memory_var, value=False, command=self.toggle_memory, 
                       bg=self.BG_COLOR, fg=self.FG_COLOR, selectcolor="#222", activebackground=self.BG_COLOR, 
                       activeforeground=self.USER_FG, font=("Consolas", 11)).pack(anchor='w')
        
        self.send_button = tk.Button(
            self.input_frame, text="SEND", command=self.send_message,
            bg=self.BTN_BG, fg=self.FG_COLOR, activebackground="#333300", activeforeground=self.USER_FG,
            font=self.FONT_BTN, borderwidth=0, cursor="hand2"
        )
        self.send_button.place(relwidth=0.10, relheight=0.7, relx=0.88, rely=0.15)
        
        # Initialize Bot
        self.bot = None
        self.append_log("\n--- System: Initializing chatbot... ---\n", "system")
        threading.Thread(target=self.init_bot, daemon=True).start()

    def handle_return(self, event):
        if event.state & 0x0001:  # Shift pressed
            return None
        self.send_message()
        return "break"

    def init_bot(self):
        try:
            self.bot = ChatBot()
            self.append_log("--- System: Chatbot ready! ---\n\n", "system")
            greeting = self.bot.start_conversation()
            self.root.after(0, self.append_log, f"Bot:\n{greeting}\n\n", "bot")
        except Exception as e:
            self.append_log(f"--- System: Error initializing bot - {e} ---\n\n", "system")

    def restart_conversation(self):
        if self.bot:
            greeting = self.bot.start_conversation()
            self.chat_log.config(state='normal')
            self.chat_log.delete('1.0', tk.END)
            self.chat_log.config(state='disabled')
            self.append_log("\n--- System: Conversation restarted. ---\n\n", "system")
            self.append_log(f"Bot:\n{greeting}\n\n", "bot")

    def toggle_memory(self):
        if self.bot:
            self.bot.memory_enabled = self.memory_var.get()
            state_str = "ON" if self.bot.memory_enabled else "OFF"
            self.append_log(f"\n--- System: Short Term Memory toggled {state_str} ---\n\n", "system")

    def set_memory_size(self):
        if not self.bot:
            return
        
        dialog = CustomInputDialog(self.root, "Memory Size", "Enter number of previous conversations to remember:", self.bot.memory_size)
        if dialog.result is not None:
            self.bot.memory_size = dialog.result
            self.append_log(f"\n--- System: Memory size set to {dialog.result} conversations ---\n\n", "system")

    def load_system_prompt(self):
        dialog = CustomFileDialog(self.root, "Select System Prompt File")
        if dialog.result:
            try:
                with open(dialog.result, 'r', encoding='utf-8') as f:
                    sys_prompt = f.read()
                
                if self.bot:
                    self.bot.reset_chat(sys_prompt)
                    
                self.chat_log.config(state='normal')
                self.chat_log.delete('1.0', tk.END)
                self.chat_log.config(state='disabled')
                
                base_name = os.path.basename(dialog.result)
                self.append_log(f"\n--- System: {base_name} loaded successfully. ---\n\n", "system")
                greeting = self.bot.start_conversation()
                self.append_log(f"Bot:\n{greeting}\n\n", "bot")
                
            except Exception as e:
                self.append_log(f"\n--- System: Error loading file - {e} ---\n\n", "system")

    def load_conversation(self):
        if not self.bot:
            return
        
        # Save current if exists before loading
        self.bot.orchestrator.save_conversation()
        
        dialog = CustomConversationDialog(self.root, "Select Conversation")
        if dialog.result:
            try:
                if self.bot.load_conversation(dialog.result):
                    self.chat_log.config(state='normal')
                    self.chat_log.delete('1.0', tk.END)
                    self.chat_log.config(state='disabled')
                    
                    self.append_log(f"--- System: Loaded conversation from {os.path.basename(dialog.result)} ---\n\n", "system")
                    
                    # Display history in UI
                    for item in self.bot.orchestrator._all_history:
                        role = "You" if item.role == "user" else "Bot"
                        tag = "user" if item.role == "user" else "bot"
                        text = "".join([p.text for p in item.parts if p.text])
                        self.append_log(f"{role}:\n{text}\n\n", tag)
                else:
                    self.append_log("--- System: Failed to load conversation ---\n\n", "system")
            except Exception as e:
                self.append_log(f"--- System: Error loading conversation - {e} ---\n\n", "system")

    def append_log(self, text, tag):
        self.chat_log.config(state='normal')
        self.chat_log.insert(tk.END, text, tag)
        self.chat_log.config(state='disabled')
        self.chat_log.yview(tk.END)

    def send_message(self):
        if not self.bot:
            self.append_log("\n--- System: Bot is not ready yet. ---\n\n", "system")
            return
            
        user_text = self.prompt_entry.get("1.0", tk.END).strip()
        if not user_text:
            return
            
        self.append_log(f"You:\n{user_text}\n", "user")
        self.prompt_entry.delete("1.0", tk.END)
        
        self.send_button.config(state='disabled')
        self.append_log("Bot:\n", "bot")
        threading.Thread(target=self.fetch_response, args=(user_text,), daemon=True).start()

    def fetch_response(self, user_text):
        try:
            for chunk in self.bot.send_message_stream(user_text):
                if chunk.text:
                    self.root.after(0, self.append_chunk, chunk.text)
                    
            self.root.after(0, self.append_chunk, "\n\n")
            
        except Exception as e:
            self.root.after(0, self.append_log, f"\n--- System: Error - {e} ---\n\n", "system")
        finally:
            self.root.after(0, lambda: self.send_button.config(state='normal'))
            # Check if bot was reset (e.g. by 'bye')
            if not self.bot.orchestrator._all_history:
                self.root.after(500, self.handle_post_bye_reset)

    def handle_post_bye_reset(self):
        self.append_log("\n--- System: Conversation saved and memories reset. ---\n", "system")
        greeting = self.bot.start_conversation()
        self.append_log(f"Bot:\n{greeting}\n\n", "bot")
            
    def append_chunk(self, text):
        self.chat_log.config(state='normal')
        self.chat_log.insert(tk.END, text, "bot")
        self.chat_log.config(state='disabled')
        self.chat_log.yview(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotUI(root)
    root.mainloop()
