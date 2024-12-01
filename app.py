import gradio as gr
import playai_gradio

gr.load(
    name='PlayDialog',
    src=playai_gradio.registry,
).launch()
