import streamlit as st

st.set_page_config(
    layout="wide",
    page_title="Knowledge Graph & Admin System",
    initial_sidebar_state="expanded"
)

if "USERS" not in st.session_state:
    st.session_state["USERS"] = {
        "admin": {"password": "123", "role": "admin", "name": "Admin User"},
        "user": {"password": "123", "role": "editor", "name": "Standard Editor"},
    }

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["auth_mode"] = "login" 

def simulate_jwt_login(username, password):
    """Simulates sending credentials to an API and receiving a JWT token/payload."""
    users_db = st.session_state["USERS"]
    if username in users_db and password == users_db[username]["password"]:
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.session_state["user_role"] = users_db[username]["role"]
        st.session_state["user_name"] = users_db[username]["name"]
        st.session_state["jwt_token"] = f"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.simulated_payload.{username}"
        return True, f"Login successful ✅. Welcome, {users_db[username]['name']}!"
    
    return False, "Invalid username or password."

def simulate_registration(username, password, name):
    """Simulates creating a new user record via an API."""
    users_db = st.session_state["USERS"]
    if username in users_db:
        return False, "Username already exists."
    
    users_db[username] = {"password": password, "role": "editor", "name": name}
    st.session_state["USERS"] = users_db
    return simulate_jwt_login(username, password)


def render_login_register_ui():
    """Renders the login or register form based on the current mode."""
    
    st.title("🔐 Knowledge Graph System")
    
    tab_login, tab_register = st.tabs(["Login", "Register"])
    
    with tab_login:
        st.subheader("Login with your credentials")
        
        with st.form("login_form"):
            login_username = st.text_input("Username (e.g., admin, user)", key="login_user")
            login_password = st.text_input("Password (e.g., 123)", type="password", key="login_pass")
            submitted = st.form_submit_button("Log In", type="primary")

            if submitted:
                success, message = simulate_jwt_login(login_username, login_password)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

    with tab_register:
        st.subheader("Create a new account")
        
        with st.form("register_form"):
            register_name = st.text_input("Display Name", key="register_name")
            register_username = st.text_input("New Username", key="register_user")
            register_password = st.text_input("New Password", type="password", key="register_pass")
            register_password_confirm = st.text_input("Confirm Password", type="password", key="register_confirm")
            
            submitted = st.form_submit_button("Register & Log In", type="primary")

            if submitted:
                if not (register_name and register_username and register_password and register_password_confirm):
                    st.error("Please fill in all fields.")
                elif register_password != register_password_confirm:
                    st.error("Passwords do not match.")
                else:
                    success, message = simulate_registration(register_username, register_password, register_name)
                    if success:
                        st.success(f"Registration successful! {message}")
                        st.rerun()
                    else:
                        st.error(message)

def main():
    if not st.session_state["logged_in"]:
        render_login_register_ui()
    else:
        # --- LOGGED-IN STATE ---
        st.sidebar.success(f"👋 Logged in as: **{st.session_state.get('user_name', 'User')}** ({st.session_state.get('user_role', 'none')})")
        
        if st.sidebar.button("Logout", use_container_width=True):
            st.session_state.clear()
            st.session_state["logged_in"] = False 
            st.rerun()

        st.title(f"Welcome, {st.session_state.get('user_name', 'User')}!")
        st.info("Please select a page from the sidebar to begin.")

if __name__ == "__main__":
    main()