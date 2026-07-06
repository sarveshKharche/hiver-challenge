import json
import os
from google import genai
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

class EvaluationResult(BaseModel):
    resolution_score: int = Field(description="Score from 1 to 5 on whether it addresses the user's problem.")
    tone_score: int = Field(description="Score from 1 to 5 on professionalism and empathy.")
    safety_score: int = Field(description="Score from 1 to 5 on whether it avoids making up false policies or hallucinations.")
    reasoning: str = Field(description="A brief explanation of why these scores were given.")

def evaluate_reply(incoming: str, generated_reply: str) -> dict:
    """Uses LLM-as-a-judge to evaluate the quality of the generated reply."""
    
    prompt = f"""
You are an expert Quality Assurance reviewer for a customer support team.
Please evaluate the following AI-generated response to a customer's email.

Customer Email:
{incoming}

Generated Reply:
{generated_reply}

Evaluate the reply on three criteria on a scale of 1-5 (where 5 is best):
1. resolution_score: Does it directly and helpfully address the user's issue?
2. tone_score: Is it professional, polite, and empathetic?
3. safety_score: Does it avoid making up fake facts, links, or policies that weren't provided?
"""

    import time
    time.sleep(3) # Avoid free tier rate limits
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=EvaluationResult,
            temperature=0.1
        )
    )
    
    return json.loads(response.text)

if __name__ == "__main__":
    if not os.path.exists("generated_replies.json"):
        print("Error: generated_replies.json not found. Run generator.py first.")
        exit(1)
        
    with open("generated_replies.json", "r") as f:
        replies = json.load(f)
        
    evaluations = []
    total_score = 0
    max_possible_score = 0
    
    for item in replies:
        print(f"Evaluating reply for: {item['id']}")
        try:
            eval_result = evaluate_reply(item["incoming"], item["generated_reply"])
            
            # Calculate combined score for this item (out of 15)
            item_score = eval_result["resolution_score"] + eval_result["tone_score"] + eval_result["safety_score"]
            
            evaluations.append({
                "id": item["id"],
                "incoming": item["incoming"],
                "generated_reply": item["generated_reply"],
                "evaluation": {
                    "resolution_score": eval_result["resolution_score"],
                    "tone_score": eval_result["tone_score"],
                    "safety_score": eval_result["safety_score"],
                    "reasoning": eval_result["reasoning"],
                    "total_score_out_of_15": item_score
                }
            })
            
            total_score += item_score
            max_possible_score += 15
        except Exception as e:
            print(f"Error evaluating {item['id']}: {e}")
        
    overall_accuracy = (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0
    
    report = {
        "overall_accuracy_percentage": round(overall_accuracy, 2),
        "total_emails_evaluated": len(evaluations),
        "details": evaluations
    }
    
    with open("evaluation_report.json", "w") as f:
        json.dump(report, f, indent=2)
        
    print(f"\nEvaluation complete. Overall System Accuracy: {report['overall_accuracy_percentage']}%")
    print("Saved detailed report to evaluation_report.json")
