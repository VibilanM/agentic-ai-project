import streamlit as st
from pypdf import PdfReader
from supabase import create_client
import requests
import json
import time
import re

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Agentic Career Advisor",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DARK THEME CUSTOM CSS ---
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Dark Theme */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #0f0f1a !important;
        color: #e0e0e0 !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    /* Sidebar Dark */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #0f0f1a 100%) !important;
        border-right: 1px solid #2d2d44;
    }
    
    [data-testid="stSidebar"] * {
        color: #e0e0e0 !important;
    }
    
    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 700;
    }
    
    h1 {
        background: linear-gradient(90deg, #00d4ff 0%, #7c3aed 50%, #ff6b6b 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 2.5rem !important;
    }

    /* Buttons - Neon Glow Effect */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 0.85rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    /* Progress Bar - Animated Gradient */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #00d4ff, #7c3aed, #ff6b6b);
        background-size: 200% 200%;
        animation: gradient 3s ease infinite;
        border-radius: 10px;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Cards/Containers - Glassmorphism */
    [data-testid="stExpander"], .stAlert {
        background: rgba(255, 255, 255, 0.05) !important;
        backdrop-filter: blur(10px);
        border-radius: 16px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* Text Area & Inputs */
    .stTextArea textarea, .stTextInput input {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #e0e0e0 !important;
        padding: 1rem;
    }
    
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 2px dashed rgba(255, 255, 255, 0.2) !important;
        border-radius: 16px !important;
        padding: 1.5rem;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #667eea !important;
        background: rgba(102, 126, 234, 0.05) !important;
    }

    /* Metric Cards */
    [data-testid="stMetricValue"] {
        font-size: 3rem !important;
        background: linear-gradient(90deg, #00d4ff, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Badges/Pills */
    .skill-badge {
        display: inline-block;
        padding: 0.5em 1em;
        font-size: 0.9em;
        font-weight: 600;
        border-radius: 50px;
        margin: 0.25rem;
        transition: all 0.3s ease;
    }
    
    .skill-badge-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #fff;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .skill-badge-warning {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: #fff;
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.3);
    }
    
    .skill-badge:hover {
        transform: translateY(-2px);
    }
    
    /* Divider */
    hr {
        border-color: rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Info/Warning/Success boxes */
    .stAlert > div {
        color: #e0e0e0 !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a2e;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #667eea, #764ba2);
        border-radius: 10px;
    }
    
    /* Step Cards */
    .step-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .step-card:hover {
        border-color: #667eea;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
    }
</style>
""", unsafe_allow_html=True)


supabase_url = "https://vgyfjrnpecfebplytafg.supabase.co"
supabase_key = "sb_publishable_QYYGfPW5cYgI_UsKNrpkMw_BZUG7yZi"
headers_supabase = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

try:
    supabase = create_client(supabase_url, supabase_key)
except Exception as e:
    st.error(f"Failed to connect to Supabase: {e}")

openrouter_key = "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"
headers_openrouter = {
    "Authorization": f"Bearer {openrouter_key}",
    "Content-Type": "application/json"
}

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    return text

def extract_json(text):
    """Robust JSON extraction that handles markdown code blocks and other formatting."""
    if not text:
        return None
    
    try:
        # First, try to find JSON in markdown code blocks
        code_block_pattern = r'```(?:json)?\s*(\{[\s\S]*?\})\s*```'
        match = re.search(code_block_pattern, text)
        if match:
            return json.loads(match.group(1))
        
        # Next, find the first '{' and last '}' for raw JSON
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            json_str = text[start:end]
            # Clean up potential issues
            json_str = json_str.replace('\n', ' ').replace('\r', '')
            return json.loads(json_str)
        
        return None
    except json.JSONDecodeError:
        # Try more aggressive cleaning
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                json_str = text[start:end]
                # Remove control characters
                json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
                return json.loads(json_str)
        except:
            pass
        return None
    except Exception:
        return None

def display_skills(skills, skill_type="current"):
    if not skills:
        st.markdown("_No skills identified_")
        return
    
    if skill_type == "current":
        st.markdown("##### ✅ Current Skills")
        html = '<div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">'
        for skill in skills:
            html += f'<span class="skill-badge skill-badge-primary">{skill}</span>'
        html += '</div>'
    else:
        st.markdown("##### ⚠️ Skills to Improve")
        html = '<div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">'
        for skill in skills:
            html += f'<span class="skill-badge skill-badge-warning">{skill}</span>'
        html += '</div>'
    
    st.markdown(html, unsafe_allow_html=True)
    st.write("")

def job_search(data):
    sc3 = """You are a job-search advisory agent in a multi-agent career system.

    The user has the required skills for their target role and is ready to apply.
    Your task is to help the user successfully search and apply for jobs.

    Your response MUST be a clear, human-readable explanation.

    Structure your response in THREE clearly separated sections:

    1. Job Platforms  
    - List the best platforms for the target role in the order of whichever platform has the highest chance of getting the user a job.

    2. Search Keywords & Filters  
    - Provide exact search keywords the user can paste into job platforms.
    - Suggest useful filters (experience level, location, role type).

    3. Resume & Application Tips  
    - Suggest specific resume improvements or bullet rewrites.
    - Give practical tips to make applications stand out.
    - Keep everything copy-paste friendly.

    Rules:
    - Be practical and specific.
    - Do NOT include motivational or generic advice.
    - Do NOT mention percentages or evaluations.
    - Do NOT suggest further learning steps.
    - Assume the user will act immediately after reading this.
    """

    with st.spinner("🔍 Finding relevant jobs..."):
        ai_response4 = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers_openrouter,
            json={
                "model": "google/gemma-3-27b-it:free",
                "messages": [
                    {"role": "system", "content": sc3},
                    {"role": "user", "content": f"My resume:\n{resume}\n\nMy goal:\n{expectation}\n\nThis is the analysis provided by the previous agent:\n{data}"}
                ]
            }
        )

    if ai_response4.status_code == 200:
        content = ai_response4.json()["choices"][0]["message"]["content"]
        st.success("🎉 You are ready to apply! Here is your strategy:")
        st.markdown(content)
    else:
        st.error(f"Error fetching job search strategy: {ai_response4.status_code}")

def skill_up(data):
    if "foundation_steps" in st.session_state:
        del st.session_state.foundation_steps
        del st.session_state.foundation_index

    sc2 = """You are a skill-upgrading agent in a multi-agent career system.

    The user has basic foundations but is not yet job-ready.
    Your task is to design a intermediate-level learning path to upgrade the user's skills.

    STRICT RULES:
    - Output ONLY valid JSON.
    - NO explanations, NO markdown formatting, NO code blocks.
    - Just raw JSON starting with { and ending with }

    Required JSON Schema:
    {"steps": ["step1", "step2", ...], "chances_percentage": 60, "current_skills": ["skill1", "skill2"]}
    """
    
    with st.spinner("📈 Generating skill-up plan..."):
        ai_response3 = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers_openrouter,
            json={
                "model": "google/gemma-3-27b-it:free",
                "messages": [
                    {"role": "system", "content": sc2},
                    {"role": "user", "content": f"My resume:\n{resume}\n\nMy goal:\n{expectation}\n\nAnalysis:\n{json.dumps(data) if isinstance(data, dict) else data}"}
                ]
            }
        )
    
    if ai_response3.status_code != 200:
        st.error(f"API error: {ai_response3.status_code}")
        return
    
    try:
        raw = ai_response3.json()["choices"][0]["message"]["content"]
        skill_up_response = extract_json(raw)
        
        if not skill_up_response:
            st.error("Could not parse response. Retrying with different approach...")
            with st.expander("View raw response"):
                st.code(raw)
            return
        
        steps = skill_up_response.get("steps", [])
        if not steps:
            st.warning("No steps were generated. Please try again.")
            return
            
    except Exception as e:
        st.error(f"Error processing response: {str(e)}")
        return
    
    if "skill_up_steps" not in st.session_state:
        st.session_state.skill_up_steps = steps
        st.session_state.skill_up_index = 0

    if "step_completed" not in st.session_state:
        st.session_state.step_completed = False

    ind = st.session_state.skill_up_index
    total = len(st.session_state.skill_up_steps)
    
    st.markdown("### 📈 Skill Up Plan")
    if total > 0:
        st.progress(ind / total if total > 0 else 0)
        st.markdown(f"**Progress:** {ind}/{total} steps completed")

    st.session_state.step_completed = False

    if ind < total:
        st.markdown(f"""
        <div class="step-card">
            <h4>Step {ind+1} of {total}</h4>
            <p>{st.session_state.skill_up_steps[ind]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✅ Mark Step as Completed", key="skill_btn_complete"):
            st.session_state.step_completed = True
            st.session_state.skill_up_index += 1
            st.rerun()
    else:
        st.balloons()
        st.success("🎉 Skill Up level complete! Time to Search Jobs!")
        time.sleep(2)
        job_search(data)

def foundation(data):
    sc1 = """You are a foundation-building agent in a multi-agent career system.

    The user is NOT currently ready for their target role.
    Your task is to design a beginner-friendly foundational learning path.

    STRICT RULES:
    - Output ONLY valid JSON.
    - NO explanations, NO markdown formatting, NO code blocks.
    - Just raw JSON starting with { and ending with }

    Required JSON Schema:
    {"steps": ["step1", "step2", ...], "chances_percentage": 30, "current_skills": ["skill1"], "missing_skills": ["skill1", "skill2"]}
    """
    
    with st.spinner("🏗️ Generating foundation plan..."):
        ai_response2 = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers_openrouter,
            json={
                "model": "google/gemma-3-27b-it:free",
                "messages": [
                    {"role": "system", "content": sc1},
                    {"role": "user", "content": f"My resume:\n{resume}\n\nMy goal:\n{expectation}\n\nAnalysis:\n{json.dumps(data) if isinstance(data, dict) else data}"}
                ]
            }
        )
    
    if ai_response2.status_code != 200:
        st.error(f"API error: {ai_response2.status_code}")
        return
    
    try:
        raw = ai_response2.json()["choices"][0]["message"]["content"]
        foundation_response = extract_json(raw)
        
        if not foundation_response:
            st.error("Could not parse response. Please try again.")
            with st.expander("View raw response for debugging"):
                st.code(raw)
            return
        
        steps = foundation_response.get("steps", [])
        if not steps:
            st.warning("No steps were generated. Please try again.")
            return
            
    except Exception as e:
        st.error(f"Error processing response: {str(e)}")
        return
    
    if "foundation_steps" not in st.session_state:
        st.session_state.foundation_steps = steps
        st.session_state.foundation_index = 0

    if "step_completed" not in st.session_state:
        st.session_state.step_completed = False

    ind = st.session_state.foundation_index
    total = len(st.session_state.foundation_steps)

    st.markdown("### 🏗️ Foundation Plan")
    if total > 0:
        st.progress(ind / total if total > 0 else 0)
        st.markdown(f"**Progress:** {ind}/{total} steps completed")

    st.session_state.step_completed = False

    if ind < total:
        st.markdown(f"""
        <div class="step-card">
            <h4>Step {ind+1} of {total}</h4>
            <p>{st.session_state.foundation_steps[ind]}</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("✅ Mark Step as Completed", key="foundation_btn_complete"):
            st.session_state.step_completed = True
            st.session_state.foundation_index += 1
            st.rerun()

    else:
        st.success("🎉 Foundation level complete! Advancing to Skill Up Phase...")
        time.sleep(2)
        skill_up(data)

def decide_mode(ai_response1):
    try:
        data = json.loads(ai_response1) if isinstance(ai_response1, str) else ai_response1
    except json.JSONDecodeError:
        st.error("Could not parse analysis results.")
        return

    # Store analysis data in session state for persistence
    st.session_state.analysis_data = data
    
    chances = data.get("chances_percentage", 0)
    current_skills = data.get("current_skills", [])
    missing_skills = data.get("missing_skills", [])

    col1, col2 = st.columns(2)
    with col1:
        display_skills(current_skills, "current")
    with col2:
        display_skills(missing_skills, "missing")
    
    st.divider()

    if chances < 40:
        st.info("🏗️ Starting Foundation Path - Let's build your skills from the ground up!")
        st.session_state.current_mode = "foundation"
        foundation(data)
    elif chances < 80:
        st.info("📈 Starting Skill-Up Path - Time to level up your existing skills!")
        st.session_state.current_mode = "skill_up"
        skill_up(data)
    else:
        st.success("🎯 You are Job Ready! Let's find you the perfect opportunity!")
        st.session_state.current_mode = "job_search"
        job_search(data)

def resume_analysis(resume_text, goal):
    system_content = '''You are an evaluation agent.

    STRICT RULES:
    - Output ONLY valid JSON.
    - NO explanations, NO markdown formatting, NO code blocks.
    - Just raw JSON starting with { and ending with }

    Required JSON Schema:
    {"chances_percentage": 50, "current_skills": ["skill1", "skill2"], "missing_skills": ["skill1", "skill2"]}

    Where chances_percentage is 0-100 indicating job match likelihood.
    '''
    
    with st.spinner("🔍 Analyzing your resume..."):
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers_openrouter,
            json={
                "model": "google/gemma-3-27b-it:free",
                "messages": [
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": f"Resume:\n{resume_text}\n\nTarget Role:\n{goal}\n\nAnalyze the match percentage."}
                ]
            }
        )
    
    if response.status_code != 200:
        st.error(f"API error: {response.status_code}")
        return None
    
    try:
        raw_content = response.json()["choices"][0]["message"]["content"]
        data = extract_json(raw_content)
        
        if not data:
            st.error("Could not parse analysis response.")
            with st.expander("View raw response for debugging"):
                st.code(raw_content)
            return None
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None
        
    chances = data.get("chances_percentage", 0)
    
    # Display Analysis Result with beautiful metric
    st.markdown("### 📊 Analysis Result")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Custom styled metric
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem; background: rgba(255,255,255,0.05); border-radius: 20px; border: 1px solid rgba(255,255,255,0.1);">
            <p style="font-size: 1rem; color: #888; margin-bottom: 0.5rem;">Match Probability</p>
            <p style="font-size: 4rem; font-weight: 700; background: linear-gradient(90deg, #00d4ff, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0;">{chances}%</p>
        </div>
        """, unsafe_allow_html=True)
        st.progress(chances / 100)

    if "missing_skills" not in data:
        data["missing_skills"] = []
    
    return json.dumps(data)

# --- MAIN UI LAYOUT ---

st.markdown("""
<div style="text-align: center; padding: 2rem 0;">
    <h1>🚀 Agentic Career Advisor</h1>
    <p style="font-size: 1.2rem; color: #888;">Your AI-powered partner for career growth</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# Sidebar for Inputs
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h2>📂 Upload & Configure</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("Upload your resume and define your target role to get started.")
    
    file = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])
    expectation = st.text_area("🎯 Target Role / Goal", height=150, placeholder="e.g. Senior Python Developer at a Tech Startup...")
    
    st.markdown("<br>", unsafe_allow_html=True)
    analyze_btn = st.button("🚀 Analyze Profile")

# Main Content Area

# Initialize session state
if "current_mode" not in st.session_state:
    st.session_state.current_mode = None
if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None

# Helper function to display skill_up UI from session state
def display_skill_up_ui():
    if "skill_up_steps" not in st.session_state:
        return
    
    ind = st.session_state.skill_up_index
    total = len(st.session_state.skill_up_steps)
    
    st.markdown("### 📈 Skill Up Plan")
    if total > 0:
        st.progress(ind / total if total > 0 else 0)
        st.markdown(f"**Progress:** {ind}/{total} steps completed")

    if ind < total:
        st.markdown(f"""
        <div class="step-card">
            <h4>Step {ind+1} of {total}</h4>
            <p>{st.session_state.skill_up_steps[ind]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✅ Mark Step as Completed", key="skill_display_btn"):
            st.session_state.skill_up_index += 1
            st.rerun()
    else:
        st.balloons()
        st.success("🎉 Skill Up level complete! Time to Search Jobs!")
        st.session_state.current_mode = "job_search"
        time.sleep(1)
        st.rerun()

# Helper function to display foundation UI from session state
def display_foundation_ui():
    if "foundation_steps" not in st.session_state:
        return
    
    ind = st.session_state.foundation_index
    total = len(st.session_state.foundation_steps)

    st.markdown("### 🏗️ Foundation Plan")
    if total > 0:
        st.progress(ind / total if total > 0 else 0)
        st.markdown(f"**Progress:** {ind}/{total} steps completed")

    if ind < total:
        st.markdown(f"""
        <div class="step-card">
            <h4>Step {ind+1} of {total}</h4>
            <p>{st.session_state.foundation_steps[ind]}</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("✅ Mark Step as Completed", key="foundation_display_btn"):
            st.session_state.foundation_index += 1
            st.rerun()
    else:
        st.success("🎉 Foundation level complete! Advancing to Skill Up Phase...")
        st.session_state.current_mode = "skill_up"
        del st.session_state.foundation_steps
        del st.session_state.foundation_index
        time.sleep(1)
        st.rerun()

# Check if we have an active learning path
if st.session_state.current_mode == "skill_up" and "skill_up_steps" in st.session_state:
    display_skill_up_ui()

elif st.session_state.current_mode == "foundation" and "foundation_steps" in st.session_state:
    display_foundation_ui()

elif st.session_state.current_mode == "job_search" and file is not None and expectation:
    resume = extract_text_from_pdf(file)
    job_search(st.session_state.analysis_data)

elif st.session_state.current_mode == "skill_up" and file is not None and expectation:
    # Need to generate skill_up steps
    resume = extract_text_from_pdf(file)
    skill_up(st.session_state.analysis_data)

elif file is not None and expectation:
    try:
        resume = extract_text_from_pdf(file)
        with st.expander("📄 View Extracted Resume Text"):
            st.text(resume)
            
        if analyze_btn:
            # Clear previous state when starting new analysis
            for key in ["skill_up_steps", "skill_up_index", "foundation_steps", "foundation_index"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.current_mode = None
            
            analysis = resume_analysis(resume, expectation)
            if analysis:
                decide_mode(analysis)
                
    except Exception as e:
        st.error(f"Error reading file: {e}")

elif analyze_btn:
    st.sidebar.error("⚠️ Please upload a resume and enter a goal.")
else:
    # Welcome screen
    st.markdown("""
    <div style="text-align: center; padding: 3rem; max-width: 800px; margin: auto;">
        <h3>Welcome! Here's how it works:</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="step-card" style="text-align: center; min-height: 200px;">
            <h3>📄</h3>
            <h4>Upload Resume</h4>
            <p style="color: #888;">Upload your PDF resume in the sidebar</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="step-card" style="text-align: center; min-height: 200px;">
            <h3>🎯</h3>
            <h4>Set Your Goal</h4>
            <p style="color: #888;">Tell us what job you want to land</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="step-card" style="text-align: center; min-height: 200px;">
            <h3>🚀</h3>
            <h4>Get Your Plan</h4>
            <p style="color: #888;">Receive a personalized career roadmap</p>
        </div>
        """, unsafe_allow_html=True)

