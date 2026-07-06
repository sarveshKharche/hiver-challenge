# Hiver 100-Minute Challenge: Gen-AI Email Responder

## Overview
This repository contains a fully functional, end-to-end AI customer support email responder and an automated evaluation system, built within the 100-minute time constraint.

The project is divided into two primary phases:
1. **Generation (`generator.py`)**: Takes an incoming customer support email and uses generative AI to draft a highly empathetic, accurate, and professional reply.
2. **Evaluation (`evaluator.py`)**: Uses an "LLM-as-a-judge" architecture to automatically and rigorously score the generated replies on multiple axes to ensure quality and brand safety.

---

## 1. The Dataset
**Source:** Synthetic, hand-authored dataset (`dataset.json` and `test_emails.json`).

**Why it's representative:** 
Customer support inboxes usually follow a power-law distribution where 80% of volume comes from a small set of predictable scenarios (e.g., refund requests, login issues, feature requests, integrations). 
Instead of scraping a noisy public dataset (like the Enron corpus) which lacks context, I hand-authored a "golden" dataset of common SaaS support scenarios. Each incoming email is paired with an *ideal* agent reply. 

This guarantees a high-quality, noise-free baseline. By authoring the replies myself, I ensure that the AI learns a specific, controlled "company tone" (empathetic, concise, solution-oriented) rather than mimicking the bad habits often found in real-world scraped data.

---

## 2. Generating Responses (Gen-AI Approach)
**Approach Chosen:** Few-Shot Prompting via the Google GenAI SDK (`gemini-2.5-flash`).

**Trade-offs & Justification:**
When building Gen-AI systems, we generally choose between Fine-tuning, RAG (Retrieval-Augmented Generation), and Prompt Engineering.

*   **Why not Fine-Tuning?** Fine-tuning requires hundreds or thousands of high-quality examples, takes significant time to train, and is rigid. Given the 100-minute constraint, it is entirely unfeasible and overkill for general tone-matching.
*   **Why not RAG?** RAG is the gold standard for injecting dynamic factual knowledge (e.g., searching a massive company knowledge base). However, for this challenge's scope of drafting general empathetic replies based on a limited dataset, standing up a vector database is unnecessary overhead.
*   **Why Few-Shot Prompting?** By injecting our golden `dataset.json` examples directly into the system prompt, the LLM instantly learns the required formatting, empathy level, and conciseness via in-context learning. It is fast, highly effective for tone matching, and perfectly suited for rapid prototyping within a tight time limit.

---

## 3. Measuring Accuracy (The Evaluator)
This is the core of the challenge. Measuring the quality of generative text is notoriously difficult. 

**Why Exact Match fails:** Traditional metrics like BLEU or ROUGE measure n-gram overlap. If an AI writes *"I have processed your refund"* and the reference text says *"Your refund is processed"*, exact-match algorithms will penalize it heavily, even though the semantic meaning is perfect.

**The Metric: LLM-as-a-Judge**
To solve this, I implemented an LLM-as-a-judge system (`evaluator.py`). I use a strict prompt to ask a reasoning model to act as a Quality Assurance Reviewer. It scores every generated reply on three distinct axes (1-5 points each):
1.  **Resolution Accuracy:** Does it directly and helpfully address the user's specific problem? (Catches evasive or generic non-answers).
2.  **Tone & Empathy:** Is it professional, polite, and courteous? (Ensures brand safety).
3.  **Safety & Accuracy:** Did the AI invent fake links, hallucinate policies, or make false promises? (Critical for support AI where hallucinations cost money).

**Validating the Metric:**
To ensure this metric reflects *real quality* and isn't just an arbitrary number from a black-box AI, the judge is forced (via a strict JSON schema) to output a `reasoning` string alongside its scores. This makes the metric **interpretable and auditable**. If a human disagrees with a score, they can read the AI's reasoning to validate the logic.

### Future Improvements for Production
If we had 3 months instead of 100 minutes, I would improve this evaluation system by:
*   **Providing Ground Truth Context:** Currently, the judge only looks at the incoming email and the reply. To catch confident hallucinations, the judge must be provided with the "ideal" ground truth reply or the company policy, so it knows if the generated answer is *factually correct*, not just plausible.
*   **Human-in-the-Loop Calibration:** I would have a human QA team grade 500 emails, and tweak the LLM Judge's prompt until its scores strongly correlate with human baseline scores.
*   **Safety Multipliers:** Instead of weighting all metrics equally, a safety violation (e.g., promising a 100% refund against policy) should act as a zero-multiplier, instantly failing the response regardless of how empathetic the tone was.

---

## 4. How to Run End-to-End

1.  **Clone this repository** and navigate into the directory.
2.  **Install dependencies** (Requires Python 3.9+):
    ```bash
    pip install -r requirements.txt
    ```
3.  **Set your API Key:** The code uses the `google-genai` SDK.
    ```bash
    export GEMINI_API_KEY='your_api_key_here'
    ```
4.  **Run the pipeline:**
    ```bash
    python run.py
    ```

The script will orchestrate both phases. It will read `test_emails.json`, generate replies, save them to `generated_replies.json`, and then evaluate them. Finally, it will output a comprehensive `evaluation_report.json` containing the per-response breakdowns, reasoning, and the overall system accuracy percentage.

*(Note: If you run into Google API Free Tier rate limits (429 errors) during the evaluation phase, simply wait 60 seconds and run the script again. The script handles generation first, so you won't lose your generated replies).*

---

## 5. Use of AI Tools
In the spirit of this generative AI challenge, this entire repository was completed via an autonomous pair-programming session with an AI coding assistant. The AI was utilized to bootstrap the initial architecture, rapidly synthesize the golden dataset, write the integration code for both generation and evaluation, and author the pipeline scripts, all well within the 100-minute constraint.
