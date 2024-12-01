import gradio as gr
import requests
import os
import json

__version__ = "0.0.1"

# API endpoint
API_URL = "https://api.play.ai/api/v1/tts/stream"

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
    def chat_response(message, history, voice_selection, model_selection, 
                     # Common parameters
                     output_format, speed, sample_rate, seed, temperature, language,
                     # PlayDialog specific parameters
                     voice2_selection=None, turn_prefix=None, turn_prefix2=None,
                     prompt=None, prompt2=None,
                     voice_conditioning_seconds=20, voice_conditioning_seconds2=20,
                     # Play3.0-mini specific parameters
                     quality=None, voice_guidance=None, style_guidance=None, text_guidance=None):
        """Modified to work with ChatInterface with all available options"""
        if not message:
            return "Please enter some text first"
        
        # Use global VOICES dictionary
        global VOICES
        selected_voice = voice_selection.split(" (")[0]
        voice_id = VOICES[selected_voice]["id"]
        
        # Get voice2_id if provided
        voice2_id = None
        if voice2_selection and voice2_selection != "None":
            voice2_name = voice2_selection.split(" (")[0]
            voice2_id = VOICES[voice2_name]["id"]
        
        # Base payload
        payload = {
            "model": model_selection,
            "text": message,
            "voice": voice_id,
            "outputFormat": output_format,
            "speed": speed,
            "sampleRate": sample_rate,
            "seed": seed if seed != 0 else None,
            "temperature": temperature if temperature != 0 else None,
            "language": language if language != "auto" else None
        }
        
        # Add model-specific parameters
        if model_selection == "PlayDialog":
            if voice2_id:
                payload["voice2"] = voice2_id
            if turn_prefix:
                payload["turnPrefix"] = turn_prefix
            if turn_prefix2:
                payload["turnPrefix2"] = turn_prefix2
            if prompt:
                payload["prompt"] = prompt
            if prompt2:
                payload["prompt2"] = prompt2
            if voice_conditioning_seconds != 20:
                payload["voiceConditioningSeconds"] = voice_conditioning_seconds
            if voice_conditioning_seconds2 != 20:
                payload["voiceConditioningSeconds2"] = voice_conditioning_seconds2
        else:  # Play3.0-mini
            payload.update({
                "quality": quality,
                "voiceGuidance": voice_guidance if voice_guidance != 0 else None,
                "styleGuidance": style_guidance if style_guidance != 0 else None,
                "textGuidance": text_guidance if text_guidance != 0 else None
            })
        
        headers = {
            "AUTHORIZATION": api_key,
            "X-USER-ID": user_id,
            "Content-Type": "application/json"
        }

        # Generate TTS response using the global API_URL
        response = requests.post(API_URL, json=payload, headers=headers)
        
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
            # Common inputs
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
            gr.Dropdown(
                choices=["mp3", "mulaw", "raw", "wav", "ogg", "flac"],
                value="mp3",
                label="Output Format"
            ),
            gr.Slider(
                minimum=0.1,
                maximum=5.0,
                value=1.0,
                step=0.1,
                label="Speed (0.1-5.0)"
            ),
            gr.Slider(
                minimum=8000,
                maximum=48000,
                value=24000,
                step=1000,
                label="Sample Rate (8000-48000 Hz)"
            ),
            gr.Number(
                value=0,
                label="Seed (0 for random, >0 for reproducible results)"
            ),
            gr.Slider(
                minimum=0,
                maximum=2.0,
                value=0,
                step=0.1,
                label="Temperature (0-2, 0 for default)"
            ),
            gr.Dropdown(
                choices=["auto"] + [
                    "afrikaans", "albanian", "amharic", "arabic", "bengali", 
                    "bulgarian", "catalan", "croatian", "czech", "danish", "dutch", 
                    "english", "french", "galician", "german", "greek", "hebrew", 
                    "hindi", "hungarian", "indonesian", "italian", "japanese", 
                    "korean", "malay", "mandarin", "polish", "portuguese", "russian", 
                    "serbian", "spanish", "swedish", "tagalog", "thai", "turkish", 
                    "ukrainian", "urdu", "xhosa"
                ],
                value="english",
                label="Language"
            ),
            # PlayDialog specific inputs
            gr.Dropdown(
                choices=["None"] + voice_choices,
                value="None",
                label="Voice 2 Selection (for PlayDialog multi-turn dialogue)"
            ),
            gr.Textbox(
                value="",
                label="Turn Prefix (for voice 1)",
                placeholder="e.g., 'Speaker 1:'"
            ),
            gr.Textbox(
                value="",
                label="Turn Prefix 2 (for voice 2)",
                placeholder="e.g., 'Speaker 2:'"
            ),
            gr.Textbox(
                value="",
                label="Prompt (for voice 1)",
                placeholder="Optional prompt for voice 1"
            ),
            gr.Textbox(
                value="",
                label="Prompt 2 (for voice 2)",
                placeholder="Optional prompt for voice 2"
            ),
            gr.Slider(
                minimum=1,
                maximum=60,
                value=20,
                step=1,
                label="Voice Conditioning Seconds (voice 1)"
            ),
            gr.Slider(
                minimum=1,
                maximum=60,
                value=20,
                step=1,
                label="Voice Conditioning Seconds (voice 2)"
            ),
            # Play3.0-mini specific inputs
            gr.Dropdown(
                choices=["draft", "low", "medium", "high", "premium"],
                value="draft",
                label="Quality (Play3.0-mini only)"
            ),
            gr.Slider(
                minimum=0,
                maximum=6.0,
                value=0,
                step=0.1,
                label="Voice Guidance (1-6, Play3.0-mini only)"
            ),
            gr.Slider(
                minimum=0,
                maximum=30.0,
                value=0,
                step=0.1,
                label="Style Guidance (1-30, Play3.0-mini only)"
            ),
            gr.Slider(
                minimum=0,
                maximum=2.0,
                value=1.0,
                step=0.1,
                label="Text Guidance (1-2, Play3.0-mini only)"
            )
        ],
        **kwargs
    )
    
    return interface

# Only launch if running directly
if __name__ == "__main__":
    demo = registry("PlayDialog")
    demo.launch()