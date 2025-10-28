import json
import io
import streamlit as st
from groq import Groq


# Try importing PDF/DOCX libraries
try:
    import PyPDF2
except ImportError:
    st.warning("PyPDF2 not installed. Install with: pip install PyPDF2")

try:
    from docx import Document
except ImportError:
    st.warning("python-docx not installed. Install with: pip install python-docx")


# Helper functions
def extract_text_from_pdf(file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""


def extract_text_from_docx(file):
    """Extract text from DOCX file"""
    try:
        doc = Document(file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        st.error(f"Error reading DOCX: {e}")
        return ""


def call_groq_api(prompt, api_key, max_tokens=1000):
    """Call Groq API with given prompt"""
    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", #"llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error calling Groq API: {e}")
        return None


def analyze_resume_strengths(resume_text, api_key):
    """Analyze resume and extract top strengths"""
    prompt = f"""Analyze the following resume and identify the top 5 key strengths of the candidate. 
For each strength, provide a brief explanation.

Resume:
{resume_text}

Return the response in JSON format:
{{"strengths": [{{"strength": "...", "explanation": "..."}}, ...]}}
"""

    response = call_groq_api(prompt, api_key)
    if response:
        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            return data.get('strengths', [])
        except:
            # Fallback: parse as text
            return [{"strength": "Analysis completed", "explanation": response}]
    return []


def generate_interview_questions(resume_text, job_description, api_key):
    """Generate 5 relevant interview questions"""
    prompt = f"""Based on the following resume and job description, generate 5 relevant interview questions.
The questions should test technical skills, behavioral competencies, and role fit.

Resume:
{resume_text[:2000]}...

Job Description:
{job_description}

Return the response in JSON format:
{{"questions": [{{"question": "...", "focus_area": "...", "difficulty": "..."}}, ...]}}

Focus areas can be: Technical, Behavioral, Situational, Role-specific
Difficulty can be: Easy, Medium, Hard
"""

    response = call_groq_api(prompt, api_key, max_tokens=1500)
    if response:
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            return data.get('questions', [])
        except:
            return []
    return []


def evaluate_answer(question, answer, api_key):
    """Evaluate candidate's answer to a question"""
    prompt = f"""You are an experienced interviewer. Evaluate the following answer to an interview question.
Provide a score (1-10) and brief feedback.

Question: {question}

Answer: {answer}

Return in JSON format:
{{"score": X, "feedback": "...", "strengths": "...", "improvements": "..."}}
"""

    response = call_groq_api(prompt, api_key, max_tokens=500)
    if response:
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            return json.loads(json_str)
        except:
            return {"score": 0, "feedback": response}
    return {"score": 0, "feedback": "Unable to evaluate"}

