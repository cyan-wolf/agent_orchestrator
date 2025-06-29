from dotenv import load_dotenv
load_dotenv()

import os
from datetime import datetime

import requests
import json
import base64

from PIL import Image
from io import BytesIO

import colorama
colorama.init()

SERVER_ROUTE = os.environ["DEV_SERVER_ROUTE"]

def prompt_agent(user_input: str) -> dict:
    resp = requests.post(f"{SERVER_ROUTE}/api/send-message", json={
        "user_message": user_input
    })
    return resp.json()


def user_prompt_loop():
    latest_timestamp: float = 0

    try: 
        history = get_message_history()
        if len(history) > 0:
            latest_timestamp = history[-1]["timestamp"]
            pretty_print_messages(history)

    except Exception as ex:
        print(f"error: {ex}")

    while True:
        try:
            user_input = input("user> ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            _ = prompt_agent(user_input)

            latest_messages = get_latest_messages(latest_timestamp)
            latest_timestamp = latest_messages[-1]["timestamp"]

            pretty_print_messages(latest_messages)

            write_history()

        except Exception as ex:
            print(f"error: {ex}")
            break


def get_latest_messages(latest_timestamp: float) -> list:
    return requests.get(f"{SERVER_ROUTE}/api/get-latest-messages/{latest_timestamp}").json()


def pretty_print_messages(messages: list[dict]): 
    pretty_message = ""

    for message in messages:
        if message["kind"] == "ai_message":
            pretty_message = f"AI ({message["agent_name"]})> {message["content"]}"

            if not message["is_main_agent"]:
                pretty_message = f"{colorama.Fore.LIGHTBLACK_EX}{pretty_message}{colorama.Fore.RESET}"

        elif message["kind"] == "human_message":
            pretty_message = f"user ({message['username']})> {message['content']}"

        elif message["kind"] == "side_effect" and message["side_effect_kind"] == "image_generation":
            base64_encoded_image = message["base64_encoded_image"]
            show_base64_encoded_image(base64_encoded_image)

            # Do not show this message as text (as it's too long)
            continue

        else:
            pretty_message = f"{colorama.Fore.LIGHTBLACK_EX}{message}{colorama.Fore.RESET}"

        timestamp_date = datetime.fromtimestamp(message["timestamp"])
        print(f"[{colorama.Fore.YELLOW}{timestamp_date}{colorama.Fore.RESET}] {pretty_message}\n")



def get_message_history() -> list[dict]:
    return requests.get(f"{SERVER_ROUTE}/api/history").json()


def write_history():
    history_json = get_message_history()
    
    with open("hist.json", "w") as f:
        f.write(json.dumps(history_json, indent=4))


def show_base64_encoded_image(image_base64: str):
    decoded = base64.b64decode(image_base64)

    byte_stream = BytesIO(decoded)
    image = Image.open(byte_stream)

    image.show()


def main():
    user_prompt_loop()


if __name__ == "__main__":
    main()

