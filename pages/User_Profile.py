import streamlit as st

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.error("You must be logged in to view this page.")
    st.stop()


st.title("👤 User Profile & Access Details")
st.subheader("Manage your account information and view security token.")

st.markdown("---")

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### Profile Information")
    st.metric("Name", st.session_state["user_name"])
    st.metric("Role / Permissions", st.session_state["user_role"].capitalize())
    st.metric("Username", st.session_state["username"])

with col2:
    st.markdown("### Security & Access Token (Simulated JWT)")
    st.warning("This area simulates the display of a secure JWT token received from an API after login.")
    
    st.code(st.session_state["jwt_token"], language="text")
    
    st.markdown("---")
    
    st.markdown("### Account Management")
    
    with st.form("profile_update_form"):
        new_name = st.text_input("Update Display Name", value=st.session_state["user_name"])
        new_pass = st.text_input("New Password (Leave blank to keep current)", type="password")
        
        if st.form_submit_button("Update Profile"):
            st.session_state["user_name"] = new_name 
            st.success(f"Profile updated successfully! Display name is now **{new_name}**.")
            
            if new_pass:
                st.info("Password update request sent to the backend.")