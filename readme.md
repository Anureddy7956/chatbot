# Chatbot Project

A Python chatbot using the `google-genai` library and `gemini-2.5-flash-lite` model.

## Folder Architecture
- `bot.py` : Contains the main chatbot code
- `ui.py` : Contains the chatbot ui code
- `.env` : Contains the `GEMINI_API_KEY` for secure access
- `requirements.txt` : Contains the required Python packages
- `readme.md` : Contains setup and run instructions

## Setup Instructions

1. Ensure you have Conda installed. Create or activate the conda environment required for this project:
   ```bash
   conda activate env_name
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Your `.env` file should contain the API key:
   ```env
   GEMINI_API_KEY="your_api_key_here"
   ```

## Running the Chatbot

You can now start the graphical user interface by running:
```bash
python ui.py
```

Alternatively, you can run the CLI version:
```bash
python bot.py
```
- Type your prompt in the terminal to chat.
- Type `quit` and press enter to exit the application.
