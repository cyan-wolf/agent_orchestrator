from dotenv import load_dotenv
load_dotenv()

import os

import requests

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


def main():
    user_prompt_loop()


if __name__ == "__main__":
    main()

