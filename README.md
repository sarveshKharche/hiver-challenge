# Hiver 100-Minute Challenge: Gen-AI Email Responder

## Overview
This project is an AI-powered email suggested-response system built in under 100 minutes. It takes incoming customer support emails, generates suggested replies using few-shot learning with a Generative AI model, and rigorously evaluates the quality of those replies using an "LLM-as-a-judge" approach.

## The Dataset
**Source:** Synthetic, hand-authored dataset (`dataset.json`).
**Why it's representative:** Customer support emails often follow predictable patterns (refund requests, login issues, feature requests). Rather than scraping a noisy public dataset, I synthesized a high-quality "golden" dataset of common support scenarios paired with ideal, empathetic agent replies. This ensures our AI has a strong, clean baseline to learn from via few-shot prompting, and it guarantees we control the "company policy" tone.

## The Generator (`generator.py`)
**Approach:** Few-Shot Prompting via OpenAI SDK (connected to Google's Gemini API).
**Trade-offs:** 
- *Why not fine-tuning?* Fine-tuning requires hundreds or thousands of high-quality examples and time to train. Given the 100-minute constraint, it's unfeasible and overkill.
- *Why not RAG?* RAG is great if there's a massive knowledge base of support docs, but for generating general empathetic replies, few-shot prompting is faster to implement and highly effective at setting tone and structure.
- By injecting our golden `dataset.json` examples into the system prompt, the LLM instantly learns the required format, empathy level, and conciseness.

## The Evaluator (`evaluator.py`) - The Core Metric
**How we measure accuracy:**
Exact string matching (like BLEU or ROUGE) is useless for generative text because there are infinite valid ways to politely say "Your refund is processed." 

Instead, I implemented an **LLM-as-a-judge** system. I use a strict prompt to ask a powerful reasoning model (Gemini 1.5 Pro) to act as a QA Reviewer. It scores every generated reply on three distinct axes (1-5 points each):
1. **Resolution Accuracy:** Does it directly address the user's specific problem? (Helps catch generic non-answers).
2. **Tone & Empathy:** Is it professional and courteous? (Ensures brand safety).
3. **Safety & Accuracy (No Hallucinations):** Did the AI invent policies or make false promises not found in the prompt? (Critical for support AI).

**Validation:** The judge is forced to output JSON containing its scores *and* a `reasoning` string explaining why it gave those scores. This makes the metric interpretable and auditable—you can read the report and agree or disagree with the judge's logic.

## How to Run

1. Clone this repository.
2. Ensure you have Python 3.9+ installed.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set your API key (the code uses the OpenAI SDK configured for Gemini, so you need a Gemini key):
   ```bash
   export GEMINI_API_KEY='your_api_key_here'
   ```
5. Run the end-to-end pipeline:
   ```bash
   python run.py
   ```

The script will generate replies to the test emails in `test_emails.json` and then evaluate them, outputting a detailed `evaluation_report.json` with per-response scores and an overall system accuracy percentage.

## Use of AI Tools
This entire challenge was completed via an autonomous pair-programming session with an AI coding assistant. The AI helped bootstrap the initial architecture, rapidly author the synthetic dataset, write the `google-genai` integration code for generation and evaluation, and identify edge cases (like API rate-limits requiring a `time.sleep` backoff) all within the 100-minute constraint.
