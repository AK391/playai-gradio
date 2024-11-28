import gradio as gr
import pyht_gradio

gr.load(
    name='Play3.0-mini-http',
    src=pyht_gradio.registry,
).launch()
