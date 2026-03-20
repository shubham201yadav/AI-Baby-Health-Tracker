import streamlit as st
import requests
import random
import pandas as pd
from streamlit.components.v1 import html
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(
    page_title="👶 Baby Tracker AI",
    layout="wide",
    page_icon="🍼",
    initial_sidebar_state="expanded"
)

# --- SESSION STATE ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "selected_feature" not in st.session_state:
    st.session_state.selected_feature = None
if "selected_age" not in st.session_state:
    st.session_state.selected_age = 1
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_data" not in st.session_state:
    st.session_state.user_data = {}
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# --- LOGIN/SIGNUP SYSTEM ---
def signup():
    st.markdown("<h1 style='text-align:center; color:#00FF00; font-size:40px;'>🤖 Create New BabyBot Account</h1>", unsafe_allow_html=True)
    username = st.text_input("Enter a Username", key="signup_user")
    password = st.text_input("Enter a Password", type="password", key="signup_pass")
    if st.button("Create Account 🚀"):
        if username and password:
            st.session_state.user_data[username] = password
            st.success("✅ Account created! Please Login now.")
            st.session_state.signup = False
        else:
            st.error("❌ Please fill in both fields.")

def login():
    st.markdown("<h1 style='text-align:center; color:#00BFFF; font-size:40px;'>🤖 Login to BabyBot</h1>", unsafe_allow_html=True)
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")
    if st.button("Login 🔒"):
        if username in st.session_state.user_data and st.session_state.user_data[username] == password:
            st.success("✅ Login Successful! Loading BabyBot...")
            st.session_state.authenticated = True
        else:
            st.error("❌ Incorrect Username or Password.")

def login_signup_page():
    st.markdown("""
        <style>
            body { background-color: #0d0d0d; }
            .stTextInput > div > div > input {
                background-color: #1a1a1a;
                color: #00FF00;
                font-size: 20px;
            }
            .stButton>button {
                background-color: #333;
                color: #00FF00;
                font-size: 22px;
                border-radius: 8px;
                height: 3em;
                width: 100%;
            }
            .stButton>button:hover {
                background-color: #00FF00;
                color: black;
            }
            .stMarkdown p {
                color: white;
                font-size: 22px;
            }
        </style>
    """, unsafe_allow_html=True)

    if "signup" not in st.session_state:
        st.session_state.signup = False

    if st.session_state.signup:
        signup()
    else:
        login()

    st.markdown("---")
    if not st.session_state.signup:
        if st.button("Need to create account? ➡️ Signup"):
            st.session_state.signup = True
    else:
        if st.button("Already have account? ➡️ Login"):
            st.session_state.signup = False

# --- CALL GEMINI FUNCTION ---
GOOGLE_API_KEY = "AIzaSyAzfSxkYvHce0fX5npLTO9FDweM2kup0eo"
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={GOOGLE_API_KEY}"

def call_gemini(user_prompt):
    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [{"parts": [{"text": user_prompt}]}],
        "generationConfig": {"temperature": 0.7, "topP": 0.95, "maxOutputTokens": 1024}
    }
    try:
        response = requests.post(GEMINI_ENDPOINT, headers=headers, json=body)
        response.raise_for_status()
        result = response.json()
        if "candidates" in result and result["candidates"]:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return "❌ No valid response received from Gemini AI."
    except requests.exceptions.RequestException as e:
        return f"❌ Error: {e}"

# --- GROWTH CHART FUNCTION ---
def show_growth_chart(age):
    months = [f"{i} yr" for i in range(1, 6)]
    height = [75 + random.randint(0, 5) + i * 5 for i in range(5)]
    weight = [10 + random.uniform(1.5, 2.5) * i for i in range(5)]
    df = pd.DataFrame({"Age": months, "Height (cm)": height, "Weight (kg)": weight})
    st.markdown("""
    <div style="background:linear-gradient(135deg,#f5f7fa 0%,#c3cfe2 100%);
                padding:15px;
                border-radius:12px;
                margin-bottom:20px;">
        <h3 style="color:#333;text-align:center;">📊 Growth Tracker Chart</h3>
    </div>
    """, unsafe_allow_html=True)
    st.line_chart(df.set_index("Age"))

# --- NEW FEATURES ---
def vaccine_schedule():
    st.markdown("### 💉 Vaccine Schedule")
    st.markdown("""Here's a general recommended vaccine timeline. Please consult your pediatrician for personalized advice.""")
    st.table({"Age": ["Birth", "2 months", "4 months", "6 months", "12 months", "18 months"],
              "Vaccines": ["HepB", "DTaP, IPV, Hib, PCV, RV", "DTaP, IPV, Hib, PCV, RV", "DTaP, IPV, Hib, PCV, RV", "MMR, Varicella, HepA", "DTaP, IPV"]})

def parenting_tips():
    st.markdown("### 🧠 Parenting Tips")
    tips = call_gemini("Give me essential parenting tips for early childhood care.")
    st.write(tips)

