from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os
import os.path
import time
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from pdf_utils import extract_pdf_text

# Load .env from parent directory
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY not found. Please check your .env file.")

# ✅ DEBUG: Verify API key is loaded
print(f"✅ OPENROUTER_API_KEY loaded: {OPENROUTER_API_KEY[:20]}...{OPENROUTER_API_KEY[-10:]}")
print(f"✅ API Key length: {len(OPENROUTER_API_KEY)} characters")
print(f"✅ .env file location: {dotenv_path}")

# OpenRouter Gemma 4 Configuration
# ✅ Using Gemma 4 only - it's free and supports system prompts (developer instructions)
# Gemma 3 does NOT support system prompts, so we removed the fallback
AI_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

app = FastAPI(title="Brain Checker AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory PDF store (use a DB in production)
pdf_store = {}

SYSTEM_PROMPTS = {
    "report": """You are Brain Checker's Post-Counseling AI Assistant in UNDERSTAND REPORT mode.
Help parents and students understand their psychometric counseling report in simple, warm, parent-friendly language.
Rules:
- ONLY use information from the report PDF text provided.
- Always mention Source (IQ/RIASEC/Personality/Counselor Remarks) and Confidence (Direct/Inferred/General).
- End every report-based answer with a disclaimer about consulting the counselor.
- Use simple words. Avoid jargon.
- Suggest next steps after answering (Career Roadmap, Find Colleges, Action Plan, Parent Guide).
Report Content:\n""",

    "roadmap": """You are Brain Checker's Post-Counseling AI Assistant in CAREER & COLLEGE ROADMAP mode.
Create clear, timeline-based career and education roadmaps for students.
- Present as a timeline: 10th → 12th → Entrance Exams → Degree → Career → Skills.
- Include specific exams (JEE/NEET/CLAT/NDA etc.), degree options, and skills.
- Be specific, practical, and encouraging.
- Keep language simple and parent-friendly.""",

    "college": """You are Brain Checker's Post-Counseling AI Assistant in FIND BEST FIT COLLEGE mode.
Guide parents and students to find the best colleges through friendly conversation.
- Collect: stream, career interest, marks, entrance exams, preferred location, budget.
- Suggest: 3-5 Government colleges, 3-5 Private colleges, required exams, backup options.
- Use real Indian college names.
- Be encouraging and realistic.""",

    "plan": """You are Brain Checker's Post-Counseling AI Assistant in ACTION PLAN mode.
Create personalised 30-60-90 day action plans.
- Ask: study hours per day, main challenge, target career/exam.
- Generate a table-format plan: 30 Days / 60 Days / 90 Days.
- Each section: Time period, Student Actions, Parent Support Actions.
- Be practical and achievable.""",

    "parent": """You are Brain Checker's Post-Counseling AI Assistant in PARENT GUIDE mode.
Advise parents on how to best support their child after counseling.
- Cover: learning styles, communication, motivation, what to avoid, study environment.
- Be warm, empathetic, non-judgmental.
- Never give medical or psychological diagnoses.
- Acknowledge that parenting is hard and they are doing their best."""
}


class ChatRequest(BaseModel):
    mode: str
    message: str
    history: list
    session_id: Optional[str] = None


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...), session_id: str = Query("default")):
    """
    Upload a PDF and extract its text content.
    Args:
        file: The PDF file to upload
        session_id: Session ID to store the PDF text (query parameter, default: "default")
    
    Returns:
        JSON: {"status": "success", "filename": str, "characters": int, "session_id": str}
    """
    try:
        # Validate file extension
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            error_msg = "Only PDF files are supported."
            print(f"❌ Extension error: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)

        print(f"\n📤 Upload request received:")
        print(f"   Filename: {file.filename}")
        print(f"   Session ID: {session_id}")
        print(f"   Content-Type: {file.content_type}")
        
        # Read file contents
        try:
            contents = await file.read()
            print(f"   File size: {len(contents)} bytes")
            
            if len(contents) == 0:
                raise HTTPException(status_code=400, detail="PDF file is empty.")
                
        except Exception as e:
            error_msg = f"Failed to read PDF file: {str(e)}"
            print(f"❌ Read error: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Extract text from PDF
        try:
            text = extract_pdf_text(contents)
            print(f"   Extracted text: {len(text)} characters")
        except Exception as e:
            error_msg = f"Failed to extract text from PDF: {str(e)}"
            print(f"❌ Extraction error: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)

        # Validate extracted text
        if not text or not text.strip():
            error_msg = "Could not extract text from PDF. Make sure it's not a scanned image."
            print(f"❌ Content error: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)

        # Store PDF text in memory
        pdf_store[session_id] = text
        print(f"✅ PDF uploaded and stored successfully for session: {session_id}")
        
        # Ensure response is valid JSON
        response = {
            "status": "success",
            "filename": str(file.filename),
            "characters": int(len(text)),
            "session_id": str(session_id)
        }
        print(f"   Returning: {response}")
        return response
    
    except HTTPException as http_err:
        print(f"❌ HTTP error: {http_err.status_code} - {http_err.detail}")
        raise
    except Exception as e:
        error_msg = f"Unexpected error during PDF upload: {str(e)}"
        print(f"❌ Unexpected error: {error_msg}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_msg)


@app.post("/api/ask")
async def ask(req: ChatRequest):
    """
    Chat endpoint using Gemma 4 (supports system prompts for ai modes)
    No fallback to avoid unsupported feature errors from other models
    """
    if req.mode not in SYSTEM_PROMPTS:
        raise HTTPException(status_code=400, detail="Invalid mode.")

    system_prompt = SYSTEM_PROMPTS[req.mode]

    # Attach PDF text for report mode
    if req.mode == "report":
        pdf_text = pdf_store.get(req.session_id, "(No PDF uploaded yet.)")
        system_prompt += pdf_text

    # Build OpenRouter chat history
    chat_history = []
    for msg in req.history:
        chat_history.append({"role": msg["role"], "content": msg["content"]})

    # Add current message to history
    chat_history.append({"role": "user", "content": req.message})

    try:
        # Initialize OpenRouter client with OpenAI SDK
        client = OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_BASE_URL)
        
        print(f"\n🔵 API Request sent to OpenRouter:")
        print(f"   Model: {AI_MODEL}")
        print(f"   API Key (masked): {OPENROUTER_API_KEY[:20]}...{OPENROUTER_API_KEY[-10:]}")
        print(f"   Message: {req.message[:50]}...")
        
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[{"role": "system", "content": system_prompt}] + chat_history,
            temperature=0.7,
            max_tokens=2048
        )
        print(f"✅ SUCCESS! Response received from {response.model}")
        return {"reply": response.choices[0].message.content, "mode": req.mode, "model": AI_MODEL}
        
    except Exception as e:
        error_str = str(e).lower()
        
        # Handle rate limits with helpful message
        if "429" in str(e) or "quota" in error_str or "rate_limit" in error_str:
            raise HTTPException(
                status_code=429, 
                detail="⏱️ Free tier rate limit reached. Please wait a few moments and try again. The free tier has hourly usage limits."
            )
        
        # Handle developer instruction not enabled errors
        if "developer instruction" in error_str or "not enabled" in error_str:
            raise HTTPException(
                status_code=400,
                detail="❌ Model error: This model doesn't support the required AI instruction format. Please try again in a moment."
            )
        
        # Generic error handling
        raise HTTPException(status_code=500, detail=f"OpenRouter API Error: {str(e)}")


@app.get("/")
def root():
    return {"message": "Brain Checker AI API is running. Visit /docs for API documentation."}


# ✅ IMPORTANT: Serve static files with custom route handler
# This ensures /api/* routes are handled first, then static files serve the frontend
frontend_dir = Path(__file__).parent.parent

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """Serve static files for the frontend. API routes are handled before this."""
    
    # Skip API routes (they should be handled above)
    if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("redoc") or full_path.startswith("openapi"):
        raise HTTPException(status_code=404, detail="Not found")
    
    # Try to serve the requested file
    file_path = frontend_dir / full_path
    
    # Security check: ensure file is within frontend_dir
    try:
        file_path = file_path.resolve()
        frontend_dir_resolved = frontend_dir.resolve()
        if frontend_dir_resolved not in file_path.parents and file_path != frontend_dir_resolved:
            raise HTTPException(status_code=404, detail="Not found")
    except:
        raise HTTPException(status_code=404, detail="Not found")
    
    # If it's a directory or doesn't exist, serve index.html
    if not file_path.exists() or file_path.is_dir():
        index_path = frontend_dir / "index.html"
        if index_path.exists():
            return FileResponse(index_path, media_type="text/html")
        raise HTTPException(status_code=404, detail="Not found")
    
    # Serve the file
    return FileResponse(file_path)


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 Starting Brain Checker AI Backend Server")
    print("="*60)
    print("📡 Server: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("📖 ReDoc: http://localhost:8000/redoc")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
