import streamlit as st
import time, json, os
from hashlib import sha256
from chatbot import Chatbot
from engines.simple_faq import SimpleFAQEngine
from engines.rag_engine import RagEngine
import re

# --- Page Config ---
st.set_page_config(page_title="Student Assistant Chatbot", layout="wide")

from utils import setup_environment
setup_environment()  # Must be first thing in app.py

# --- Initialize Session State ---
for key, val in {
    "logged_in": False,
    "username": None,
    "role": None,
    "page": "login",
    "messages": [],
    "session_id": None,
    "chatbot": None,
    "model": "Simple FAQ",
    "rag_engine": None,
    "documents_uploaded": False,
    "uploaded_pdf_files": [],
    "processed_pdf_names": []  # NEW: Track which PDFs have been processed
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- File Paths ---
USERS_FILE = "users.json"
ADMINS_FILE = "credentials.json"

# --- Utility Functions ---
def load_data(file):
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump({}, f)
    with open(file, "r") as f:
        return json.load(f)

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def hash_password(password):
    return sha256(password.encode()).hexdigest()

# --- User and Bot Avatars ---
AVATARS = {
    "Default User": "assets/avatars/def.png",
    "Male Student": "assets/avatars/male.png",
    "Female Student": "assets/avatars/female.png",
    "Teacher": "assets/avatars/teacher.png"
}
BOT_AVATARS = {
    "Male Lilo": "assets/bot_avatars/male.png",
    "Female Lilo": "assets/bot_avatars/female.png"
}

# =====================================================
# CHATBOT INITIALIZATION
# =====================================================
def initialize_chatbot(model_name: str) -> Chatbot:
    """
    Initialize the appropriate chatbot engine based on model selection.
    
    Args:
        model_name: The selected model ("Simple FAQ" or "RAG")
        
    Returns:
        Chatbot instance with the selected engine
    """
    if model_name == "Simple FAQ":
        engine = SimpleFAQEngine()
    elif model_name == "RAG":
        # Initialize RAG engine (PDFs must be uploaded separately)
        if st.session_state.rag_engine is None:
            st.session_state.rag_engine = RagEngine()
        engine = st.session_state.rag_engine
    else:
        # Default to Simple FAQ
        engine = SimpleFAQEngine()
    
    return Chatbot(engine)

# =====================================================
# LOGIN PAGE
# =====================================================
def login_page():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # Centered and tight buttons layout
    col_space1, col_main, col_space2 = st.columns([2, 1.5, 2])
    with col_main:
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔓 Login", use_container_width=True):
                users = load_data(USERS_FILE)
                admins = load_data(ADMINS_FILE)
                hashed = hash_password(password)

                # Admin check
                if username in admins and admins[username]["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.role = "admin"
                    st.session_state.username = username
                    st.session_state.page = "home"
                    st.session_state.session_id = f"{username}_session"
                    st.success("✅ Logged in as Admin")
                    time.sleep(2)
                    st.rerun()

                # User check
                elif username in users and users[username]["password"] == hashed:
                    st.session_state.logged_in = True
                    st.session_state.role = "user"
                    st.session_state.username = username
                    st.session_state.page = "home"
                    st.session_state.session_id = f"{username}_session"
                    st.success("✅ Logged in as User")
                    time.sleep(2)
                    st.rerun()

                # Invalid credentials
                else:
                    st.error("❌ Invalid username or password")

        with col2:
            if st.button("🆕 Sign Up", use_container_width=True):
                st.session_state.page = "register"
                st.rerun()

# =====================================================
# REGISTER PAGE
# =====================================================
def register_page():
    st.title("📝 Register New User")

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()
    
    # Input fields
    username = st.text_input("Choose a username")
    password = st.text_input("Choose a password", type="password")
    confirm = st.text_input("Confirm password", type="password")

    # Username Validation functions
    def _validate_username(u):
        if not u:
            return False, "Username cannot be empty."
        if len(u) < 3 or len(u) > 30:
            return False, "Username must be between 3 and 30 characters."
        if not re.match(r'^[A-Za-z][A-Za-z0-9_]*$', u):
            return False, "Username must start with a letter and contain only letters, numbers, or underscores."
        reserved = {"admin", "root", "system"}
        if u.lower() in reserved:
            return False, "This username is reserved. Please choose another."
        return True, ""

    # Password Validation functions
    def _validate_password(p, u):
        if not p:
            return False, "Password cannot be empty."
        if len(p) < 8:
            return False, "Password must be at least 8 characters long."
        if len(p) > 128:
            return False, "Password is too long."
        if p.lower() == (u or "").lower():
            return False, "Password cannot be the same as the username."
        has_upper = any(c.isupper() for c in p)
        has_lower = any(c.islower() for c in p)
        has_digit = any(c.isdigit() for c in p)
        has_special = any(not c.isalnum() for c in p)
        missing = []
        if not has_upper: missing.append("uppercase")
        if not has_lower: missing.append("lowercase")
        if not has_digit: missing.append("digit")
        if not has_special: missing.append("special character")
        if missing:
            return False, "Password must include: " + ", ".join(missing) + "."
        common = {"password", "123456", "12345678", "qwerty", "letmein", "password1"}
        if p.lower() in common:
            return False, "Password is too common. Choose a stronger password."
        return True, ""

    if st.button("Register"):
        valid_u, msg_u = _validate_username(username)
        if not valid_u:
            st.error(f"❌ {msg_u}")
            return

        if password != confirm:
            st.error("❌ Passwords do not match.")
            return

        valid_p, msg_p = _validate_password(password, username)
        if not valid_p:
            st.error(f"❌ {msg_p}")
            return

        users = load_data(USERS_FILE)
        admins = load_data(ADMINS_FILE)
        if username in users or username in admins:
            st.error("⚠️ Username already exists. Choose a different username.")
            return

        users[username] = {"password": hash_password(password)}
        save_data(USERS_FILE, users)
        with st.spinner("Finalizing registration..."):
            time.sleep(4)
        st.success("✅ Registration successful! Redirecting to login...")
        time.sleep(4)
        st.session_state.page = "login"
        st.rerun()


def chatbot_interface():
    # =====================================================
    # SIDE BAR INTERFACE
    # =====================================================
    st.sidebar.title("⚙️ Settings")

    # Model Selection - Now Functional with RAG!
    model = st.sidebar.selectbox("Model selection", ["Simple FAQ", "RAG"])
    
    if st.session_state.model != model:
        st.session_state.model = model
        st.session_state.chatbot = initialize_chatbot(model)
        st.session_state.messages = []  # Clear history on model switch
        st.rerun()

    # Show different UI based on model selection
    if st.session_state.model == "RAG":
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📄 RAG Configuration")
        
        # PDF Upload for RAG
        uploaded_files = st.sidebar.file_uploader(
            "Upload PDFs",
            type=["pdf"],
            accept_multiple_files=True,
            key="pdf_uploader"
        )
        
        # Store uploaded files in session state
        if uploaded_files:
            st.session_state.uploaded_pdf_files = uploaded_files
        
        if st.session_state.uploaded_pdf_files:
            st.sidebar.info(f"📄 {len(st.session_state.uploaded_pdf_files)} file(s) ready to process")
            
            # Check if there are new files to process
            new_files = [f for f in st.session_state.uploaded_pdf_files 
                        if f.name not in st.session_state.processed_pdf_names]
            
            if new_files and not st.session_state.documents_uploaded:
                # Show button only if there are unprocessed files
                if st.sidebar.button("📤 Process PDFs", use_container_width=True):
                    with st.spinner("Processing PDFs..."):
                        # Initialize RAG engine if not done
                        if st.session_state.rag_engine is None:
                            st.session_state.rag_engine = RagEngine()
                        
                        # Ingest PDFs
                        result = st.session_state.rag_engine.ingest_pdfs(
                            st.session_state.session_id,
                            st.session_state.uploaded_pdf_files
                        )
                        
                        if result["success"]:
                            st.session_state.documents_uploaded = True
                            # Track which files have been processed
                            st.session_state.processed_pdf_names = [f.name for f in st.session_state.uploaded_pdf_files]
                            st.sidebar.success(result["message"])
                            st.session_state.uploaded_pdf_files = []  # Clear file list
                            st.rerun()
                        else:
                            st.sidebar.error(f"❌ {result.get('error', 'Unknown error')}")
            elif st.session_state.documents_uploaded:
                # Show button only if user adds NEW files
                new_files = [f for f in st.session_state.uploaded_pdf_files 
                            if f.name not in st.session_state.processed_pdf_names]
                
                if new_files:
                    st.sidebar.warning(f"⚠️ {len(new_files)} new file(s) detected")
                    if st.sidebar.button("📤 Process New PDFs", use_container_width=True):
                        with st.spinner("Processing new PDFs..."):
                            result = st.session_state.rag_engine.ingest_pdfs(
                                st.session_state.session_id,
                                new_files
                            )
                            
                            if result["success"]:
                                # Track newly processed files
                                st.session_state.processed_pdf_names.extend([f.name for f in new_files])
                                st.sidebar.success(result["message"])
                                st.rerun()
                            else:
                                st.sidebar.error(f"❌ {result.get('error', 'Unknown error')}")
        
        # Show status
        if st.session_state.documents_uploaded:
            st.sidebar.info("✅ Documents uploaded and ready for questions!")
        else:
            st.sidebar.warning("⚠️ No documents uploaded yet. Please upload PDFs to ask questions.")
    
    else:
        # Simple FAQ UI
        st.sidebar.markdown("---")
        st.sidebar.markdown("### ⚡ Quick Commands")

        # Show All Students (everyone)
        if st.sidebar.button("👨‍🎓 Show All Students"):
            response = st.session_state.chatbot.ask(st.session_state.session_id, "show all students")
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

        # Find Student (everyone)
        find_query = st.sidebar.number_input("Find Student by ID", min_value=1, step=1, key="find_query")
        if st.sidebar.button("🔍 Find Student"):               
            command = f"find student {find_query}"
            response = st.session_state.chatbot.ask(st.session_state.session_id, command)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

        # Add Student (admin only)
        if st.session_state.role == "admin":
            with st.sidebar.expander("➕ Add Student", expanded=False):
                with st.form(key='add_student_form'):
                    add_name = st.text_input("Name")
                    add_age = st.number_input("Age", min_value=1, max_value=100, value=1)
                    add_grade = st.text_input("Grade")
                    submit_button = st.form_submit_button(label='Add Student')

                if submit_button:
                    command = f"add student {add_name} {add_age} {add_grade}"
                    response = st.session_state.chatbot.ask(st.session_state.session_id, command)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.rerun()

        # Update Student (admin only)
        if st.session_state.role == "admin":
            with st.sidebar.expander("✏️ Update Student", expanded=False):
                with st.form(key='update_student_form'):
                    update_id = st.number_input("Student ID", min_value=1, step=1)
                    update_name = st.text_input("New Name")
                    update_age = st.number_input("New Age", min_value=1, max_value=100, value=1)
                    update_grade = st.text_input("New Grade")
                    update_button = st.form_submit_button(label='Update Student')

                if update_button:
                    command = f"update student {update_id} {update_name} {update_age} {update_grade}"
                    response = st.session_state.chatbot.ask(st.session_state.session_id, command)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.rerun()

        # Delete Student (admin only)
        if st.session_state.role == "admin":
            with st.sidebar.expander("❌ Delete Student", expanded=False):
                with st.form(key='delete_student_form'):
                    delete_id = st.number_input("Student ID to Delete", min_value=1, step=1)
                    delete_button = st.form_submit_button(label='Delete Student')

                if delete_button:
                    command = f"delete student {delete_id}"
                    response = st.session_state.chatbot.ask(st.session_state.session_id, command)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.rerun()

    # response delay
    delay = st.sidebar.slider("Response delay (s)", 0.0, 5.0, 1.0)
    
    # user & bot avatars
    st.sidebar.markdown("---")
    user_avatar = st.sidebar.selectbox("👤 User Avatar", list(AVATARS.keys()))
    st.sidebar.image(AVATARS[user_avatar], width=50)
    bot_avatar = st.sidebar.selectbox("🤖 Bot Avatar", list(BOT_AVATARS.keys()))
    st.sidebar.image(BOT_AVATARS[bot_avatar], width=50)

    # download & clear conversation 
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🛠️ Utilities")

    # download chat history
    if st.session_state.messages and len(st.session_state.messages) > 1:
        chat_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])
        st.sidebar.download_button(
            "⬇️ Download Chat", 
            chat_text,
            file_name="chat_history.txt",
            mime="text/plain"
        )
        
    st.sidebar.markdown("---")

    # clear conversation
    if st.sidebar.button("🧹 Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

    # =====================================================
    # MAIN CHAT INTERFACE
    # =====================================================
    st.title("💬 Student Assistant Chatbot")
    
    # Initialize chatbot if not already done
    if st.session_state.chatbot is None:
        st.session_state.chatbot = initialize_chatbot(st.session_state.model)

    # Display model info
    st.caption(f"🤖 Using: **{st.session_state.model}** model")

    if not st.session_state.messages:
        if st.session_state.model == "RAG":
            st.session_state.messages.append({
                "role": "assistant",
                "content": "👋 Hi! I'm Lilo, your PDF Assistant Bot. Upload PDF documents and ask me questions about them!"
            })
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "👋 Hi! I'm Lilo, your Student Assistant Bot. Type 'help' to see what I can do!"
            })

    # Display chat messages
    for msg in st.session_state.messages:
        avatar = AVATARS[user_avatar] if msg["role"] == "user" else BOT_AVATARS[bot_avatar]
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("Type your message...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar=AVATARS[user_avatar]):
            st.markdown(user_input)

        with st.spinner("Assistant is typing..."):
            time.sleep(delay)
            response = st.session_state.chatbot.ask(st.session_state.session_id, user_input)

        with st.chat_message("assistant", avatar=BOT_AVATARS[bot_avatar]):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})


# =====================================================
# MAIN APP LOGIC
# =====================================================
def main():
    if not st.session_state.logged_in:
        if st.session_state.page == "register":
            register_page()
        else:
            login_page()
    else:
        chatbot_interface()
        if st.sidebar.button("🚪 Logout"):
            # Cleanup session data
            if st.session_state.rag_engine and st.session_state.session_id:
                st.session_state.rag_engine.delete_session(st.session_state.session_id)
            
            st.session_state.logged_in = False
            st.session_state.page = "login"
            st.session_state.username = None
            st.session_state.role = None
            st.session_state.messages = []
            st.session_state.chatbot = None
            st.session_state.rag_engine = None
            st.session_state.documents_uploaded = False
            st.session_state.uploaded_pdf_files = []
            st.session_state.processed_pdf_names = []
            st.rerun()

if __name__ == "__main__":
    main()