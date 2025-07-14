import discord
import httpx
from io import BytesIO
import aiohttp
import base64
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN") # For connect to Discord BOT
OWNER_ID = os.getenv("DISCORD_OWNER_ID") # For !resetmemory command
# === CONFIGURATION ===
G4F_API = "http://localhost:1337/v1/chat/completions"
G4F_API_IMAGE = "http://localhost:1337/v1/images/generate"
DEFAULT_MODEL = "llava:34b"  # ou qwen-vl, qwen2.5:14b, etc.

# === INTENTS & CLIENT ===
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

# === USER MEMORY ===
user_history = {}
user_models = {}

# === QUERY G4F FUNCTION ===
async def query_g4f(prompt, model, image_b64=None):
    prompt = [{"role": "user", "content": prompt}]
    payload = {"model": "", "messages": prompt, "timeout": 60}
    if image_b64:
        payload["image"] = "data:image/jpeg;base64,"+str(image_b64)
    try:
        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(G4F_API, json=payload)
            print(f"Request send status code: {response.status_code}")
            print(f"Payload : {response.text}")
            if response.status_code == 200:
                return response.json()
            else:
                return f"G4F Error : {response.status_code}"
    except Exception as e:
        return f"Connection error to G4F : {e}"

# === SPLIT BIG ANSWER FUNCTION ===
def split_message(text, max_length=1800):
    parts = []
    while len(text) > max_length:
        split_index = text.rfind('\n', 0, max_length)
        if split_index == -1:
            split_index = text.rfind('. ', 0, max_length) + 1
        if split_index <= 0:
            split_index = max_length
        parts.append(text[:split_index].strip())
        text = text[split_index:].strip()
    if text:
        parts.append(text)
    return parts

# === IMAGE GENERATION FUNCTION ===
async def generate_image(prompt):
    payload = {
        "model": "flux",
        "prompt": prompt
    }
    try:
        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(G4F_API_IMAGE, json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                return f"G4F Error : {response.status_code}"
    except Exception as e:
        return f"Connection error to G4F : {e}"

# === DISCORD BOT EVENT ===
@client.event
async def on_ready():
    print(f"✅ Connecté en tant que {client.user}")
    activity = discord.Game(name="Ready to interact !")
    await client.change_presence(status=discord.Status.online, activity=activity)

# === PRINCIPAL FUNCTION ===
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    user_id = str(message.author.id)

    # === User Memory Reset command ===
    if message.content.startswith("!resetmemory"): 
        if message.author.id == int(OWNER_ID):
            user_history.pop(user_id, None)
            await message.channel.send("🧠 User memory reset.")
            return
        else:
            await message.channel.send("❌ You don't have the permission to use this command !")
            return

    # === Chat Generation command ===
    if message.content.startswith("!chat "):
        prompt = message.content[len("!chat "):].strip()
        debug = False
        if '--debug' in prompt:
            prompt = prompt.replace('--debug', '').strip()
            debug = True

        image_b64 = None
        if message.attachments:
            try:
                image_bytes = await message.attachments[0].read()
                image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            except:
                await message.channel.send("❌ Unable to read image !")

        model = DEFAULT_MODEL

        history = user_history.get(user_id, [])
        history.append(f"User: {prompt}")
        prompt_with_history = "\n".join(history[-5:]) + "\nAssistant:"

        async with message.channel.typing():
            await client.change_presence(activity=discord.Game(name=f"Responds to {message.author.name}"))
            response = await query_g4f(prompt_with_history, model, image_b64)

            answer = response.get("choices", [{}])[0].get("message", {}).get("content", "No content.")
            if debug :
                await message.channel.send(f"Raw Message : \n```json\n{response}\n```")
                return


        history.append(f"Bot: {answer}")
        user_history[user_id] = history

        chunks = split_message(answer)
        for chunk in chunks:
            await message.channel.send(chunk)

        await client.change_presence(activity=discord.Game(name="Ready to interact !"))

    # === Generate Image command ===
    if message.content.startswith("!generate "):
        prompt = message.content[len("!generate "):].strip()
        debug = False
        if '--debug' in prompt:
            prompt = prompt.replace('--debug', '').strip()
            debug = True
        async with message.channel.typing():
            await client.change_presence(activity=discord.Game(name=f"Generating image for {message.author.name}"))

            response = await generate_image(prompt)
            image_url = response['data'][0]['url']

            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    if resp.status != 200:
                        await message.channel.send("Unable to download image")
                        return
                    image_data = await resp.read()
            if debug:
                await message.channel.send(f"Raw Message : \n```json\n{response}\n```")
                return
            image_file = BytesIO(image_data)
            image_file.seek(0)

            await message.channel.send(file=discord.File(fp=image_file, filename="image.png"))

        await client.change_presence(activity=discord.Game(name="Ready to interact !"))

# === CLIENT DISCORD RUN ===
client.run(DISCORD_TOKEN)
