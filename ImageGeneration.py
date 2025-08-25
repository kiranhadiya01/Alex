import asyncio
from random import randint
from PIL import Image
import requests
import os
from time import sleep


# ------------------------------
# Hugging Face Stable Diffusion API
# ------------------------------
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": "Bearer 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"}  # your token


# ------------------------------
# Async query to Hugging Face
# ------------------------------
async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        print("Error from API:", response.text[:200])
    return response.content


# ------------------------------
# Async image generation
# ------------------------------
async def generate_images(prompt: str):
    tasks = []

    # Create 4 image generation tasks
    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=2K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}",
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    # Wait for all tasks
    image_bytes_list = await asyncio.gather(*tasks)

    # Ensure output folder exists
    os.makedirs("Data", exist_ok=True)

    # Save images
    for i, image_bytes in enumerate(image_bytes_list):
        if not image_bytes:
            continue
        filename = os.path.join("Data", f"{prompt.replace(' ', '_')}_{i+1}.jpg")
        with open(filename, "wb") as f:
            f.write(image_bytes)
        print(f"Saved: {filename} ({len(image_bytes)} bytes)")


# ------------------------------
# Open generated images
# ------------------------------
def open_images(prompt):
    folder_path = "Data"
    files = [f for f in os.listdir(folder_path) if f.startswith(prompt.replace(" ", "_")) and f.endswith(".jpg")]

    for jpg_file in files:
        image_path = os.path.join(folder_path, jpg_file)
        try:
            img = Image.open(image_path)
            img.show()
            sleep(1)
        except IOError:
            print(f"Unable to open {image_path}")


# ------------------------------
# Wrapper function
# ------------------------------
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)


# ------------------------------
# Main loop (watch for file trigger)
# ------------------------------
FILE_PATH = r"C:\Users\Kiran\AppData\Local\Programs\Alex\Frontend\Files\ImageGeneration.data"

while True:
    try:
        # Read file
        with open(FILE_PATH, "r") as f:
            Data = f.read().strip()

        if not Data:
            sleep(1)
            continue

        # Split Prompt and Status
        try:
            Prompt, Status = Data.split(",")
            Prompt = Prompt.strip()
            Status = Status.strip()
        except ValueError:
            sleep(1)
            continue

        # If status is True → generate images
        if Status == "True":
            print(f"Generating images for prompt: {Prompt}")
            GenerateImages(Prompt)

            # Reset file
            with open(FILE_PATH, "w") as f:
                f.write("False,False")

            break  # exit after one run
        else:
            sleep(1)

    except Exception as e:
        print("Error:", e)
        sleep(1)
