import os
import gradio as gr
from typing import Callable
import base64
from pyht import Client
from pyht.client import TTSOptions, Format, Language
import numpy as np
import io
from pydub import AudioSegment
from gradio_webrtc import WebRTC, ReplyOnPause

__version__ = "0.0.3"

VALID_VOICE_ENGINES = {
    'Play3.0-mini-http': 'Latest multilingual model, streaming over HTTP',
    'Play3.0-mini-ws': 'Latest multilingual model, streaming over WebSockets',
    'Play3.0-mini-grpc': 'Latest multilingual model, streaming over gRPC (for Play On-Prem)',
    'PlayHT2.0-turbo': 'Legacy English-only model, streaming over gRPC'
}

def aggregate_chunks(chunks_iterator):
    """Convert audio chunks to numpy arrays for streaming."""
    leftover = b''  # Store incomplete bytes between chunks
    
    for chunk in chunks_iterator:
        # Combine with any leftover bytes from previous chunk
        current_bytes = leftover + chunk
        
        # Calculate complete samples
        n_complete_samples = len(current_bytes) // 2  # int16 = 2 bytes
        bytes_to_process = n_complete_samples * 2
        
        # Split into complete samples and leftover
        to_process = current_bytes[:bytes_to_process]
        leftover = current_bytes[bytes_to_process:]
        
        if to_process:  # Only yield if we have complete samples
            audio_array = np.frombuffer(to_process, dtype=np.int16).reshape(1, -1)
            yield (24000, audio_array, "mono")  # Include sample rate and channel format

def audio_to_bytes(audio: tuple[int, np.ndarray]) -> bytes:
    """Convert audio tuple to bytes in MP3 format."""
    audio_buffer = io.BytesIO()
    segment = AudioSegment(
        audio[1].tobytes(),
        frame_rate=audio[0],
        sample_width=audio[1].dtype.itemsize,
        channels=1,
    )
    segment.export(audio_buffer, format="mp3")
    return audio_buffer.getvalue()

def get_fn(model_name: str, preprocess: Callable, postprocess: Callable, api_key: str, user_id: str):
    def response(audio: tuple[int, np.ndarray]):
        try:
            # Initialize PlayHT client
            client = Client(
                user_id=user_id,
                api_key=api_key
            )
            
            # Configure TTS options
            options = TTSOptions(
                voice=model_name,
                format=Format.FORMAT_WAV,
                sample_rate=24000,  # High quality audio
                speed=1.0,
                language=Language.ENGLISH
            )

            # Generate audio and stream chunks
            audio_chunks = client.tts(audio[1], options)
            yield from aggregate_chunks(audio_chunks)
            
        except Exception as e:
            print(f"Error generating audio: {str(e)}")
            return None

    return response

def get_image_base64(url: str, ext: str):
    with open(url, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return "data:image/" + ext + ";base64," + encoded_string

def handle_user_msg(message: str):
    if type(message) is str:
        return message
    elif type(message) is dict:
        if message["files"] is not None and len(message["files"]) > 0:
            ext = os.path.splitext(message["files"][-1])[1].strip(".")
            if ext.lower() in ["png", "jpg", "jpeg", "gif", "pdf"]:
                encoded_str = get_image_base64(message["files"][-1], ext)
            else:
                raise NotImplementedError(f"Not supported file type {ext}")
            content = [
                    {"type": "text", "text": message["text"]},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": encoded_str,
                        }
                    },
                ]
        else:
            content = message["text"]
        return content
    else:
        raise NotImplementedError

def get_interface_args(pipeline):
    if pipeline == "chat":
        inputs = None
        outputs = gr.Chatbot(
            bubble_full_width=False,
            show_label=False,
            height=400
        )

        def preprocess(message, history):
            return {"message": handle_user_msg(message)}

        def postprocess(text, audio):
            return text
            
    else:
        raise ValueError(f"Unsupported pipeline type: {pipeline}")
    return inputs, outputs, preprocess, postprocess

def get_pipeline(model_name):
    # Determine the pipeline type based on the model name
    # For simplicity, assuming all models are chat models at the moment
    return "chat"

def registry(name: str = 'Play3.0-mini-http', token: str | None = None, user_id: str | None = None, **kwargs):
    """
    Create a Gradio Interface for a model using PlayHT with WebRTC support.
    """
    if name not in VALID_VOICE_ENGINES:
        raise ValueError(f"Invalid voice engine: {name}. Must be one of: {', '.join(VALID_VOICE_ENGINES.keys())}")
    
    api_key = token or os.environ.get("PLAY_HT_API_KEY")
    user_id = user_id or os.environ.get("PLAY_HT_USER_ID")
    
    if not api_key or not user_id:
        raise ValueError("PLAY_HT_API_KEY and PLAY_HT_USER_ID environment variables must be set.")

    # Create the Blocks interface with WebRTC
    with gr.Blocks() as interface:
        gr.HTML("""
        <h1 style='text-align: center'>
        PlayHT Text-to-Speech (Powered by WebRTC ⚡️)
        </h1>
        """)
        
        with gr.Column():
            with gr.Group():
                audio = WebRTC(
                    label="Audio Stream",
                    mode="send-receive",
                    modality="audio",
                )
            
            # Get the response function and wrap it with ReplyOnPause
            fn = get_fn(name, None, None, api_key, user_id)
            audio.stream(
                fn=ReplyOnPause(fn),
                inputs=[audio],
                outputs=[audio],
                time_limit=60  # 1 minute time limit
            )

    return interface
