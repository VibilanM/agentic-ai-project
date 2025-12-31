import streamlit as st
from pypdf import PdfReader
from supabase import create_client
import requests
import json
import time
import re

st.set_page_config(
    page_title="Snellire",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]
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

openrouter_key = st.secrets["OPENROUTER_KEY"]
headers_openrouter = {
    "Authorization": f"Bearer {openrouter_key}",
    "Content-Type": "application/json"
}

def check_username_exists(username):
    try:
        response = supabase.table("user_progress").select("username").eq("username", username).execute()
        return len(response.data) > 0
    except Exception as e:
        st.error(f"Error checking username: {e}")
        return False

def create_new_user(username, password):
    try:
        response = supabase.table("user_progress").insert({"username": username, "password": password}).execute()
        return len(response.data) > 0
    except Exception as e:
        st.error(f"Error creating user: {e}")
        return False

def verify_user_credentials(username, password):
    try:
        response = supabase.table("user_progress").select("*").eq("username", username).eq("password", password).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        st.error(f"Error verifying credentials: {e}")
        return None

def load_user_progress(username):
    try:
        response = supabase.table("user_progress").select("*").eq("username", username).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        st.error(f"Error loading progress: {e}")
        return None

def save_user_progress():
    if "username" not in st.session_state or not st.session_state.username:
        return
    
    try:
        update_data = {
            "current_mode": st.session_state.get("current_mode"),
            "chances_percentage": st.session_state.get("chances_percentage", 0),
            "current_skills": st.session_state.get("current_skills", []),
            "missing_skills": st.session_state.get("missing_skills", []),
            "foundation_steps": st.session_state.get("foundation_steps", []),
            "foundation_index": st.session_state.get("foundation_index", 0),
            "skill_up_steps": st.session_state.get("skill_up_steps", []),
            "skill_up_index": st.session_state.get("skill_up_index", 0),
            "resume_text": st.session_state.get("resume_text"),
            "expectation_text": st.session_state.get("expectation_text")
        }
        
        supabase.table("user_progress").update(update_data).eq("username", st.session_state.username).execute()
    except Exception as e:
        st.error(f"Error saving progress: {e}")

def restore_session_from_data(data):
    st.session_state.current_mode = data.get("current_mode")
    st.session_state.chances_percentage = data.get("chances_percentage", 0)
    st.session_state.current_skills = data.get("current_skills", [])
    st.session_state.missing_skills = data.get("missing_skills", [])
    st.session_state.resume_text = data.get("resume_text")
    st.session_state.expectation_text = data.get("expectation_text")
    
    if data.get("foundation_steps"):
        st.session_state.foundation_steps = data.get("foundation_steps", [])
        st.session_state.foundation_index = data.get("foundation_index", 0)
    
    if data.get("skill_up_steps"):
        st.session_state.skill_up_steps = data.get("skill_up_steps", [])
        st.session_state.skill_up_index = data.get("skill_up_index", 0)
    
    if st.session_state.current_mode:
        st.session_state.analysis_data = {
            "chances_percentage": data.get("chances_percentage", 0),
            "current_skills": data.get("current_skills", []),
            "missing_skills": data.get("missing_skills", [])
        }

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    return text

def api_request_with_retry(messages, system_content=None, max_retries=3):
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
                wait_time = (2 ** attempt) * 2
                st.warning(f"Rate limited. Waiting {wait_time} seconds before retry ({attempt + 1}/{max_retries})...")
                time.sleep(wait_time)
                continue
            else:
                return response
                
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2)
    
    return response

def extract_json(text):
    if not text:
        return None
    
    try:
        code_block_pattern = r'```(?:json)?\s*(\{[\s\S]*?\})\s*```'
        match = re.search(code_block_pattern, text)
        if match:
            return json.loads(match.group(1))
        
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            json_str = text[start:end]
            json_str = json_str.replace('\n', ' ').replace('\r', '')
            return json.loads(json_str)
        
        return None
    except json.JSONDecodeError:
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                json_str = text[start:end]
                json_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_str)
                return json.loads(json_str)
        except:
            pass
        return None
    except Exception:
        return None

