import json
from typing import AsyncGenerator

import gradio as gr
import requests

API_URL = "http://localhost:8000/api/v1/chatbot/chat"
AUTH_URL = "http://localhost:8000/token"

# Global variable to store the access token
access_token = None


def login(username: str, password: str) -> str:
    global access_token
    try:
        response = requests.post(
            AUTH_URL, data={"username": username, "password": password}
        )
        response.raise_for_status()
        access_token = response.json()["access_token"]
        return "Login successful!"
    except requests.exceptions.RequestException as e:
        return f"Login failed: {str(e)}"


def _prepare_api_data(message: str, history: list, agent_type: str) -> dict:
    flattened_history = [item for sublist in history for item in sublist]
    return {
        "prompt": message,
        "history": flattened_history,
        "agent_type": agent_type,
        "metadata": {},
    }


async def _handle_api_response(response: requests.Response) -> str:
    return response.json()["response"]


async def inference(
    message: str, history: list, agent_type: str
) -> AsyncGenerator[str, None]:
    global access_token
    if not access_token:
        yield "Please log in first."
        return

    try:
        data = _prepare_api_data(message, history, agent_type)
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(API_URL, json=data, headers=headers)
        response.raise_for_status()
        yield await _handle_api_response(response)
    except requests.exceptions.RequestException as e:
        print("Request Exception:", str(e))
        if e.response is not None:
            print("Response content:", e.response.text)
        yield f"An error occurred: {str(e)}"
    except Exception as e:
        print("Exception encountered:", str(e))
        yield "An unexpected error occurred. Please try again."


with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Chatbot Application")

    with gr.Tab("Login"):
        username_input = gr.Textbox(label="Username")
        password_input = gr.Textbox(label="Password", type="password")
        login_button = gr.Button("Login")
        login_output = gr.Textbox(label="Login Status")

        login_button.click(
            login, inputs=[username_input, password_input], outputs=login_output
        )

    with gr.Tab("Chat"):
        agent_type = gr.Dropdown(
            ["multi_step", "prompt_optim"], label="Agent Type", value="multi_step"
        )

        chatbot = gr.ChatInterface(
            inference,
            chatbot=gr.Chatbot(height=400),
            textbox=gr.Textbox(
                placeholder="Enter your message here...", container=False
            ),
            title="Chatbot Interface",
            description="Chat with our AI assistant",
            theme="soft",
            examples=[
                ["What is machine learning?"],
                ["Explain the concept of neural networks."],
            ],
            retry_btn="Retry",
            undo_btn="Undo",
            clear_btn="Clear",
            additional_inputs=[agent_type],
        )

demo.launch()
