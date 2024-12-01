# `playai-gradio`

is a Python package that makes it easy for developers to create text-to-speech apps powered by PlayAI's API.

# Installation

You can install `playai-gradio` directly using pip:

```bash
pip install playai-gradio
```

# Basic Usage

First, save your Play.ai credentials as environment variables:

```bash
export PLAYAI_API_KEY=<your api key>
export PLAYAI_USER_ID=<your user id>
```

Then in a Python file, write:

```python
import gradio as gr
import playai_gradio

gr.load(
    name='PlayDialog',
    src=playai_gradio.registry,
).launch()
```

Run the Python file, and you should see a Gradio Interface connected to Play.ai's text-to-speech service!

# Customization 

You can customize the interface by setting your own title, description, and examples:

```python
import gradio as gr
import playai_gradio

gr.load(
    name='PlayDialog',
    src=playai_gradio.registry,
    title='Play.ai-Gradio Integration',
    description="Convert text to speech using Play.ai's models.",
    examples=["Hello world!", "The quick brown fox jumps over the lazy dog."]
).launch()
```

# Supported Models and Features

The following Play.ai models are supported:

- `PlayDialog`: For multi-turn dialogue with two voices
- `Play3.0-mini`: For single-voice text-to-speech

Available voices include Angelo, Arsenio, Cillian, Timo, and many others, each with specific accent, gender, age, and style characteristics.

Key features include:
- Voice selection with detailed characteristics
- Multiple output formats (mp3, wav, ogg, etc.)
- Speed and sample rate adjustment
- Temperature and seed control
- Multi-language support
- Model-specific parameters for fine-tuning

# Authentication

If you are getting authentication errors, you can also set your credentials directly in your Python code:

```python
import os

os.environ["PLAYAI_API_KEY"] = "your-api-key"
os.environ["PLAYAI_USER_ID"] = "your-user-id"
```