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
    
    /* Quiz Mode Styles */
    .quiz-fullscreen-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
        z-index: 9999;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;
    }
    
    .quiz-container {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        padding: 2.5rem;
        max-width: 800px;
        width: 100%;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
    }
    
    .quiz-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .quiz-timer {
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #ff6b6b, #feca57);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: pulse 1s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .quiz-question {
        font-size: 1.3rem;
        line-height: 1.8;
        color: #fff;
        margin-bottom: 2rem;
    }
    
    .quiz-option {
        background: rgba(255, 255, 255, 0.05);
        border: 2px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 0.75rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        color: #e0e0e0;
    }
    
    .quiz-option:hover {
        border-color: #667eea;
        background: rgba(102, 126, 234, 0.1);
        transform: translateX(10px);
    }
    
    .quiz-option-selected {
        border-color: #667eea !important;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2)) !important;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.3);
    }
    
    .quiz-option-correct {
        border-color: #4ade80 !important;
        background: rgba(74, 222, 128, 0.2) !important;
    }
    
    .quiz-option-wrong {
        border-color: #f87171 !important;
        background: rgba(248, 113, 113, 0.2) !important;
    }
    
    .quiz-progress {
        width: 100%;
        height: 8px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        overflow: hidden;
        margin-bottom: 1.5rem;
    }
    
    .quiz-progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 10px;
        transition: width 0.3s ease;
    }
    
    .quiz-warning {
        background: linear-gradient(135deg, rgba(248, 113, 113, 0.2), rgba(239, 68, 68, 0.3));
        border: 1px solid #ef4444;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        margin: 2rem 0;
    }
    
    .quiz-warning h3 {
        color: #f87171 !important;
        margin-bottom: 0.5rem;
    }
    
    .quiz-score-card {
        text-align: center;
        padding: 3rem;
    }
    
    .quiz-score {
        font-size: 5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00d4ff, #7c3aed, #ff6b6b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .proctored-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 600;
        animation: recording-pulse 2s ease-in-out infinite;
    }
    
    @keyframes recording-pulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
        50% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
    }
    
    .proctored-badge::before {
        content: '';
        width: 8px;
        height: 8px;
        background: white;
        border-radius: 50%;
        animation: blink 1s ease-in-out infinite;
    }
    
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
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

def api_request_with_retry(messages, system_content=None, max_retries=3):
    """Make API request with retry logic for rate limiting (429 errors)."""
    for attempt in range(max_retries):
        try:
            msg_list = []
            if system_content:
                msg_list.append({"role": "system", "content": system_content})
            msg_list.extend(messages)
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers_openrouter,
                json={
                    "model": "google/gemma-3-27b-it:free",
                    "messages": msg_list
                }
            )
            
            if response.status_code == 200:
                return response
            elif response.status_code == 429:
                # Rate limited - wait and retry
                wait_time = (2 ** attempt) * 2  # 2, 4, 8 seconds
                st.warning(f"⏳ Rate limited. Waiting {wait_time} seconds before retry ({attempt + 1}/{max_retries})...")
                time.sleep(wait_time)
                continue
            else:
                return response  # Return other errors immediately
                
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2)
    
    return response  # Return last response if all retries failed

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

# =============================================
# FEATURE 1: AI-POWERED QUIZ GENERATOR
# =============================================

def generate_quiz_questions(topic, num_questions=5):
    """Generate quiz questions using AI based on a skill topic."""
    quiz_prompt = f"""Generate exactly {num_questions} multiple choice questions to test knowledge on: {topic}

    STRICT RULES:
    - Output ONLY valid JSON, no markdown, no explanations
    - Each question must have exactly 4 options (A, B, C, D)
    - Include the correct answer key
    
    Required JSON Schema:
    {{"questions": [
        {{"question": "Question text here?", "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}}, "correct": "A", "explanation": "Brief explanation"}},
        ...
    ]}}
    """
    
    try:
        response = api_request_with_retry(
            messages=[{"role": "user", "content": quiz_prompt}],
            system_content="You are a quiz generator. Output only valid JSON."
        )
        
        if response.status_code == 200:
            raw = response.json()["choices"][0]["message"]["content"]
            quiz_data = extract_json(raw)
            if quiz_data and "questions" in quiz_data:
                return quiz_data["questions"]
        elif response.status_code == 429:
            st.error("⚠️ API rate limit exceeded. Please wait a moment and try again.")
        else:
            st.error(f"API error: {response.status_code}")
        return None
    except Exception as e:
        st.error(f"Error generating quiz: {e}")
        return None

