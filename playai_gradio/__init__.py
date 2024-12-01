import gradio as gr
import requests
import os
import json

__version__ = "0.0.1"

# Move VOICES dictionary to module level
VOICES = {
    "Angelo": {"id": "s3://voice-cloning-zero-shot/baf1ef41-36b6-428c-9bdf-50ba54682bd8/original/manifest.json", "accent": "US", "gender": "M", "age": "Young", "style": "Conversational"},
    "Arsenio": {"id": "s3://voice-cloning-zero-shot/65977f5e-a22a-4b36-861b-ecede19bdd65/original/manifest.json", "accent": "US African American", "gender": "M", "age": "Middle", "style": "Conversational"},
    "Cillian": {"id": "s3://voice-cloning-zero-shot/1591b954-8760-41a9-bc58-9176a68c5726/original/manifest.json", "accent": "Irish", "gender": "M", "age": "Middle", "style": "Conversational"},
    "Timo": {"id": "s3://voice-cloning-zero-shot/677a4ae3-252f-476e-85ce-eeed68e85951/original/manifest.json", "accent": "US", "gender": "M", "age": "Middle", "style": "Conversational"},
    "Dexter": {"id": "s3://voice-cloning-zero-shot/b27bc13e-996f-4841-b584-4d35801aea98/original/manifest.json", "accent": "US", "gender": "M", "age": "Middle", "style": "Conversational"},
    "Miles": {"id": "s3://voice-cloning-zero-shot/29dd9a52-bd32-4a6e-bff1-bbb98dcc286a/original/manifest.json", "accent": "US African American", "gender": "M", "age": "Young", "style": "Conversational"},
    "Briggs": {"id": "s3://voice-cloning-zero-shot/71cdb799-1e03-41c6-8a05-f7cd55134b0b/original/manifest.json", "accent": "US Southern (Oklahoma)", "gender": "M", "age": "Old", "style": "Conversational"},
    "Deedee": {"id": "s3://voice-cloning-zero-shot/e040bd1b-f190-4bdb-83f0-75ef85b18f84/original/manifest.json", "accent": "US African American", "gender": "F", "age": "Middle", "style": "Conversational"},
    "Nia": {"id": "s3://voice-cloning-zero-shot/831bd330-85c6-4333-b2b4-10c476ea3491/original/manifest.json", "accent": "US", "gender": "F", "age": "Young", "style": "Conversational"},
    "Inara": {"id": "s3://voice-cloning-zero-shot/adb83b67-8d75-48ff-ad4d-a0840d231ef1/original/manifest.json", "accent": "US African American", "gender": "F", "age": "Middle", "style": "Conversational"},
    "Constanza": {"id": "s3://voice-cloning-zero-shot/b0aca4d7-1738-4848-a80b-307ac44a7298/original/manifest.json", "accent": "US Latin American", "gender": "F", "age": "Young", "style": "Conversational"},
    "Gideon": {"id": "s3://voice-cloning-zero-shot/5a3a1168-7793-4b2c-8f90-aff2b5232131/original/manifest.json", "accent": "British", "gender": "M", "age": "Old", "style": "Narrative"},
    "Casper": {"id": "s3://voice-cloning-zero-shot/1bbc6986-fadf-4bd8-98aa-b86fed0476e9/original/manifest.json", "accent": "US", "gender": "M", "age": "Middle", "style": "Narrative"},
    "Mitch": {"id": "s3://voice-cloning-zero-shot/c14e50f2-c5e3-47d1-8c45-fa4b67803d19/original/manifest.json", "accent": "Australian", "gender": "M", "age": "Middle", "style": "Narrative"},
    "Ava": {"id": "s3://voice-cloning-zero-shot/50381567-ff7b-46d2-bfdc-a9584a85e08d/original/manifest.json", "accent": "Australian", "gender": "F", "age": "Middle", "style": "Narrative"},
}

def get_fn(voice_id: str, api_key: str, user_id: str):
    def chat_response(message, history, voice_selection, model_selection, quality="draft", text_guidance=1):
        """Modified to work with ChatInterface"""
        if not message:
            return "Please enter some text first"
        
        # Use global VOICES dictionary
        global VOICES
        selected_voice = voice_selection.split(" (")[0]
        voice_id = VOICES[selected_voice]["id"]
        
        # Play.ai API configuration
        url = "https://api.play.ai/api/v1/tts/stream"
        payload = {
            "model": model_selection,
            "text": message,
            "voice": voice_id,
            "quality": quality,
            "outputFormat": "mp3",
            "speed": 1,
            "sampleRate": 24000,
            "seed": None,
            "temperature": None,
            "voiceGuidance": None,
            "styleGuidance": None,
            "textGuidance": text_guidance,
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
    """
    api_key = token or os.environ.get("PLAYAI_API_KEY")
    user_id = os.environ.get("PLAYAI_USER_ID")
    
    if not api_key:
        raise ValueError("PLAYAI_API_KEY environment variable is not set.")
    if not user_id:
        raise ValueError("PLAYAI_USER_ID environment variable is not set.")
    
    # Create voice selection dropdown
    voice_choices = [f"{name} ({info['accent']}, {info['gender']}, {info['age']}, {info['style']})" 
                    for name, info in VOICES.items()]
    
    # Pass initial voice ID for default voice (Angelo)
    fn = get_fn(VOICES["Angelo"]["id"], api_key, user_id)
    
    interface = gr.ChatInterface(
        fn=fn,
        type="messages",
        title="Play.ai Text-to-Speech Chatbot",
        description="A chatbot that converts text to speech using Play.ai's API",
        additional_inputs=[
            gr.Dropdown(
                choices=voice_choices,
                value=voice_choices[0],
                label="Voice Selection"
            ),
            gr.Dropdown(
                choices=["PlayDialog", "Play3.0-mini"],
                value="PlayDialog",
                label="Model Selection"
            ),
            gr.Radio(
                choices=["draft", "standard", "high"],
                value="draft",
                label="Quality"
            ),
            gr.Slider(
                minimum=0,
                maximum=1,
                value=1,
                step=0.1,
                label="Text Guidance"
            )
        ],
        **kwargs
    )
    
    return interface

# Only launch if running directly
if __name__ == "__main__":
    demo = registry("PlayDialog")
    demo.launch()