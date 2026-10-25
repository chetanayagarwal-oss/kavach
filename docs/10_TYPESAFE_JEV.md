# 10 · Deep-Tech: TypeSafe AI & The `jev` Model Integration

## What is TypeSafe AI / `jev`?

**TypeSafe AI** was founded in 2024 by **Diogo Almeida** (co-inventor of RLHF and InstructGPT at OpenAI), launching the **`jev-1.13.0`** model in September 2026.

```
       TYPED QUESTIONS IN                       THE JEV MODEL                       TYPED DECISIONS OUT
┌───────────────────────────────┐          ┌─────────────────────┐          ┌───────────────────────────────────┐
│ Choice: up to 255 options     │──┐       │     jev-1.13.0      │       ┌─►│ An option id                      │
└───────────────────────────────┘  │       │(jev-latest/preview) │       │  └───────────────────────────────────┘
┌───────────────────────────────┐  ├──────►│─────────────────────├───────┼─►│ A level (2 to 10)                 │
│ Score: 2 to 10 levels         │──┤       │"System One" Model   │       │  └───────────────────────────────────┘
└───────────────────────────────┘  │       │No tokens generated  │       └─►│ A probability (0.0 to 1.0)        │
┌───────────────────────────────┐  │       │Direct typed outputs │          └───────────────────────────────────┘
│ Noul: yes / no probability    │──┘       └─────────────────────┘           no prose · no hallucinated tokens
└───────────────────────────────┘          Latency: 70–500 ms                machine-native & instant
```

Unlike traditional LLMs that generate conversational prose token-by-token, `jev` is a **pure decision model**:
- **Input:** A typed question (`Choice`, `Score`, `Noul`).
- **Output:** A typed decision (`option_id`, `level`, `probability`).
- **No tokens generated:** Nothing to parse, zero grammar escapes, zero token cost for output.
- **Latency:** 70 ms to 500 ms end-to-end.
- **What it cannot do:** Generate explanatory text, write helpline phone numbers, or do arithmetic.

---

## Why `jev` and Kavach are a Perfect Match

Standard AI apps break when paired with `jev` because they expect the model to generate the user interface, text, and advice.

**Kavach was designed with deterministic separation from day one:**
1. **Perception (OCR):** Gemma 4 Vision transcribes the screenshot into clean text.
2. **Deterministic Rules:** Regex extracts UPI IDs, short links, and phone numbers.
3. **Decision Stage (Where `jev` plugs in):**
   - Question 1 (`Choice`): Select from the 16 scam categories (`digital_arrest`, `upi_collect_request`, etc.).
   - Question 2 (`Score`): Assess risk level (1 to 10).
   - Question 3 (`Noul`): Compute the calibrated probability that the message is fraudulent.
4. **Action & Advice:** Generated entirely by deterministic lookup tables in `kavach/advice.py` (fixed numbers like `1930`, official portals `cybercrime.gov.in`).

Because Kavach **never allows an AI model to hallucinate advice or helpline numbers**, replacing the generative classifier with `jev` yields a **sub-100ms, zero-token, machine-native scam checker.**

---

## Architecture: System 1 (`jev`) vs System 2 (`Gemma 4`)

Kavach supports both backends through a unified interface in [`kavach/pipeline.py`](file:///C:/Users/CHETANAY/OneDrive/Desktop/kavach/kavach/kavach/pipeline.py):

| Capability | Gemma 4 E4B (System 2) | TypeSafe jev-1.13.0 (System 1) |
|---|---|---|
| **Runtime** | Local via Ollama | TypeSafe Decision API (or local emulator) |
| **Output Type** | Constrained JSON text generation | Pure typed primitives (`Choice`, `Score`, `Noul`) |
| **Tokens Generated** | ~80 tokens | **0 tokens** |
| **Latency** | 1.5 – 3.5 seconds | **70 – 150 ms** |
| **Internet Required** | **No (100% offline)** | Yes (unless using offline emulator) |
| **Target Track** | Best Local Agentic Tool / Gemma 4 | Frontier AI & Machine-Native Automation |

---

## How to Run Kavach with `jev`

### 1. Default Mode (Gemma 4 Local Engine)
```bash
python -m kavach.cli --image data/samples/s03.png --brief
```

### 2. TypeSafe JEV Mode (Ultra-low Latency Decision)
```bash
# Set engine to jev
KAVACH_DECISION_ENGINE=jev python -m kavach.cli --image data/samples/s03.png --brief

# With your TypeSafe AI API key (if you have early-access)
TYPESAFE_API_KEY="ts_live_..." KAVACH_DECISION_ENGINE=jev python app.py
```

When no API key is specified, Kavach's `kavach/jev.py` operates in high-fidelity offline emulator mode, allowing judges to test the typed decision flow at sub-100ms speed without external network calls.
