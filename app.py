"""Kavach demo UI (Gradio). Run: python app.py  → open http://127.0.0.1:7860"""

import gradio as gr

from kavach import config
from kavach.pipeline import OllamaError, check

BADGE = {
    "scam": ("🚨 SCAM", "#c62828"),
    "suspicious": ("⚠️ SUSPICIOUS", "#ef6c00"),
    "safe": ("✅ LOOKS SAFE", "#2e7d32"),
}


def run(image, text):
    if not image and not (text or "").strip():
        return "Upload a screenshot or paste a message.", {}
    try:
        res = check(image_path=image or None, text=(text or "").strip() or None)
    except OllamaError as e:
        return f"**Model error:** {e}\n\nIs Ollama running? Try `ollama serve`.", {}

    label, color = BADGE[res["verdict"]]
    flags = res["rules"]["flags"]
    flag_lines = "\n".join(f"- {f['label_en']} / {f['label_hi']}  \n  `{f['evidence']}`" for f in flags) or "- none"
    model_flags = "\n".join(f"- {x}" for x in res["model"]["red_flags"]) or "- none"
    perf = res["perf"]
    md = f"""<div style="padding:14px;border-radius:12px;background:{color};color:white;font-size:26px;font-weight:700">
{label} &nbsp; · &nbsp; risk {res['risk_score']}/100 &nbsp; · &nbsp; {res['scam_type'].replace('_', ' ')}
</div>

### What to do
{chr(10).join('- ' + s for s in res['advice']['en'])}

### क्या करें
{chr(10).join('- ' + s for s in res['advice']['hi'])}

### Why (model)
{res['model']['reasoning']}

{model_flags}

### Rule checker (deterministic)
{flag_lines}

<sub>Model `{perf['model_name']}` running locally · {perf['decode_tok_s']} tok/s · {perf['total_s']} s total · no internet used</sub>
"""
    return md, res


with gr.Blocks(title="Kavach") as demo:
    gr.Markdown(f"# 🛡️ Kavach — offline scam checker\nScreenshot daalo, sach jaano. Runs on `{config.MODEL}` on this laptop.")
    with gr.Row():
        with gr.Column(scale=1):
            img = gr.Image(type="filepath", label="Screenshot (SMS / WhatsApp / UPI request)")
            txt = gr.Textbox(label="...or paste the message text", lines=4)
            btn = gr.Button("Check / जाँचें", variant="primary")
            gr.Examples(examples=[["data/samples/s01.png", ""], ["data/samples/s03.png", ""], ["data/samples/g01.png", ""]],
                        inputs=[img, txt])
        with gr.Column(scale=1):
            out_md = gr.Markdown()
            with gr.Accordion("Full JSON output", open=False):
                out_json = gr.JSON()
    btn.click(run, inputs=[img, txt], outputs=[out_md, out_json])

if __name__ == "__main__":
    demo.launch()
