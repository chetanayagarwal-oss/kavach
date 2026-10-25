# 08 · Submission checklist

Tick everything before 5:00 PM. Submit to **every track you qualify for** — one project can win more than one.

## Common (all tracks)

- [ ] Public GitHub repo, pushed, tagged `v1.0`
- [ ] `LICENSE` file present (MIT) ✅ already in repo
- [ ] README: problem, demo screenshot/GIF, quick start, team names
- [ ] Every team member registered individually on MLH and checked in
- [ ] Project submitted on MLH OrganizerHQ Challenges before the deadline
- [ ] Backup demo video (60 s) recorded

## Best Local Agentic Tool ⭐ main target

- [ ] **Local inference only** — no OpenAI/Anthropic/Gemini API anywhere in the final code (`grep -ri "api_key" .` should find nothing)
- [ ] Open-weight model: Gemma 4 (Apache 2.0)
- [ ] **One clearly defined task**: "classify a message screenshot as scam / suspicious / safe with advice" (say this exact sentence in README + pitch)
- [ ] README states **model name** (`gemma4:e4b`), **parameter count** (~4.5B effective), **minimum hardware tested** (your laptop specs)
- [ ] **3 repeated runs** shown: `results/EVAL_REPORT.md` table pasted in README
- [ ] Task success rate + reliability (consistency %) + tok/s all visible
- [ ] Non-generative external tools only (we use none; regex is local)

## Best Use of Gemma 4

- [ ] Gemma 4 is the core model (both OCR and judgement)
- [ ] Multimodal: image input demonstrated live
- [ ] Focused tool for the community (fraud protection, Hindi output)
- [ ] Mention why Gemma: vision + structured output on a small open model that runs on a laptop

## Best Open-Source AI Project (DigitalOcean)

- [ ] Open-weight AI is central ✅
- [ ] Agent Skill included: `skills/kavach-scam-check/SKILL.md`
- [ ] Clear CONTRIBUTING hint in README ("add a rule in rules.py, add samples in labels.csv")
- [ ] Optional: deploy the Gradio UI on a DigitalOcean GPU Droplet running the same open model (only if time — never swap in a hosted frontier API)

## Physical AI (only if you build the Pi version)

- [ ] Runs fully offline on a separate device (Pi 5), not the laptop
- [ ] Uses a camera / button / speaker meaningfully
- [ ] Working prototype shown live
- [ ] Repo section documenting the Pi setup (see `09_EDGE_RASPBERRY_PI.md`)

## Final 10-minute check

- [ ] Fresh clone works: `git clone … && pip install -r requirements.txt && python data/make_samples.py && python -m kavach.cli --image data/samples/s03.png --brief`
- [ ] No secrets, no personal phone numbers in committed sample images
- [ ] README placeholders (`___`, `_fill in_`) all replaced
- [ ] Laptop charged, model warm, demo tabs open