def food_recipes():
    st.markdown("### 🍲 Baby Food Recipes")
    recipes = call_gemini("Give me some healthy and simple baby food recipes by age.")
    st.write(recipes)

def photo_album():
    st.markdown("### 📸 Upload Baby Photos")
    uploaded_files = st.file_uploader("Upload your baby photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
    if uploaded_files:
        for photo in uploaded_files:
            st.image(photo, caption=photo.name, use_column_width=True)

def baby_notes():
    st.markdown("### 📝 Baby Notes / Journal")
    note = st.text_area("Write your notes or baby updates here")
    if st.button("Save Note"):
        st.success("📝 Note saved locally (session-based only).")

# --- FEATURE EXECUTION ---
def run_feature(feature):
    age = st.session_state.selected_age
    prompts = {
        "Feeding": f"Suggest a feeding schedule for a {age}-year-old baby and give tips for healthy baby nutrition.",
        "Sleep": f"Provide a sleep routine for a {age}-year-old baby including nap time and bedtime advice.",
        "Growth": f"Provide the average height and weight for a {age}-year-old child and explain using a chart format.",
        "Routine": f"Give a full daily routine for a {age}-year-old baby including meals, playtime, sleep, and learning.",
        "Milestones": f"What developmental milestones should a {age}-year-old baby be achieving?",
        "Clothes": f"When and how often should a {age}-year-old baby change clothes? Include situations like playtime, spills, or temperature.",
    }
    if feature in prompts:
        with st.spinner("✨ Crafting the perfect response..."):
            reply = call_gemini(prompts[feature])
        st.session_state.chat_history.append({"role": "assistant", "text": reply})
        if feature == "Growth":
            show_growth_chart(age)

# --- MAIN APP ---
if not st.session_state.authenticated:
    login_signup_page()
else:
    st.markdown("<style> body { background-color: #0f0f0f; } </style>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>🤖 BabyBot AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>The smartest way to track your baby's growth and development</p>", unsafe_allow_html=True)

    # Theme toggle
    if st.sidebar.toggle("🌗 Toggle Theme"):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

    # Age and tools
    routine_age = st.selectbox("🗓️ Select Age for Full-Day Schedule", [1, 2, 3, 4, 5], key="routine_age")
    if st.button("⚡ Generate Daily Routine Table", key="routine_gen"):
        prompt = f"Make a clear 24-hour schedule in table format for a {routine_age}-year-old baby. Include times, activities, and short descriptions."
        with st.spinner("🧠 Creating structured schedule..."):
            routine_reply = call_gemini(prompt)
        st.markdown("#### 🗓️ Baby Daily Schedule (Table Format)")
        st.markdown(routine_reply, unsafe_allow_html=True)

    with st.sidebar:
        if st.button("🧹 Clear Chat History"):
            st.session_state.chat_history = []
        st.markdown("### 👶 Baby's Age")
        cols = st.columns(5)
        ages = {1: "🐣", 2: "👶", 3: "🧒", 4: "👦", 5: "🧑"}
        for age, emoji in ages.items():
            if cols[age-1].button(f"{age} {emoji}", key=f"age_{age}"):
                st.session_state.selected_age = age
        st.markdown("### 🛠️ Tools")
        tools = {
            "🍼 Feeding Guide": "Feeding",
            "😴 Sleep Wizard": "Sleep",
            "📈 Growth Tracker": "Growth",
            "📆 Routine Maker": "Routine",
            "🏆 Milestones": "Milestones",
            "👕 Clothing Tips": "Clothes",
            "💉 Vaccine Schedule": vaccine_schedule,
            "🧠 Parenting Tips": parenting_tips,
            "🍲 Baby Food Recipes": food_recipes,
            "📸 Baby Photo Album": photo_album,
            "📝 Baby Journal": baby_notes,
        }
        for btn_text, func in tools.items():
            if isinstance(func, str):
                if st.button(btn_text):
                    st.session_state.selected_feature = func
            else:
                if st.button(btn_text):
                    func()

    # Chat
    if st.session_state.selected_feature:
        run_feature(st.session_state.selected_feature)
        st.session_state.selected_feature = None

    user_input = st.chat_input("Ask BabyBot anything...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "text": user_input})
        with st.spinner("💭 Thinking deeply..."):
            response = call_gemini(user_input)
        st.session_state.chat_history.append({"role": "assistant", "text": response})

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="🧑"):
                st.markdown(msg["text"])
        else:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(msg["text"])

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center;padding:20px;color:#666;">
        <p>Built with 💙 using <a href="https://ai.google.dev/" target="_blank">Google Gemini AI</a></p>
        <p style="font-size:12px;">© 2023 BabyBot - Making parenting easier</p>
    </div>
    """, unsafe_allow_html=True)

    html(""" ... YOUR FLOATING EMOJI CODE ... """)
