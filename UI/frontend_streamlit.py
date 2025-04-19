import streamlit as st
import requests
import base64
from PIL import Image
import io
API_URL = "http://127.0.0.1:5000"

# Initialize session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "token" not in st.session_state:
    st.session_state.token = None

st.title("🪪 KYC Upload and Viewer")

# Sidebar Menu
if st.session_state.logged_in:
    menu = st.sidebar.selectbox(
        "Select Option", ["Upload PAN", "Upload Aadhaar", "View Records", "View Details", "Logout"])
else:
    menu = st.sidebar.selectbox("Select Option", ["Register", "Login"])

# Register
if menu == "Register":
    st.subheader("👤 User Registration")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        res = requests.post(f"{API_URL}/register",
                            json={"username": username, "password": password})
        st.success(res.json()["message"]) if res.ok else st.error(
            res.json()["message"])

# Login
elif menu == "Login":
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        res = requests.post(
            f"{API_URL}/login", json={"username": username, "password": password})
        if res.ok:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.token = res.json().get("token")  # if your API sends a token
            st.success("Login successful!")
        else:
            st.error(res.json().get("message", "Login failed"))

# Logout
elif menu == "Logout":
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.token = None
    st.success("Logged out successfully!")

# Upload Aadhaar
elif menu == "Upload Aadhaar":
    if st.session_state.logged_in:
        st.subheader("📤 Upload Aadhaar Card Document")
        aadhaar_file = st.file_uploader(
            "Upload PNG/JPG of Aadhaar", type=["png", "jpg", "jpeg"])

        if aadhaar_file and st.button("Submit Aadhaar"):
            file_bytes = aadhaar_file.read()
            b64_str = base64.b64encode(file_bytes).decode()
            image_data = base64.b64decode(b64_str)
            image = Image.open(io.BytesIO(image_data))
            st.image(image)
            mime = aadhaar_file.type
            data_url = f"data:{mime};base64,{b64_str}"

            payload = {
                "username": st.session_state.username,
                "image_b64": data_url
            }
            headers = {
                "Authorization": f"Bearer {st.session_state.token}"
            } if st.session_state.token else {}

            res = requests.post(
                f"{API_URL}/extract-text-from-aadhaar", json=payload, headers=headers)
            res_details = requests.post(
                f"{API_URL}/extract-text-from-aadhaar", json=payload, headers=headers)

            if res.ok and res_details.ok:
                st.markdown(f"Name: **{res_details.json().get('Name')}**")
                st.markdown(f"DOB: **{res_details.json().get('DOB')}**")
                st.markdown(f"Gender: **{res_details.json().get('Gender')}**")
                st.markdown(
                    f"Aadhaar No.: **{res_details.json().get('Aadhaar_Number')}**")
                st.success(
                    f"Aadhaar uploaded! Record ID: {res.json().get('record_id')}")
            else:
                st.error(res.json().get("error", "Aadhaar upload failed"))
    else:
        st.warning("Please login to upload Aadhaar.")


# Upload KYC
elif menu == "Upload PAN":
    if st.session_state.logged_in:
        st.subheader("📤 Upload Scanned KYC Document")
        uploaded_file = st.file_uploader(
            "Upload PNG/JPG file", type=["png", "jpg", "jpeg"])

        if uploaded_file and st.button("Submit KYC"):
            file_bytes = uploaded_file.read()
            b64_str = base64.b64encode(file_bytes).decode()
            # Remove the 'data:image/png;base64,' part
            image_data = base64.b64decode(b64_str)
            image = Image.open(io.BytesIO(image_data))
            st.image(image)
            mime = uploaded_file.type
            data_url = f"data:{mime};base64,{b64_str}"

            payload = {"username": st.session_state.username,
                       "image_b64": data_url}
            headers = {
                "Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}
            res = requests.post(f"{API_URL}/upload-kyc",
                                json=payload, headers=headers)
            res_details = requests.post(
                f"{API_URL}/extract-text-from-kyc", json=payload, headers=headers)

            if res.ok and res_details.ok:
                st.markdown(f"DOB:{res_details.json().get("DOB")}")
                st.markdown(f"PAN:{res_details.json().get("PAN")}")
                st.success(
                    f"KYC uploaded! Record ID: {res.json().get('record_id')}")
            else:
                st.error(res.json().get("error", "Upload failed"))
    else:
        st.warning("Please login to upload KYC.")

# View KYC records
elif menu == "View Records":
    if st.session_state.logged_in:
        st.subheader("📋 View Uploaded KYC Records")
        username = st.session_state.username
        headers = {
            "Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}
        if st.button("Get Records"):
            res = requests.get(
                f"{API_URL}/kyc-records/{username}", headers=headers)
            if res.ok:
                records = res.json()
                if records:
                    for r in records:
                        st.write(
                            f"ID: {r['id']} | Name: {r['name']} | Document: {r['doc_type']}")
                else:
                    st.info("No records found.")
            else:
                st.error("Failed to retrieve records")
    else:
        st.warning("Please login to view records.")

# View KYC details
elif menu == "View Details":
    if st.session_state.logged_in:
        st.subheader("🔎 View KYC Record Details")
        record_id = st.text_input("Enter Record ID")
        headers = {
            "Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}
        if st.button("Get Details"):
            res = requests.get(
                f"{API_URL}/kyc-details/{record_id}", headers=headers)
            if res.ok:
                st.json(res.json())
            else:
                st.error("Record not found")
    else:
        st.warning("Please login to view KYC details.")
