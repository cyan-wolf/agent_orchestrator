from dotenv import load_dotenv
load_dotenv()

import base64

from PIL import Image
from io import BytesIO

from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="models/gemini-2.0-flash-preview-image-generation")

def _get_image_base64(response: BaseMessage):
    image_block = next(
        block
        for block in response.content
        if isinstance(block, dict) and block.get("image_url")
    )
    return image_block["image_url"].get("url").split(",")[-1]


def generate_image(query: str):
    """
    Generates an image based on the specified query.
    """
    message = {
        "role": "user",
        "content": query,
    }

    response = llm.invoke(
        [message],
        generation_config=dict(response_modalities=["TEXT", "IMAGE"]),
    )

    image_base64 = _get_image_base64(response)
    decoded = base64.b64decode(image_base64)

    byte_stream = BytesIO(decoded)
    image = Image.open(byte_stream)

    image.show()

if __name__ == "__main__":
    generate_image(input("user> "))