# =============================================
# FEATURE 2: PROCTORED QUIZ MODE
# =============================================

def get_fullscreen_js():
    """JavaScript for fullscreen mode and tab switch detection."""
    return """
    <script>
        // Track tab switch violations
        let tabSwitchCount = 0;
        const maxViolations = 1;
        
        // Fullscreen functions
        function enterFullscreen() {
            const elem = document.documentElement;
            if (elem.requestFullscreen) {
                elem.requestFullscreen();
            } else if (elem.webkitRequestFullscreen) {
                elem.webkitRequestFullscreen();
            } else if (elem.msRequestFullscreen) {
                elem.msRequestFullscreen();
            }
        }
        
        function exitFullscreen() {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            }
        }
        
        // Visibility change detection
        document.addEventListener('visibilitychange', function() {
            if (document.hidden && window.quizActive) {
                tabSwitchCount++;
                window.tabViolation = true;
                // Store violation in sessionStorage for Streamlit to detect
                sessionStorage.setItem('quiz_violation', 'true');
                sessionStorage.setItem('violation_count', tabSwitchCount.toString());
                
                // Alert and reload to trigger Streamlit rerun
                alert('⚠️ QUIZ TERMINATED: You switched tabs or left the app. This is not allowed during the proctored quiz.');
                window.location.reload();
            }
        });
        
        // Focus/blur detection
        window.addEventListener('blur', function() {
            if (window.quizActive) {
                tabSwitchCount++;
                window.tabViolation = true;
                sessionStorage.setItem('quiz_violation', 'true');
                sessionStorage.setItem('violation_count', tabSwitchCount.toString());
            }
        });
        
        // Prevent context menu and keyboard shortcuts
        document.addEventListener('contextmenu', function(e) {
            if (window.quizActive) {
                e.preventDefault();
                return false;
            }
        });
        
        document.addEventListener('keydown', function(e) {
            if (window.quizActive) {
                // Block common shortcuts
                if ((e.ctrlKey || e.metaKey) && (e.key === 'c' || e.key === 'v' || e.key === 't' || e.key === 'Tab')) {
                    e.preventDefault();
                    return false;
                }
                if (e.key === 'F12' || (e.ctrlKey && e.shiftKey && e.key === 'I')) {
                    e.preventDefault();
                    return false;
                }
            }
        });
        
        console.log('Proctored Quiz Mode Initialized');
    </script>
    """

def check_violation_js():
    """JavaScript to check for violations."""
    return """
    <script>
        // Check sessionStorage for violations on load
        const violation = sessionStorage.getItem('quiz_violation');
        if (violation === 'true') {
            console.log('Violation detected!');
        }
    </script>
    """