def display_skills(skills, skill_type="current"):
    if not skills:
        st.write("_No skills identified_")
        return
    
    if skill_type == "current":
        st.markdown("##### Current Skills")
        for skill in skills:
            st.success(skill)
    else:
        st.markdown("##### Skills to Improve")
        for skill in skills:
            st.warning(skill)


def job_search(data):
    sc3 = """You are a job-search advisory agent in a multi-agent career system.

    The user has the required skills for their target role and is ready to apply.
    Your task is to help the user successfully search and apply for jobs.

    BEFORE providing advice, you must first analyze:
    - Current market demand for the target role
    - Common challenges job seekers face in this field
    - Industry trends affecting hiring for this position
    - Typical competition level and what makes candidates stand out
    - Any specific requirements or preferences employers commonly have

    Your response MUST be a clear, human-readable explanation.

    Structure your response in FOUR clearly separated sections:

    1. Market Overview
    - Briefly describe the current job market for this role
    - Mention key challenges and what employers are looking for
    - Highlight any trends or insights that will help the user

    2. Job Platforms  
    - List the best platforms for the target role in the order of whichever platform has the highest chance of getting the user a job.

    3. Search Keywords & Filters  
    - Provide exact search keywords the user can paste into job platforms.
    - Suggest useful filters (experience level, location, role type).

    4. Resume & Application Tips  
    - Suggest specific resume improvements or bullet rewrites based on market expectations.
    - Give practical tips to make applications stand out against competition.
    - Keep everything copy-paste friendly.

    Rules:
    - Be practical and specific based on current market realities.
    - Do NOT include motivational or generic advice.
    - Do NOT mention percentages or evaluations.
    - Do NOT suggest further learning steps.
    - Assume the user will act immediately after reading this.
    """

    with st.spinner("Finding relevant jobs..."):
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
        st.success("You are ready to apply! Here is your strategy:")
        st.markdown(content)
    else:
        st.error(f"Error fetching job search strategy: {ai_response4.status_code}")

