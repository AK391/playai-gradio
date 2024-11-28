# `pyht-gradio`

is a Python package that makes it easy for developers to create text-to-speech apps powered by PlayHT's API.

# Installation

You can install `pyht-gradio` directly using pip:

```bash
pip install pyht-gradio
```

# Basic Usage

First, save your PlayHT credentials as environment variables:

```bash
export PLAY_HT_API_KEY=<your api key>
export PLAY_HT_USER_ID=<your user id>
```

Then in a Python file, write:

```python
import gradio as gr
import pyht_gradio

gr.load(
    name='Play3.0-mini-http',
    src=pyht_gradio.registry,
).launch()
```

Run the Python file, and you should see a Gradio Interface connected to PlayHT's text-to-speech service!

# Customization 

You can customize the interface by setting your own title, description, and examples:

```python
import gradio as gr
import pyht_gradio

gr.load(
    name='Play3.0-mini-http',
    src=pyht_gradio.registry,
    title='PlayHT-Gradio Integration',
    description="Convert text to speech using PlayHT's models.",
    examples=["Hello world!", "The quick brown fox jumps over the lazy dog."]
).launch()
```

# Supported Voice Engines

The following PlayHT voice engines are supported:

- `Play3.0-mini-http`: Latest multilingual model, streaming over HTTP (default)
- `Play3.0-mini-ws`: Latest multilingual model, streaming over WebSockets
- `Play3.0-mini-grpc`: Latest multilingual model, streaming over gRPC (for Play On-Prem)
- `PlayHT2.0-turbo`: Legacy English-only model, streaming over gRPC

# Authentication

If you are getting authentication errors, you can also set your credentials directly in your Python code:

```python
import os

os.environ["PLAY_HT_API_KEY"] = "your-api-key"
os.environ["PLAY_HT_USER_ID"] = "your-user-id"
```