def render_proctored_quiz(questions, quiz_topic):
    """Render the proctored quiz interface."""
    
    # Initialize quiz state
    if "quiz_started" not in st.session_state:
        st.session_state.quiz_started = False
    if "quiz_current_q" not in st.session_state:
        st.session_state.quiz_current_q = 0
    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}
    if "quiz_terminated" not in st.session_state:
        st.session_state.quiz_terminated = False
    if "quiz_completed" not in st.session_state:
        st.session_state.quiz_completed = False
    if "quiz_score" not in st.session_state:
        st.session_state.quiz_score = 0
    if "violation_detected" not in st.session_state:
        st.session_state.violation_detected = False
    
    # Proctoring JavaScript - This creates a persistent monitoring script
    proctoring_script = """
    <script>
    (function() {
        // Prevent multiple initializations
        if (window.proctorInitialized) return;
        window.proctorInitialized = true;
        
        let violationCount = 0;
        const streamlitDoc = window.parent.document;
        
        // Function to trigger violation
        function triggerViolation(reason) {
            violationCount++;
            console.log('PROCTOR VIOLATION:', reason);
            
            // Show alert
            alert('⚠️ QUIZ VIOLATION DETECTED!\\n\\n' + reason + '\\n\\nYour quiz will be terminated.');
            
            // Set flag in localStorage for Streamlit to detect
            localStorage.setItem('quiz_violation', 'true');
            localStorage.setItem('violation_reason', reason);
            
            // Reload to let Streamlit detect the violation
            window.parent.location.reload();
        }
        
        // Check for existing violation on page load
        if (localStorage.getItem('quiz_violation') === 'true') {
            // Clear after reading
            localStorage.removeItem('quiz_violation');
            console.log('Previous violation detected');
        }
        
        // Tab visibility change detection
        document.addEventListener('visibilitychange', function() {
            if (document.hidden) {
                triggerViolation('You switched to another tab or minimized the browser.');
            }
        });
        
        // Window blur detection (clicking outside)
        window.addEventListener('blur', function() {
            setTimeout(function() {
                if (!document.hasFocus()) {
                    triggerViolation('You clicked outside the quiz window.');
                }
            }, 100);
        });
        
        // Fullscreen exit detection
        document.addEventListener('fullscreenchange', function() {
            if (!document.fullscreenElement && window.quizInProgress) {
                triggerViolation('You exited full-screen mode.');
            }
        });
        
        // Block keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            // Block Alt+Tab, Ctrl+Tab, etc.
            if (e.altKey || (e.ctrlKey && e.key === 'Tab') || e.key === 'Meta') {
                e.preventDefault();
                triggerViolation('Keyboard shortcut detected (potential tab switch).');
                return false;
            }
            // Block F12, Ctrl+Shift+I (DevTools)
            if (e.key === 'F12' || (e.ctrlKey && e.shiftKey && e.key === 'I')) {
                e.preventDefault();
                return false;
            }
        });
        
        // Block right-click
        document.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            return false;
        });
        
        console.log('Proctor Mode Activated - Monitoring enabled');
    })();
    </script>
    """
    
    # Terminated state
    if st.session_state.quiz_terminated:
        st.error("### 🚫 Quiz Terminated")
        st.warning("""
        **Integrity Violation Detected**
        
        You switched tabs, minimized the window, or left the application during the proctored quiz.
        
        This action is not allowed during examination mode to ensure fair assessment.
        
        Your quiz has been marked as incomplete.
        """)
        
        if st.button("🔄 Restart Quiz", key="restart_quiz", use_container_width=True):
            st.session_state.quiz_started = False
            st.session_state.quiz_terminated = False
            st.session_state.quiz_current_q = 0
            st.session_state.quiz_answers = {}
            st.session_state.quiz_completed = False
            st.session_state.violation_detected = False
            st.rerun()
        return
    
    # Completed state - Show results
    if st.session_state.quiz_completed:
        correct = st.session_state.quiz_score
        total = len(questions)
        percentage = int((correct / total) * 100)
        
        st.success("### 🎉 Quiz Completed!")
        
        # Score display
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.metric(label="Your Score", value=f"{percentage}%", delta=f"{correct}/{total} correct")
        
        # Show detailed results
        with st.expander("📊 View Detailed Results", expanded=True):
            for i, q in enumerate(questions):
                user_ans = st.session_state.quiz_answers.get(i)
                correct_ans = q["correct"]
                is_correct = user_ans == correct_ans
                
                status_icon = "✅" if is_correct else "❌"
                st.markdown(f"**{status_icon} Q{i+1}: {q['question']}**")
                
                if is_correct:
                    st.success(f"Your answer: **{user_ans}** ✓")
                else:
                    st.error(f"Your answer: **{user_ans if user_ans else 'Not answered'}** | Correct: **{correct_ans}**")
                
                if "explanation" in q:
                    st.info(f"💡 {q['explanation']}")
                st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Retake Quiz", key="retake_quiz", use_container_width=True):
                st.session_state.quiz_started = False
                st.session_state.quiz_current_q = 0
                st.session_state.quiz_answers = {}
                st.session_state.quiz_completed = False
                st.session_state.quiz_score = 0
                st.rerun()
        with col2:
            if st.button("✅ Continue Learning", key="continue_learning", use_container_width=True):
                st.session_state.quiz_mode = False
                st.session_state.quiz_started = False
                st.session_state.quiz_current_q = 0
                st.session_state.quiz_answers = {}
                st.session_state.quiz_completed = False
                st.rerun()
        return
    
    # Start quiz screen
    if not st.session_state.quiz_started:
        st.markdown("### 🧠 Knowledge Assessment")
        st.markdown(f"**Topic:** {quiz_topic}")
        
        st.divider()
        
        # Proctored mode warning box
        st.error("🔒 **PROCTORED MODE**")
        
        st.warning("""
        **⚠️ Important Rules - Read Carefully:**
        
        1. 🖥️ Quiz will request **full-screen mode**
        2. 🚫 **DO NOT** switch tabs or open other apps
        3. 🚫 **DO NOT** minimize or leave this window
        4. 🚫 **DO NOT** click outside the browser
        5. ⚡ Quiz will **automatically terminate** on any violation
        6. 📱 Keep your focus on this screen only
        
        **Violations will immediately end your quiz!**
        """)
        
        st.info(f"📝 **{len(questions)} questions** • Proctored Environment")
        
        st.divider()
        
        if st.button("🚀 Start Proctored Quiz", key="start_quiz", use_container_width=True, type="primary"):
            st.session_state.quiz_started = True
            st.rerun()
        
        if st.button("🔙 Go Back", key="go_back_quiz"):
            st.session_state.quiz_mode = False
            st.rerun()
        return
    
    # ACTIVE QUIZ MODE
    # Inject the proctoring script when quiz is active
    st.components.v1.html(proctoring_script + """
        <script>
            window.quizInProgress = true;
            // Request fullscreen on the parent document
            try {
                if (window.parent.document.documentElement.requestFullscreen) {
                    window.parent.document.documentElement.requestFullscreen().catch(e => console.log('Fullscreen request:', e));
                }
            } catch(e) {
                console.log('Fullscreen not available:', e);
            }
        </script>
        <div style="background: linear-gradient(90deg, #ef4444, #dc2626); color: white; padding: 8px 16px; border-radius: 20px; display: inline-flex; align-items: center; gap: 8px; font-weight: 600; font-size: 14px; animation: pulse 2s infinite;">
            <span style="width: 10px; height: 10px; background: white; border-radius: 50%; animation: blink 1s infinite;"></span>
            PROCTORED - DO NOT LEAVE THIS PAGE
        </div>
        <style>
            @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.8; } }
            @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
        </style>
    """, height=50)
    
    # Quiz UI
    current_q = st.session_state.quiz_current_q
    total_q = len(questions)
    question = questions[current_q]
    
    # Progress
    st.progress((current_q) / total_q)
    st.markdown(f"**Question {current_q + 1} of {total_q}**")
    
    st.divider()
    
    # Question
    st.markdown(f"### Q{current_q + 1}: {question['question']}")
    
    st.markdown("")
    
    # Options as radio buttons for better UX
    options_list = [f"{k}: {v}" for k, v in question['options'].items()]
    option_keys = list(question['options'].keys())
    
    # Get current selection
    current_selection = st.session_state.quiz_answers.get(current_q)
    default_index = option_keys.index(current_selection) if current_selection in option_keys else 0
    
    selected_option = st.radio(
        "Select your answer:",
        options_list,
        index=default_index if current_selection else None,
        key=f"radio_{current_q}"
    )
    
    # Store the answer
    if selected_option:
        selected_key = selected_option.split(":")[0]
        st.session_state.quiz_answers[current_q] = selected_key
    
    st.divider()
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if current_q > 0:
            if st.button("⬅️ Previous", key="prev_q", use_container_width=True):
                st.session_state.quiz_current_q -= 1
                st.rerun()
    
    with col2:
        # Show answered count
        answered = len([a for a in st.session_state.quiz_answers.values() if a])
        st.markdown(f"**{answered}/{total_q} answered**")
    
    with col3:
        if current_q < total_q - 1:
            if st.button("Next ➡️", key="next_q", use_container_width=True):
                st.session_state.quiz_current_q += 1
                st.rerun()
        else:
            if st.button("✅ Submit Quiz", key="submit_quiz", use_container_width=True, type="primary"):
                # Calculate score
                score = 0
                for i, q in enumerate(questions):
                    if st.session_state.quiz_answers.get(i) == q["correct"]:
                        score += 1
                st.session_state.quiz_score = score
                st.session_state.quiz_completed = True
                st.rerun()


