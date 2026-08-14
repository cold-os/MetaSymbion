<div align="center">

[English](README.md) | [中文](README.zh.md)

# ColdCognition

### L1 · Cognition — the Cognitive Layer of the Cold Trust Protocol Stack

[![Status](https://img.shields.io/badge/Status-Pre--Alpha--Prototype-orange)](https://github.com/cold-os/ColdCognition)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Field](https://img.shields.io/badge/Field-CSS%20%7C%20HCI-6f42c1.svg)](https://github.com/cold-os)
[![arXiv](https://img.shields.io/badge/arXiv-2512.08740-brightgreen.svg)](https://arxiv.org/abs/2512.08740)
[![DOI](https://img.shields.io/badge/DOI-10.6084/m9.figshare.31696846-blueviolet.svg)](https://doi.org/10.6084/m9.figshare.31696846)

</div>

> **Layer:** L1 · Cognition — Cold Trust Protocol Stack  
> **Research Question:** How should an agent express what it believes vs. what it merely speculates — and be held to it?  
> **Method:** RAMTN recursive adversarial dialogue (construct · challenge · observe) over three belief classes (*certain / speculative / unknown*), with Prolog-based consistency verification.  
> **Status:** Pre-alpha prototype · not for production use.  
> **Related:** [ColdReasoner](https://github.com/cold-os/ColdReasoner) (L3) · [Cold Trust Protocol Stack](https://github.com/cold-os) · arXiv:2512.08740 · figshare:31696846

---

## 🧊 What It Is

ColdCognition is a *thinking-workshop* agent: it accepts a complex problem, subjects it to internal debate, verification, and distillation, and produces **structured, reusable cognitive frameworks** — not simple answers.

Its defining move is epistemic: the agent must express its state of mind in **belief triples — certain / speculative / unknown** — and *unknown* is a first-class citizen, an explicit act of epistemic humility, not a failure.

It operates on a strict **thinking–verification–execution** separation: an LLM-based brain (RAMTN) does the deep thinking, an independent Prolog-based logic engine verifies logical consistency, and a sandbox (CAGE) executes verified plans. This *generation–verification* separation is a **runtime-verification pathway** — supplementary to training-time alignment (RLHF / Constitutional AI), not a replacement or negation of them.

## 🔍 Why It Matters

- **Computational social science:** belief triples are *machine-readable epistemic states* — the debate traces (proposals, challenges, decisions) are data on how certainty is constructed and contested in human–AI discourse.
- **HCI:** the workshop is an *interactive cognitive scaffolding* interface — structured dialogue as a way to make an agent's reasoning legible to humans.
- **AI governance:** the "unknown" class forces *honest uncertainty disclosure* — a protocol for epistemic accountability.

## 🎯 Architecture

**Cognitive layer (RAMTN)** — three roles debate in rounds:

| Role | Responsibility |
|------|----------------|
| **Constructor** | Proposes propositions as certain / speculative / unknown |
| **Critic** | Challenges proposals; requests modifications |
| **Observer** | Weighs both sides; makes the final decision |

Belief output (JSON):

```json
{
  "faith": { "certain": [...], "speculative": [...], "unknown": [...] },
  "reason": { "certain": [...], "speculative": [...], "unknown": ["epistemic humility note"] }
}
```

**Logic verification layer (Prolog)** — deterministic checks, independent of the LLM:

| Check | Rule |
|-------|------|
| Internal consistency | `certain(X) ∧ unknown(X)` cannot hold simultaneously |
| Belief–behavior | all behaviors must be entailed by the certain set |
| Boundary permissions | referencing/modifying "unknown" entities is forbidden |

**Secure execution layer (CAGE)** — whitelist operations (`create_folder`, `write_file`, …), path isolation, operation logging; execution denied on verification failure.

## 🚀 Quick Start

```bash
pip install -r requirements.txt
export DASHSCOPE_API_KEY="your-key"
python main.py
```

## 🩺 Usage Example (condensed)

Topic: *Will AI surpass human intelligence?* — Round 3 debate output classifies claims into certain (e.g., current AI lacks self-awareness), speculative (e.g., human-level reasoning breadth under exponential growth), and unknown (e.g., whether consciousness requires a biological substrate); the behavior plan passes all three verification checks; CAGE executes the approved plan. Full dialogue in the repo.

## 🧪 Status & Limitations

Pre-alpha prototype: logic layer covers propositional logic only; cognitive output depends on the underlying LLM and a fixed number of debate rounds; CAGE is simulation-grade isolation; three layers integrated at API level only; no end-to-end or adversarial testing; **no empirical studies yet** — the debate traces are intended as data for computational analysis (CSS), and the belief-triple interface as a subject of legibility studies (HCI).

## 🛣️ Roadmap

1. **CSS:** computational analysis of debate-trace dynamics — how certainty is constructed and contested.
2. **HCI:** studies on whether triadic belief disclosure improves human understanding and trust calibration.
3. Complete cognitive-framework extraction and reuse mechanisms.

## 📜 AI Usage Disclosure

The implementation and documentation of this project heavily relied on AI-assisted tools. Details are as follows:

**Human Author Contributions:**
- All core ideas and system architecture of ColdCognition were independently proposed and designed by the human author.
- RAMTN (Recursive Adversarial Meta-Thinking Network), the cognitive symbiosis concept, and the "belief-behavior consistency" verification framework are original contributions of the human author.
- All key architectural decisions, component boundary definitions, and the design direction of the Logic Verification Layer were made by the human author.

**AI-Assisted Contributions:**
- Translating natural-language logical derivations into structured verification rules.
- Assisting with cross-component data format alignment and interface coordination.
- Generating sample test cases and initial documentation drafts.
- Code assistance and debugging.

**Regarding the Formal Logic Verification Layer:** The technical direction of introducing an independent formal logic checking machine for consistency verification was proposed by the human author. DeepSeek endorsed this approach and further supplemented the concrete technical architecture of the Logic Verification Layer, verification flow design, and integration method of the Prolog engine.

All AI-assisted content has been reviewed and verified by the human author. The ultimate responsibility for code quality, correctness, and security rests with the human author.

## 📄 Technology Stack & License

**LLM:** Qwen (qwen-plus) · **Logic:** lightweight Prolog engine · **Runtime:** Python 3.10+ · **License:** Apache 2.0

---

*Part of the [Cold Trust Protocol Stack](https://github.com/cold-os) — trust protocols for human–AI interaction, anchored in computational social science.*
