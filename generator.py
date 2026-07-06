import json
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def generate_reply(incoming_email: str, dataset: list) -> str:
    """Generates an email reply using Few-Shot prompting."""
    
    system_prompt = (
        "You are a helpful, professional, and empathetic customer support agent. "
        "Your task is to write a reply to the incoming customer email. "
        "Here are some examples of past emails and their ideal replies. "
        "Use these to understand the tone and formatting we expect.\n\n"
    )
    
    for item in dataset:
        system_prompt += f"Example Customer Email:\n{item['incoming']}\n"
        system_prompt += f"Example Agent Reply:\n{item['reply']}\n\n"
        
    system_prompt += "Now, please write a reply to the following new customer email. Only output the reply text."

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=incoming_email,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.4
        )
    )
    
    return response.text.strip()

if __name__ == "__main__":
    print("Loading dataset and test emails...")
    with open("dataset.json", "r") as f:
        dataset = json.load(f)
    
    with open("test_emails.json", "r") as f:
        test_emails = json.load(f)
        
    results = []
    for email in test_emails:
        print(f"Generating reply for: {email['id']}")
        try:
            reply = generate_reply(email["incoming"], dataset)
            results.append({
                "id": email["id"],
                "incoming": email["incoming"],
                "generated_reply": reply
            })
        except Exception as e:
            print(f"Error generating for {email['id']}: {e}")
            # fall back to returning error in reply
            results.append({
                "id": email["id"],
                "incoming": email["incoming"],
                "generated_reply": f"Error: {e}"
            })
        
    with open("generated_replies.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Saved generated replies to generated_replies.json")
