import streamlit as st
import PyPDF2
import io
import os
from google import genai
from dotenv import load_dotenv


load_dotenv()
st.set_page_config(page_title="AI_Resume_Critiquer", page_icon="📃", layout="centered")
st.title("AI Resume Critiquer")
st.markdown("Upload your resume to get AI-powered feedback tailored to your needs!")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])
job_role = st.text_input("Enter the role you're aiming for (optional)")
analyze = st.button("Analyze Resume")


def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")

def analyze_resume_hf(resume_text, role):
    # prompt = f"""
    # You are an expert resume reviewer. Analyze the following resume and provide structured feedback focusing on:
    # 1. Content clarity and impact
    # 2. Skills presentation
    # 3. Experience descriptions
    # 4. Specific improvements for {role if role else 'general job applications'}
    # 5. Improvements needed 
    # 6. Generate an ATS score at last
    # Resume content:
    # {resume_text}
    # """
    prompt = f"""
    You are an expert resume reviewer with 10+ years of experience reviewing software engineer resumes.
    Your task is to analyze the following resume and provide **highly detailed, actionable, and structured feedback**.
    Focus on these aspects:
    1. Profile Summary: Suggest improvements for clarity, impact, and relevance to {role if role else 'software engineering'} roles.
    2. Technical Skills: Check completeness, relevance, and presentation. Suggest missing but important technologies.
    3. Projects / Experience: Evaluate each project for impact, clarity, quantification of achievements, and role-specific relevance. Suggest STAR-format improvements.
    4. Certifications: Comment on relevance and presentation.
    5. Keywords: Recommend keywords commonly used in job descriptions for {role if role else 'software engineering'} roles.
    6. Soft Skills: Highlight if any are missing or could be better presented.
    7. Formatting & Clarity: Provide advice on structure, readability, and grammar.
    8. Contact Info & Links: Verify clarity and standard formatting (LinkedIn, GitHub, email, phone).
    9. Quantification: Suggest numbers, metrics, or percentages wherever possible to make achievements measurable.

    **Provide your response in this format**:
    - Section Name
      - Strengths:
      - Improvements:
      - Example Rewrite (if applicable)

    Resume Content:
    {resume_text}
    """
    # MAX_INPUT_CHARS = 2000
    # prompt = prompt[:MAX_INPUT_CHARS]
    # result = generator(prompt, max_length=500)[0]['generated_text']
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )
    return response.text

if analyze and uploaded_file:
    try:
        file_content = extract_text_from_file(uploaded_file)
        if not file_content.strip():
            st.error("File does not have any content...")
            st.stop()

        st.markdown("### Analysis Result")
        response = analyze_resume_hf(file_content,job_role)
        st.markdown(response)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

