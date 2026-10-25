# 09 · Optional: Kavach on a Raspberry Pi 5 (Physical AI track)

**Only do this if** (a) someone brings a Raspberry Pi 5 with 8 GB RAM + active cooler, and (b) the laptop version is done and measured.
Otherwise, mention it as future work.

## The device idea: "Kavach Box"

A small box on a shop counter or at an elder's home:
- Pi Camera (or USB webcam) pointed at a phone screen
- One push button: press → capture → check
- Output: a green / orange / red LED + verdict spoken through a small speaker (optional) + text on screen

Fully offline. This matches the track: an AI device sensing the real world (camera) and responding (LED/speaker).

## Model and runtime

| Option | Speed on Pi 5 (8 GB), decode | Notes |
|---|---|---|
| Gemma 4 E2B via **LiteRT-LM** | ~9 tok/s, ~1.4 GB RAM (reported) | Fastest; setup takes longer |
| Gemma 4 E2B via **llama.cpp** (Q4_0) | ~4 tok/s, ~4.4 GB RAM (reported) | Simple |
| Gemma 4 E2B via **Ollama** | similar to llama.cpp | Easiest — same code as laptop |

Recommended for a 5-hour hackathon: **Ollama + E2B** so the exact same `kavach` package runs unchanged:

```bash
# on the Pi (64-bit Raspberry Pi OS)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma4:e2b          # do this before the event
pip install requests pillow --break-system-packages
git clone <your repo> && cd kavach
KAVACH_MODEL=gemma4:e2b KAVACH_NUM_CTX=2048 python -m kavach.cli --image test.png --brief
```

## Minimal button + LED script (`pi_box.py`, write on the day)

Outline (gpiozero + picamera2 are preinstalled on Raspberry Pi OS):

```python
from gpiozero import Button, LED
from picamera2 import Picamera2
from kavach.pipeline import check

button, red, orange, green = Button(17), LED(22), LED(27), LED(23)
cam = Picamera2(); cam.start()

def on_press():
    for l in (red, orange, green): l.off()
    cam.capture_file("shot.jpg")
    res = check(image_path="shot.jpg")
    {"scam": red, "suspicious": orange, "safe": green}[res["verdict"]].on()
    print(res["verdict"], res["scam_type"], res["advice"]["hi"][0])

button.when_pressed = on_press
input("Kavach Box ready. Press the button. Enter to quit.\n")
```

## Speed tricks for the Pi

- Pasted/OCR'd text path is much faster than image path; consider a tiny local OCR (e.g. Tesseract) for step 1 on the Pi and keep Gemma only for judgement.
- `KAVACH_NUM_CTX=2048`, thinking off (default).
- Keep the Pi cool (active cooler), otherwise it throttles.
- Expect tens of seconds per check on a Pi; say so honestly and show the LED result.

## What to report

Model (E2B, ~2.3B effective), device (Pi 5 8 GB), runtime, tok/s, seconds per check, and the 3-run consistency on 10 samples.
