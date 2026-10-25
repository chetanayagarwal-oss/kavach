"""Kavach demo UI (Gradio). Run: python app.py  → open http://127.0.0.1:7860"""

import gradio as gr

from kavach import config
from kavach.pipeline import OllamaError, check

BADGE = {
    "scam": ("🚨 SCAM / फ़्रॉड", "#b71c1c", "#ffebee"),
    "suspicious": ("⚠️ SUSPICIOUS / संदिग्ध", "#e65100", "#fff3e0"),
    "safe": ("✅ LOOKS SAFE / सुरक्षित", "#1b5e20", "#e8f5e9"),
}

PRIMARY_ACTION = {
    "scam": {
        "en": "🚨 DO NOT PAY · NEVER SHARE OTP OR UPI PIN · CALL 1930 IMMEDIATELY",
        "hi": "🚨 भुगतान न करें · कभी भी OTP या UPI PIN न दें · तुरंत 1930 पर कॉल करें",
    },
    "suspicious": {
        "en": "⚠️ DO NOT CLICK LINKS OR CALL BACK · VERIFY DIRECTLY VIA OFFICIAL APP",
        "hi": "⚠️ लिंक पर क्लिक न करें · सीधे बैंक की आधिकारिक वेबसाइट या ऐप से जाँचें",
    },
    "safe": {
        "en": "✅ LEGITIMATE MESSAGE · NO ACTION REQUIRED · KEEP PINS CONFIDENTIAL",
        "hi": "✅ सुरक्षित संदेश · किसी कार्रवाई की आवश्यकता नहीं है · PIN हमेशा गोपनीय रखें",
    },
}


def run(image, text, language):
    if not image and not (text or "").strip():
        msg = "कृपया स्क्रीनशॉट अपलोड करें या संदेश पेस्ट करें।" if "हिन्दी" in language else "Upload a screenshot or paste a message."
        return f"<div style='color:#b71c1c;font-weight:600;'>{msg}</div>", {}

    try:
        res = check(image_path=image or None, text=(text or "").strip() or None)
    except OllamaError as e:
        return f"**Model error:** {e}\n\nIs Ollama running? Try `ollama serve`.", {}

    is_hi = "हिन्दी" in language
    verdict = res["verdict"]
    badge_text, badge_bg, card_bg = BADGE[verdict]
    action_text = PRIMARY_ACTION[verdict]["hi" if is_hi else "en"]
    risk = res["risk_score"]
    scam_type = res["scam_type"].replace("_", " ").title()

    # Advice checklist in selected language
    advice_items = res["advice"]["hi"] if is_hi else res["advice"]["en"]
    advice_html = "".join(f"<li style='margin-bottom:6px;'>{item}</li>" for item in advice_items)

    # Top red flags (pick top 2-3)
    rule_flags = res["rules"]["flags"]
    if rule_flags:
        flags_html = "".join(
            f"<li style='margin-bottom:4px;'><strong>{f['label_hi' if is_hi else 'label_en']}</strong>"
            + (f" &nbsp; <code>{f['evidence']}</code>" if f.get("evidence") else "")
            + "</li>"
            for f in rule_flags[:3]
        )
    else:
        flags_html = f"<li>{'कोई संदिग्ध नियम संकेत नहीं मिले' if is_hi else 'No deterministic rule flags triggered'}</li>"

    reasoning_text = res["model"].get("reasoning", "")
    perf = res["perf"]

    sec_action = "मुख्य निर्देश (Action)" if is_hi else "Immediate Action"
    sec_advice = "क्या करें और क्या न करें (Checklist)" if is_hi else "Safety Checklist"
    sec_flags = "पहचाने गए मुख्य खतरे (Top Red Flags)" if is_hi else "Top Red Flags Detected"
    sec_why = "मॉडल द्वारा विश्लेषण (AI Reasoning)" if is_hi else "AI Analysis & Reasoning"

    md = f"""
<div style="padding:16px 20px;border-radius:12px;background:{badge_bg};color:white;font-size:26px;font-weight:800;letter-spacing:0.5px;box-shadow:0 4px 12px rgba(0,0,0,0.15)">
  {badge_text} &nbsp;·&nbsp; Risk {risk}/100 &nbsp;·&nbsp; {scam_type}
</div>

<div style="margin-top:14px;padding:14px 18px;border-radius:10px;background:{card_bg};border-left:6px solid {badge_bg};font-size:17px;font-weight:700;color:#212121">
  {sec_action}:<br><span style="font-size:18px;color:{badge_bg};">{action_text}</span>
</div>

<div style="margin-top:16px;">
  <h3 style="margin-bottom:8px;font-size:18px;color:#1e293b;">📌 {sec_flags}</h3>
  <ul style="padding-left:20px;font-size:15px;line-height:1.5;">
    {flags_html}
  </ul>
</div>

<div style="margin-top:14px;">
  <h3 style="margin-bottom:8px;font-size:18px;color:#1e293b;">🛡️ {sec_advice}</h3>
  <ul style="padding-left:20px;font-size:15px;line-height:1.5;">
    {advice_html}
  </ul>
</div>

<div style="margin-top:14px;padding:10px 14px;border-radius:8px;background:#f8fafc;border:1px solid #e2e8f0;">
  <div style="font-weight:600;font-size:13px;color:#64748b;margin-bottom:4px;">🔍 {sec_why}</div>
  <div style="font-size:14px;color:#334155;line-height:1.4;">{reasoning_text}</div>
</div>

<div style="margin-top:12px;font-size:12px;color:#64748b;">
  Model <code>{perf['model_name']}</code> running locally · <strong>{perf['decode_tok_s']} tok/s</strong> · {perf['total_s']}s latency · 100% offline (no internet)
</div>
"""
    return md, res


with gr.Blocks(title="Kavach — Offline Scam Checker") as demo:
    gr.Markdown(
        f"""# 🛡️ Kavach (कवच) — Offline Scam-Screenshot Checker
> **Screenshot daalo, sach jaano.** Runs 100% locally on `{config.MODEL}`. Zero cloud APIs, private & deterministic.
"""
    )
    with gr.Row():
        with gr.Column(scale=1):
            lang = gr.Radio(["English", "हिन्दी (Hindi)"], value="English", label="Language / भाषा")
            img = gr.Image(type="filepath", label="Screenshot (SMS / WhatsApp / UPI request)")
            txt = gr.Textbox(label="...or paste the message text", lines=3, placeholder="Paste SMS, WhatsApp message, or UPI request text here...")
            btn = gr.Button("🛡️ Check / जाँचें", variant="primary", size="lg")
            gr.Examples(
                examples=[
                    ["data/samples/s01.png", "", "English"],
                    ["data/samples/s03.png", "", "English"],
                    ["data/samples/s19.png", "", "English"],
                    ["data/samples/g01.png", "", "English"],
                ],
                inputs=[img, txt, lang],
                label="Quick Test Examples (including Prompt Injection Test s19)",
            )
        with gr.Column(scale=1):
            out_md = gr.Markdown(value="*Results will appear here after clicking Check.*")
            with gr.Accordion("🔧 Developer & Audit: Full Structured JSON", open=False):
                out_json = gr.JSON()

    btn.click(run, inputs=[img, txt, lang], outputs=[out_md, out_json])

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())
