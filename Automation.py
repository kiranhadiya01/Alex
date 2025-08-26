# This is for task execution in the backend 

# Import required libraries
from AppOpener import close, open as appopen   # Import functions to open and close apps
from webbrowser import open as webopen         # Import web browser functionality
from pywhatkit import search, playonyt         # Import functions for Google search and YouTube playback
from dotenv import dotenv_values               # This loads environment variables from your .env file            
from bs4 import BeautifulSoup                   # Import BeautifulSoup for parsing HTML content
from rich import print                          # Import rich for styled console output
from groq import Groq                           # Import Groq for AI chat functionalities
import webbrowser                               # Import webbrowser for opening URLs
import subprocess                               # Import subprocess for interacting with the system
import requests                                 # Import requests for making HTTP requests
import keyboard                                 # Import keyboard for keyboard-related actions
import asyncio                                  # Import asyncio for asynchronous programming
import os                                       # Import os for operating system functionalities
import time                                     # For waiting before pressing Enter
import json                                     # For loading contacts
from urllib.parse import quote_plus             # For encoding WhatsApp messages

# ---------------- Browser Setup (Force Brave/Chrome) ---------------- #
# Change this path if needed (Chrome path usually: C:\Program Files\Google\Chrome\Application\chrome.exe)
BRAVE_PATH = r"c:\Users\Kiran\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe"
webbrowser.register('brave', None, webbrowser.BackgroundBrowser(BRAVE_PATH))

# ---------------- WhatsApp Web Constants ---------------- #
WHATSAPP_WEB_HOME = "https://web.whatsapp.com/"
CONTACTS_FILE = "Data/contacts.json"

# Load environment variables from the .env file
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")  # Retrieve the Groq API key

# Define CSS classes for parsing specific elements in HTML content.
classes = [
    "zCubwf", "hgKElc", "LTKOO sY7ric", "Z0LcW", "gsrt vk_bk FzvWSb_YwPhnf",
    "pclqee", "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "O5uR6d LTKOO",
    "VLzY6d", "webanswers-webanswers_table__webanswers-table",
    "dDoNo ikb4Bb gsrt", "sXLaOe", "LWkfKe", "VQF4g", "qv3Wpe",
    "kno-rdesc", "SPZz6b"
]

# Define a user-agent for making web requests.
useragent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"
)

# Initialize the Groq client with the API key.
client = Groq(api_key=GroqAPIKey)  # Ensure the correct API key is assigned

# Predefined professional responses for user interactions.
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask."
]

# List to store chatbot messages.
messages = []

# System message to provide context to the chatbot.
SystemChatBot = [{
    "role": "system",
    "content": f"Hello, I am {os.environ.get('Username','User')}, You're a content writer. "
               "You have to write content like letters, blogs, and articles."
}]

# ---------------- WhatsApp Functions ---------------- #

def _lookup_contact_number(name_or_number: str) -> str | None:
    """Look up contact by name or return number if already numeric."""
    if os.path.exists(CONTACTS_FILE):
        try:
            with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
                contacts = json.load(f)
            return contacts.get(name_or_number, name_or_number)
        except Exception as e:
            print(f"[red]Error reading contacts file:[/red] {e}")
    return name_or_number if name_or_number.isdigit() else None

def open_whatsapp_home() -> bool:
    """Open WhatsApp Web home in Brave."""
    webbrowser.get('brave').open(WHATSAPP_WEB_HOME)
    return True

def send_whatsapp_via_web(name_or_number: str, message: str) -> bool:
    """
    Open WhatsApp Web to a specific chat in Brave and prefill message, then send with Enter.
    """
    number = _lookup_contact_number(name_or_number)
    if not number:
        print(f"[red]Contact not found:[/red] {name_or_number}")
        return False

    encoded = quote_plus(message)
    url = f"https://web.whatsapp.com/send?phone={number}&text={encoded}"

    webbrowser.get('brave').open(url)

    time.sleep(6)  # wait for page to load
    try:
        keyboard.press_and_release("enter")
        print(f"[green]WhatsApp message sent to {number}[/green]: {message}")
        return True
    except Exception as e:
        print(f"[red]Failed to press Enter to send message[/red]: {e}")
        return False

# ---------------- Other Functions ---------------- #

def GoogleSearch(Topic):
    url = f"https://www.google.com/search?q={quote_plus(Topic)}"
    webbrowser.get('brave').open(url)
    return True

def Content(Topic):
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor, File])

    messages = []
    SystemChatBot = [{"role": "system", "content": "You are a helpful assistant."}]

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )
        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    Topic = Topic.replace("Content ", "")
    ContentByAI = ContentWriterAI(Topic)
    os.makedirs("Data", exist_ok=True)
    with open(rf"Data\{Topic.lower().replace(' ', '')}.txt", "w", encoding="utf-8") as file:
        file.write(ContentByAI)
    OpenNotepad(rf"Data\{Topic.lower().replace(' ', '')}.txt")
    return True

def YouTubeSearch(topic: str):
    url = f"https://www.youtube.com/results?search_query={quote_plus(topic)}"
    webbrowser.get('brave').open(url)
    return True

def PlayYoutube(query):
    playonyt(query, open_video=True)  # uses default browser internally
    return True

def OpenApp(app, sess=requests.session()):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        def extract_links(html):            
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [link.get('href') for link in links]
        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": useragent}
            response = sess.get(url, headers=headers)
            if response.status_code == 200:
                return response.text
            else:
                print("Failed to retrieve search results.")
                return None
        html = search_google(app)
        if html:
            link = extract_links(html)[0]
            webbrowser.get('brave').open(link)
    return True

def CloseApp(app):
    if "chrome" in app:
        pass
    else: 
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except:
            return False

def System(command):  
    def mute(): keyboard.press_and_release("volume mute")
    def unmute(): keyboard.press_and_release("volume mute")
    def volume_up(): keyboard.press_and_release("volume up")
    def volume_down(): keyboard.press_and_release("volume down")

    if command == "mute": mute()
    elif command == "unmute": unmute()
    elif command == "volume up": volume_up()
    elif command == "volume down": volume_down()
    return True

# ---------------- Command Translation ---------------- #

async def TranslateAndExecute(commands: list[str]):
    funcs = []
    for command in commands:
        if command.startswith("open whatsapp send "):
            parts = command.replace("open whatsapp send ", "").split(":", 1)
            if len(parts) == 2:
                name, msg = parts
                fun = asyncio.to_thread(send_whatsapp_via_web, name.strip(), msg.strip())
                funcs.append(fun)
        elif command.startswith("open whatsapp"):
            fun = asyncio.to_thread(open_whatsapp_home)
            funcs.append(fun)
        elif command.startswith("open "):
            fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
            funcs.append(fun)
        elif command.startswith("close"):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close"))
            funcs.append(fun)
        elif command.startswith("play"):
            fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play"))
            funcs.append(fun)
        elif command.startswith("content "):
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)
        elif command.startswith("google search "):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)
        elif command.startswith("youtube search "):
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)
        elif command.startswith("system "):
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)
        else:
            print(f"No Function Found for {command}")
    results = await asyncio.gather(*funcs)
    for result in results:
        yield result

async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True

# ---------------- Example ---------------- #
if __name__ == "__main__":
    # Example: send WhatsApp message
    #asyncio.run(Automation(["open whatsapp send Hito: Hello Hito, how are you?"]))
    
    # Example: Google search
    # asyncio.run(Automation(["google search OpenAI GPT-5"]))
    
    # Example: Content writing
    # asyncio.run(Automation(["content Application for leave"]))
    pass
