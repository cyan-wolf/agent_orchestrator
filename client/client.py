from dotenv import load_dotenv
load_dotenv()

import os

import requests

import base64

from PIL import Image
from io import BytesIO

SERVER_ROUTE = os.environ["DEV_SERVER_ROUTE"]

def prompt_agent(user_input: str) -> dict:
    resp = requests.post(SERVER_ROUTE, json={
        "user_message": user_input
    })
    return resp.json()


def user_prompt_loop():
    while True:
        try:
            user_input = input("user> ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            response = prompt_agent(user_input)
            message = response['message']
            print(f"AI> {message}")

        except Exception as ex:
            print(f"error: {ex}")
            break


def get_history():
    history_json = requests.get(f"{SERVER_ROUTE}/history").json()
    print(history_json)


def show_base64_encoded_image(image_base64: str):
    decoded = base64.b64decode(image_base64)

    byte_stream = BytesIO(decoded)
    image = Image.open(byte_stream)

    image.show()


def main():
    user_prompt_loop()


if __name__ == "__main__":
    main()

