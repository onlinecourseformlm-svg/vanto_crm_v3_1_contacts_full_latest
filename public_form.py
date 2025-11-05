import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# Simple public form only
st.set_page_config(page_title="APLGO Registration", page_icon="🌟", layout="centered")

# Database connection
import psycopg2
import streamlit as st

def get_connection():
    return psycopg2.connect(
        host=st.secrets["supabase"]["host"],
        database=st.secrets["supabase"]["database"],
        user=st.secrets["supabase"]["user"],
        password=st.secrets["supabase"]["password"],
        port=st.secrets["supabase"]["port"]
    )


# Your existing insert function
def safe_insert_contact(contact_data):
    PROSPECT_COLUMNS = [
        "DateCaptured", "State", "Country", "Province", "City",
        "FullName", "PhoneNumber", "EmailAddress", "InterestLevel",
        "AssignedTo", "ActionTaken", "NextAction", "LeadTemperature",
        "CommunicationStatus", "SponsorName", "LeadType",
        "AssociateStatus", "RegistrationStatus", "APLGoID", "AccountPassword"
    ]
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Your duplicate checking logic here
    phone = contact_data.get('PhoneNumber', '')
    email = contact_data.get('EmailAddress', '')
    
    if phone:
        cur.execute("SELECT id FROM contacts WHERE PhoneNumber = ?", (phone,))
        if cur.fetchone():
            conn.close()
            return False, "Duplicate phone number", None
    
    # Insert logic
    for col in PROSPECT_COLUMNS:
        if col not in contact_data:
            contact_data[col] = ""
    
    if not contact_data.get("DateCaptured"):
        contact_data["DateCaptured"] = datetime.now().strftime("%Y-%m-%d")
    
    columns = ", ".join(PROSPECT_COLUMNS)
    placeholders = ", ".join(["?" for _ in PROSPECT_COLUMNS])
    values = [contact_data[col] for col in PROSPECT_COLUMNS]
    
    cur.execute(f"INSERT INTO contacts ({columns}) VALUES ({placeholders})", values)
    contact_id = cur.lastrowid
    conn.commit()
    conn.close()
    
    return True, "Success", contact_id

# Public Form UI
st.title("🌟 Join APLGO South Africa")
st.write("Complete the form below to get started")

with st.form("public_registration"):
    st.subheader("Your Information")
    
    col1, col2 = st.columns(2)
    with col1:
        full_name = st.text_input("Full Name *", placeholder="Enter your full name")
        phone = st.text_input("Phone Number *", placeholder="0712345678")
    
    with col2:
        email = st.text_input("Email Address", placeholder="your@email.com")
        city = st.text_input("City", placeholder="Your city")
    
    st.subheader("Location Details")
    col3, col4 = st.columns(2)
    with col3:
        province = st.text_input("Province", placeholder="Gauteng, Western Cape, etc.")
    with col4:
        country = st.text_input("Country", value="South Africa")
    
    st.subheader("APLGO Information")
    sponsor_name = st.text_input("Sponsor Name (if any)", placeholder="Who referred you?")
    interest = st.selectbox("Interest Level", ["Very Interested", "Somewhat Interested", "Just Curious"])
    
    st.markdown("**Required fields*")
    submitted = st.form_submit_button("🚀 Join APLGO Now")
    
    if submitted:
        if not full_name or not phone:
            st.error("Please fill in Name and Phone Number")
        else:
            prospect_data = {
                "FullName": full_name,
                "PhoneNumber": phone,
                "EmailAddress": email,
                "City": city,
                "Province": province,
                "State": province,
                "Country": country,
                "InterestLevel": interest,
                "SponsorName": sponsor_name,
                "LeadTemperature": "Warm",
                "CommunicationStatus": "New",
                "RegistrationStatus": "Not Registered",
                "ActionTaken": "Public Form Submission",
                "NextAction": "Follow Up",
                "LeadType": "Prospect"
            }
            
            success, message, contact_id = safe_insert_contact(prospect_data)
            
            if success:
                st.success("🎉 Welcome to APLGO! We'll contact you within 24 hours.")
                st.balloons()
                st.info("**Next Steps:** Check your WhatsApp for updates from our team")
            else:

                st.warning("📱 We already have your details! Our team will contact you soon.")
