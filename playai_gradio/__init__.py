import gradio as gr
import requests
import os
import json

__version__ = "0.0.1"

def get_fn(voice_id: str, api_key: str, user_id: str):
    def chat_response(message, history):
        """Modified to work with ChatInterface"""
        if not message:
            return "Please enter some text first"
        
        # Play.ai API configuration
        url = "https://api.play.ai/api/v1/tts/stream"
        payload = {
            "model": "PlayDialog",
            "text": message,
            "voice": voice_id,
            "outputFormat": "mp3",
            "speed": 1,
            "sampleRate": 24000,
            "language": "english"
        }
        
        headers = {
            "AUTHORIZATION": api_key,
            "X-USER-ID": user_id,
            "Content-Type": "application/json"
        }

        # Generate TTS response
        response = requests.post(url, json=payload, headers=headers)
        
        # Save the audio response with a unique filename
        response_path = f"response_{len(history)}.mp3"
        with open(response_path, "wb") as f:
            f.write(response.content)
        
        # Return OpenAI-style message with audio file
        return {
            "role": "assistant",
            "content": {
                "path": response_path
            }
        }
    
    return chat_response

def registry(name: str, token: str | None = None, **kwargs):
    """
    Create a Gradio Interface for Play.ai TTS.
    
    Parameters:
        - name (str): The name of the voice model
        - token (str, optional): The API key for Play.ai
    """
    api_key = token or os.environ.get("PLAYAI_API_KEY")
    user_id = os.environ.get("PLAYAI_USER_ID")
    
    if not api_key:
        raise ValueError("PLAYAI_API_KEY environment variable is not set.")
    if not user_id:
        raise ValueError("PLAYAI_USER_ID environment variable is not set.")
        
    voice_id = "s3://voice-cloning-zero-shot/baf1ef41-36b6-428c-9bdf-50ba54682bd8/original/manifest.json"
    fn = get_fn(voice_id, api_key, user_id)
    
    interface = gr.ChatInterface(
        fn=fn,
        type="messages",  # Specify OpenAI-style message format
        title="Play.ai Text-to-Speech Chatbot",
        description="A chatbot that converts text to speech using Play.ai's API",
        examples=["Hello, how are you today?"],
        **kwargs
    )
    
    return interface

# Only launch if running directly
if __name__ == "__main__":
    demo = registry("PlayDialog")
    demo.launch()