def display_quiz_button(topic):
    """Display a button to start the knowledge quiz for a topic."""
    st.markdown("---")
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)); 
                border-radius: 16px; padding: 1.5rem; border: 1px solid rgba(102, 126, 234, 0.2); margin: 1rem 0;">
        <h4 style="margin: 0;">🧠 Test Your Knowledge</h4>
        <p style="color: #888; margin: 0.5rem 0;">Ready to prove your skills? Take a proctored quiz on this topic!</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📝 Take Knowledge Quiz", key=f"quiz_btn_{topic[:20]}", use_container_width=True):
        st.session_state.quiz_mode = True
        st.session_state.quiz_topic = topic
        st.session_state.quiz_questions = None
        st.rerun()


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
if "quiz_mode" not in st.session_state:
    st.session_state.quiz_mode = False
if "quiz_topic" not in st.session_state:
    st.session_state.quiz_topic = None
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = None

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
        
        col1, col2 = st.columns([2, 1])
        with col1:
            if st.button("✅ Mark Step as Completed", key="skill_display_btn"):
                st.session_state.skill_up_index += 1
                st.rerun()
        with col2:
            if st.button("📝 Test Knowledge", key="skill_quiz_btn"):
                st.session_state.quiz_mode = True
                st.session_state.quiz_topic = st.session_state.skill_up_steps[ind]
                st.session_state.quiz_questions = None
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

        col1, col2 = st.columns([2, 1])
        with col1:
            if st.button("✅ Mark Step as Completed", key="foundation_display_btn"):
                st.session_state.foundation_index += 1
                st.rerun()
        with col2:
            if st.button("📝 Test Knowledge", key="foundation_quiz_btn"):
                st.session_state.quiz_mode = True
                st.session_state.quiz_topic = st.session_state.foundation_steps[ind]
                st.session_state.quiz_questions = None
                st.rerun()
    else:
        st.success("🎉 Foundation level complete! Advancing to Skill Up Phase...")
        st.session_state.current_mode = "skill_up"
        del st.session_state.foundation_steps
        del st.session_state.foundation_index
        time.sleep(1)
        st.rerun()

# Check if quiz mode is active
if st.session_state.quiz_mode and st.session_state.quiz_topic:
    st.markdown("### 🧠 Knowledge Quiz")
    
    # Generate questions if not already done
    if st.session_state.quiz_questions is None:
        with st.spinner("🧠 Generating quiz questions..."):
            questions = generate_quiz_questions(st.session_state.quiz_topic, num_questions=5)
            if questions:
                st.session_state.quiz_questions = questions
                st.rerun()
            else:
                st.error("Failed to generate quiz. Please try again.")
                if st.button("🔙 Go Back"):
                    st.session_state.quiz_mode = False
                    st.rerun()
    else:
        render_proctored_quiz(st.session_state.quiz_questions, st.session_state.quiz_topic)

# Check if we have an active learning path
elif st.session_state.current_mode == "skill_up" and "skill_up_steps" in st.session_state:
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

