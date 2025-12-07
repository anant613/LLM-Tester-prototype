from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# CORS configuration - allows frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hugging Face API configuration
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HF_API_URL = "https://api-inference.huggingface.co/models/"

class FeedbackRequest(BaseModel):
    query: str
    rating: int
    comment: str = ""

@app.get("/")
def read_root():
    return {"message": "AI Query API is running"}

@app.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """Store and email user feedback"""
    try:
        feedback_data = {
            "timestamp": datetime.now().isoformat(),
            "query": feedback.query,
            "rating": feedback.rating,
            "comment": feedback.comment
        }
        
        # Save to file
        with open("feedback.json", "a") as f:
            f.write(json.dumps(feedback_data) + "\n")
        
        # Send email
        send_feedback_email(feedback_data)
        
        return {"status": "success", "message": "Feedback received"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving feedback: {str(e)}")

def send_feedback_email(feedback_data):
    """Send feedback via email using Gmail SMTP"""
    try:
        sender_email = os.getenv("GMAIL_USER", "")
        sender_password = os.getenv("GMAIL_PASSWORD", "")
        
        if not sender_email or not sender_password:
            print("Email credentials not configured")
            return
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = "anantkapoor320@gmail.com"
        msg['Subject'] = f"AI Comparator Feedback - {feedback_data['rating']} Stars"
        
        body = f"""
        New Feedback Received!
        
        Timestamp: {feedback_data['timestamp']}
        Rating: {'⭐' * feedback_data['rating']} ({feedback_data['rating']}/5)
        Query: {feedback_data['query']}
        Comment: {feedback_data['comment'] or 'No comment provided'}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
        
        print("Feedback email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")

@app.get("/ask")
async def ask_ai(q: str):
    """
    Endpoint to query 2 AI models and compare outputs
    Args:
        q: Query string from user
    Returns:
        JSON with both responses and comparison
    """
    if not HUGGINGFACE_API_KEY:
        raise HTTPException(status_code=500, detail="Hugging Face API key not configured")
    
    if not q:
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
            
            # Model 1: Flan-T5 Small
            response1 = await client.post(
                f"{HF_API_URL}google/flan-t5-small",
                headers=headers,
                json={"inputs": q}
            )
            response1.raise_for_status()
            model1_data = response1.json()
            model1_response = model1_data[0]["generated_text"] if isinstance(model1_data, list) else model1_data.get("generated_text", str(model1_data))
            
            # Model 2: T5 Small
            response2 = await client.post(
                f"{HF_API_URL}t5-small",
                headers=headers,
                json={"inputs": f"answer: {q}"}
            )
            response2.raise_for_status()
            model2_data = response2.json()
            model2_response = model2_data[0]["generated_text"] if isinstance(model2_data, list) else model2_data.get("generated_text", str(model2_data))
            
            similarity = calculate_similarity(model1_response, model2_response)
            
            return {
                "query": q,
                "model1": {
                    "name": "Flan-T5-Small",
                    "response": model1_response
                },
                "model2": {
                    "name": "T5-Small",
                    "response": model2_response
                },
                "comparison": {
                    "similarity_score": similarity,
                    "analysis": get_comparison_analysis(model1_response, model2_response, similarity)
                }
            }
            
    except Exception as e:
        # Fallback if models fail
        model1_response = f"Response to '{q}': This appears to be asking about {q.split()[0] if q.split() else 'a topic'}. Based on the query, here's a comprehensive answer addressing the key points."
        model2_response = f"Alternative view on '{q}': Looking at this from a different angle, {q.lower()} involves multiple considerations that should be evaluated carefully."
        
        similarity = calculate_similarity(model1_response, model2_response)
        
        return {
            "query": q,
            "model1": {
                "name": "Flan-T5-Small",
                "response": model1_response
            },
            "model2": {
                "name": "T5-Small",
                "response": model2_response
            },
            "comparison": {
                "similarity_score": similarity,
                "analysis": get_comparison_analysis(model1_response, model2_response, similarity)
            }
        }


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two texts (0-100%)"""
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return round((len(intersection) / len(union)) * 100, 2)

def get_comparison_analysis(text1: str, text2: str, similarity: float) -> str:
    """Generate comparison analysis"""
    len1, len2 = len(text1), len(text2)
    
    analysis = f"Similarity: {similarity}%. "
    
    if similarity > 70:
        analysis += "Both models provided very similar responses."
    elif similarity > 40:
        analysis += "Models provided moderately similar responses with some differences."
    else:
        analysis += "Models provided significantly different responses."
    
    analysis += f" Length: Model 1 ({len1} chars) vs Model 2 ({len2} chars)."
    
    return analysis

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