def skill_up(data):
    if "foundation_steps" in st.session_state:
        del st.session_state.foundation_steps
        del st.session_state.foundation_index

    sc2 = """You are a skill-upgrading agent in a multi-agent career system.

    The user has basic foundations but is not yet job-ready.
    Your task is to design an intermediate-level learning path to upgrade the user's skills.

    STRICT RULES:
    - Output ONLY valid JSON.
    - NO explanations, NO markdown formatting, NO code blocks.
    - Just raw JSON starting with { and ending with }

    Required JSON Schema:
    {
        "steps": [
            {
                "title": "Step title here",
                "description": "A detailed explanation of what the user should do in this step, including specific resources, techniques, or actions to take. This should be 2-4 sentences explaining the step clearly.",
                "resources": ["Optional list of specific resources, courses, or tools to use"]
            }
        ],
        "chances_percentage": 60,
        "current_skills": ["skill1", "skill2"]
    }

    IMPORTANT: Each step must be a complete, actionable learning task with a clear title and detailed description. Do NOT use bullet points or one-liners. Each step should explain WHAT to do and HOW to do it.
    """
    
    with st.spinner("Generating skill-up plan..."):
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
        save_user_progress()

    ind = st.session_state.skill_up_index
    total = len(st.session_state.skill_up_steps)
    
    st.header("Skill Up Plan")
    if total > 0:
        st.progress(ind / total if total > 0 else 0)
        st.write(f"**Progress:** {ind}/{total} steps completed")

    if ind < total:
        current_step = st.session_state.skill_up_steps[ind]
        
        if isinstance(current_step, dict):
            step_title = current_step.get("title", f"Step {ind+1}")
            step_description = current_step.get("description", "")
            step_resources = current_step.get("resources", [])
        else:
            step_title = f"Step {ind+1}"
            step_description = current_step
            step_resources = []
        
        st.subheader(f"Step {ind+1} of {total}: {step_title}")
        st.write(step_description)
        
        if step_resources:
            st.markdown("**Resources:**")
            for resource in step_resources:
                st.write(f"- {resource}")
        
        if st.button("I Completed This Step", key="skill_btn_complete", use_container_width=True):
            st.session_state.skill_up_index += 1
            save_user_progress()
            st.rerun()
    else:
        st.balloons()
        st.success("Skill Up level complete! Time to Search Jobs!")
        st.session_state.current_mode = "job_search"
        save_user_progress()
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
    {
        "steps": [
            {
                "title": "Step title here",
                "description": "A detailed explanation of what the user should do in this step, including specific resources, techniques, or actions to take. This should be 2-4 sentences explaining the step clearly.",
                "resources": ["Optional list of specific resources, courses, or tools to use"]
            }
        ],
        "chances_percentage": 30,
        "current_skills": ["skill1"],
        "missing_skills": ["skill1", "skill2"]
    }

    IMPORTANT: Each step must be a complete, actionable learning task with a clear title and detailed description. Do NOT use bullet points or one-liners. Each step should explain WHAT to do and HOW to do it.
    """
    
    with st.spinner("Generating foundation plan..."):
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
        save_user_progress()

    ind = st.session_state.foundation_index
    total = len(st.session_state.foundation_steps)

    st.header("Foundation Plan")
    if total > 0:
        st.progress(ind / total if total > 0 else 0)
        st.write(f"**Progress:** {ind}/{total} steps completed")

    if ind < total:
        current_step = st.session_state.foundation_steps[ind]
        
        if isinstance(current_step, dict):
            step_title = current_step.get("title", f"Step {ind+1}")
            step_description = current_step.get("description", "")
            step_resources = current_step.get("resources", [])
        else:
            step_title = f"Step {ind+1}"
            step_description = current_step
            step_resources = []
        
        st.subheader(f"Step {ind+1} of {total}: {step_title}")
        st.write(step_description)
        
        if step_resources:
            st.markdown("**Resources:**")
            for resource in step_resources:
                st.write(f"- {resource}")

        if st.button("I Completed This Step", key="foundation_btn_complete", use_container_width=True):
            st.session_state.foundation_index += 1
            save_user_progress()
            st.rerun()

    else:
        st.success("Foundation level complete! Advancing to Skill Up Phase...")
        st.session_state.current_mode = "skill_up"
        save_user_progress()
        time.sleep(2)
        skill_up(data)

def decide_mode(ai_response1):
    try:
        data = json.loads(ai_response1) if isinstance(ai_response1, str) else ai_response1
    except json.JSONDecodeError:
        st.error("Could not parse analysis results.")
        return

    st.session_state.analysis_data = data
    st.session_state.chances_percentage = data.get("chances_percentage", 0)
    st.session_state.current_skills = data.get("current_skills", [])
    st.session_state.missing_skills = data.get("missing_skills", [])
    
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
        st.info("Starting Foundation Path - Let's build your skills from the ground up!")
        st.session_state.current_mode = "foundation"
        save_user_progress()
        foundation(data)
    elif chances < 80:
        st.info("Starting Skill-Up Path - Time to level up your existing skills!")
        st.session_state.current_mode = "skill_up"
        save_user_progress()
        skill_up(data)
    else:
        st.success("You are Job Ready! Let's find you the perfect opportunity!")
        st.session_state.current_mode = "job_search"
        save_user_progress()
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
    
    with st.spinner("Analyzing your resume..."):
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
    
    st.header("Analysis Result")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.metric(label="Match Probability", value=f"{chances}%")
        st.progress(chances / 100)

    if "missing_skills" not in data:
        data["missing_skills"] = []
    
    return json.dumps(data)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "current_mode" not in st.session_state:
    st.session_state.current_mode = None
if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None
if "resume_text" not in st.session_state:
    st.session_state.resume_text = None
if "expectation_text" not in st.session_state:
    st.session_state.expectation_text = None

st.title("SNELLIRE")
st.caption("Your AI-powered partner for career growth")

st.divider()

if not st.session_state.authenticated:
    st.header("Welcome")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("New User (Sign Up)", use_container_width=True):
            st.session_state.auth_mode = "signup"
            st.rerun()
    
    with col2:
        if st.button("Existing User (Sign In)", use_container_width=True):
            st.session_state.auth_mode = "signin"
            st.rerun()
    
    if "auth_mode" in st.session_state:
        st.divider()
        
        if st.session_state.auth_mode == "signup":
            st.subheader("Create New Account")
            new_username = st.text_input("Enter a unique username", key="new_username_input")
            new_password = st.text_input("Enter a password (min 8 characters)", type="password", key="new_password_input")
            
            username_available = False
            password_valid = False
            
            if new_username:
                if check_username_exists(new_username):
                    st.error("Username already taken. Please choose another.")
                else:
                    st.success("Username is available!")
                    username_available = True
            
            if new_password:
                if len(new_password) < 8:
                    st.error("Password must be at least 8 characters.")
                else:
                    password_valid = True
            
            can_signup = username_available and password_valid
            signup_btn = st.button("Sign Up", disabled=not can_signup, use_container_width=True)
            
            if signup_btn and can_signup:
                if create_new_user(new_username, new_password):
                    st.session_state.authenticated = True
                    st.session_state.username = new_username
                    st.success("Account created successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Failed to create account. Please try again.")
        
        elif st.session_state.auth_mode == "signin":
            st.subheader("Sign In")
            existing_username = st.text_input("Enter your username", key="existing_username_input")
            existing_password = st.text_input("Enter your password", type="password", key="existing_password_input")
            
            can_signin = bool(existing_username and existing_password)
            signin_btn = st.button("Sign In", disabled=not can_signin, use_container_width=True)
            
            if signin_btn and can_signin:
                user_data = verify_user_credentials(existing_username, existing_password)
                if user_data:
                    st.session_state.authenticated = True
                    st.session_state.username = existing_username
                    restore_session_from_data(user_data)
                    st.success("Welcome back!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid username or password. Please try again.")

else:
    st.write(f"Signed in as: **{st.session_state.username}**")
    
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("Sign Out"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    st.divider()
    
    def display_skill_up_ui():
        if "skill_up_steps" not in st.session_state:
            return
        
        ind = st.session_state.skill_up_index
        total = len(st.session_state.skill_up_steps)
        
        st.header("Skill Up Plan")
        if total > 0:
            st.progress(ind / total if total > 0 else 0)
            st.write(f"**Progress:** {ind}/{total} steps completed")

        if ind < total:
            current_step = st.session_state.skill_up_steps[ind]
            
            if isinstance(current_step, dict):
                step_title = current_step.get("title", f"Step {ind+1}")
                step_description = current_step.get("description", "")
                step_resources = current_step.get("resources", [])
            else:
                step_title = f"Step {ind+1}"
                step_description = current_step
                step_resources = []
            
            st.subheader(f"Step {ind+1} of {total}: {step_title}")
            st.write(step_description)
            
            if step_resources:
                st.markdown("**Resources:**")
                for resource in step_resources:
                    st.write(f"- {resource}")
            
            if st.button("I Completed This Step", key="skill_display_btn", use_container_width=True):
                st.session_state.skill_up_index += 1
                save_user_progress()
                st.rerun()
        else:
            st.balloons()
            st.success("Skill Up level complete! Time to Search Jobs!")
            st.session_state.current_mode = "job_search"
            save_user_progress()
            time.sleep(1)
            st.rerun()

    def display_foundation_ui():
        if "foundation_steps" not in st.session_state:
            return
        
        ind = st.session_state.foundation_index
        total = len(st.session_state.foundation_steps)

        st.header("Foundation Plan")
        if total > 0:
            st.progress(ind / total if total > 0 else 0)
            st.write(f"**Progress:** {ind}/{total} steps completed")

        if ind < total:
            current_step = st.session_state.foundation_steps[ind]
            
            if isinstance(current_step, dict):
                step_title = current_step.get("title", f"Step {ind+1}")
                step_description = current_step.get("description", "")
                step_resources = current_step.get("resources", [])
            else:
                step_title = f"Step {ind+1}"
                step_description = current_step
                step_resources = []
            
            st.subheader(f"Step {ind+1} of {total}: {step_title}")
            st.write(step_description)
            
            if step_resources:
                st.markdown("**Resources:**")
                for resource in step_resources:
                    st.write(f"- {resource}")

            if st.button("I Completed This Step", key="foundation_display_btn", use_container_width=True):
                st.session_state.foundation_index += 1
                save_user_progress()
                st.rerun()
        else:
            st.success("Foundation level complete! Advancing to Skill Up Phase...")
            st.session_state.current_mode = "skill_up"
            del st.session_state.foundation_steps
            del st.session_state.foundation_index
            save_user_progress()
            time.sleep(1)
            st.rerun()

    if st.session_state.current_mode is not None:
        if st.button("Start New Analysis", use_container_width=False):
            for key in ["skill_up_steps", "skill_up_index", "foundation_steps", "foundation_index", 
                        "current_mode", "analysis_data", "resume_text", "expectation_text",
                        "chances_percentage", "current_skills", "missing_skills"]:
                if key in st.session_state:
                    del st.session_state[key]
            save_user_progress()
            st.rerun()
        
        st.divider()
        
        if st.session_state.current_mode == "skill_up" and "skill_up_steps" in st.session_state:
            display_skill_up_ui()
        
        elif st.session_state.current_mode == "foundation" and "foundation_steps" in st.session_state:
            display_foundation_ui()
        
        elif st.session_state.current_mode == "job_search":
            resume = st.session_state.resume_text
            expectation = st.session_state.expectation_text
            job_search(st.session_state.analysis_data)
        
        elif st.session_state.current_mode == "skill_up":
            resume = st.session_state.resume_text
            expectation = st.session_state.expectation_text
            skill_up(st.session_state.analysis_data)
        
        elif st.session_state.current_mode == "foundation":
            resume = st.session_state.resume_text
            expectation = st.session_state.expectation_text
            foundation(st.session_state.analysis_data)

    else:
        st.header("Get Started")
        st.info("Upload your resume and define your target role to receive a personalized career plan.")
        
        file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
        expectation = st.text_area("Target Role / Goal", height=150, placeholder="e.g. Senior Python Developer at a Tech Startup...")
        
        st.write("")
        analyze_btn = st.button("Analyze Profile", use_container_width=True)
        
        if file is not None and expectation:
            try:
                resume = extract_text_from_pdf(file)
                
                with st.expander("View Extracted Resume Text"):
                    st.text(resume)
                    
                if analyze_btn:
                    st.session_state.resume_text = resume
                    st.session_state.expectation_text = expectation
                    
                    for key in ["skill_up_steps", "skill_up_index", "foundation_steps", "foundation_index"]:
                        if key in st.session_state:
                            del st.session_state[key]
                    
                    save_user_progress()
                    analysis = resume_analysis(resume, expectation)
                    if analysis:
                        decide_mode(analysis)
                        
            except Exception as e:
                st.error(f"Error reading file: {e}")
        
        elif analyze_btn:
            st.error("Please upload a resume and enter a goal.")
        else:
            st.divider()
            st.header("How it works:")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("Upload Resume")
                st.write("Upload your PDF resume above")
            
            with col2:
                st.subheader("Set Your Goal")
                st.write("Tell us what job you want to land")
            
            with col3:
                st.subheader("Get Your Plan")
                st.write("Receive a personalized career roadmap")
