# 🤖 Discord Bot with LLM Integration

This is a Python-based Discord bot that connects to local G4F API. Thanks to [G4F](https://github.com/xtekky/gpt4free) <3. It supports text-based conversations with memory and multimodal input (text + image), as well as image generation.

---

## 📦 Features

- 💬 **Chat with LLMs** via `!chat <prompt>`
- 🧠 **Per-user memory** for contextual answers
- 🖼️ **Image input** support in conversations
- 🎨 **Image generation** via `!generate <prompt>`
- 🛠️ **Debug output** using `--debug`
- 🔄 **Memory reset command** for the bot owner

---

## ⚙️ Requirements

- Python 3.8+
- A running [G4F](https://github.com/xtekky/gpt4free)  API on port 1337 or [Ollama](https://ollama.com/) API on port 1337
- Discord bot token

---

## 🧪 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ImAnonFR/LLM4ALL
   cd LLM4ALL
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy `env.example` in `.env` file  with your bot credentials:
   ```
   DISCORD_TOKEN=your_discord_bot_token
   DISCORD_OWNER_ID=your_discord_user_id
   ```

---

## 🚀 Usage

### Start the bot:

##### 1st Step :

Start G4F API on port 1337 : (Use screen or another terminal because G4F need to run everytime)

```python
python -m g4f
```

##### 2nd Step :

Start the Discord BOT : 

```python
python discord-llm4all.py
```




### Commands

#### `!chat <prompt>`
Chat with the model using natural language.

- Supports image input (attach image).
- Supports `--debug` flag to print raw JSON.

#### `!generate <prompt>`
Generate an image from a text prompt.

- Supports `--debug` flag to print raw JSON.

#### `!resetmemory`
Clears the conversation history for a user (owner-only).

---

## 🧠 Memory

The bot keeps a per-user history (last 5 messages) to simulate memory and context in conversations. Memory is resettable using the `!resetmemory` command.

---

## 🧩 Configuration

Edit the following variables in `bot.py` to match your setup:

```python
G4F_URL = "http://localhost:1337/v1/chat/completions"
G4F_URL_IMAGE = "http://localhost:1337/v1/images/generate"
DEFAULT_MODEL = "llava:34b"
```

You can change `DEFAULT_MODEL` to any model supported by G4F/or your Ollama  (e.g., `qwen-vl`, `qwen2.5:14b`, etc.).

---

## 🔐 Notes

- Your bot token and user ID are read from environment variables.
- The bot uses `httpx` for async HTTP requests.
- Image data is sent in base64 format to the backend.

---

## Contact

- Discord : imanonfr
- Telegram : @deleteduser864


Don't hesitate to make feedback or merge request for improve. This is a base.