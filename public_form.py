import streamlit as st
import psycopg2
import pandas as pd
from datetime import datetime

# -----------------------
# DATABASE CONNECTION
# -----------------------
def get_connection():
    try:
        conn = psycopg2.connect(
            host=st.secrets["supabase"]["host"],
            database=st.secrets["supabase"]["database"],
            user=st.secrets["supabase"]["user"],
            password=st.secrets["supabase"]["password"],
            port=st.secrets["supabase"]["port"]
        )
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

# -----------------------
# SAFE INSERT FUNCTION
# -----------------------
def safe_insert_contact(data):
    conn = get_connection()
    if conn is None:
        return False, "Could not connect to database."

    cur = conn.cursor()
    try:
        # Check if contact exists by phone number
        cur.execute("SELECT id FROM contacts WHERE PhoneNumber = %s", (data["PhoneNumber"],))
        existing = cur.fetchone()

        if existing:
            return False, "This phone number is already registered."

        # Insert new contact
        cur.execute("""
            INSERT INTO contacts 
            (FullName, PhoneNumber, EmailAddress, City, Province, Country, SponsorName, InterestLevel, DateAdded)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            data["FullName"],
            data["PhoneNumber"],
            data["EmailAddress"],
            data["City"],
            data["Province"],
            data["Country"],
            data["SponsorName"],
            data["InterestLevel"],
            datetime.now()
        ))

        conn.commit()
        return True, "Contact successfully added!"
    except Exception as e:
        conn.rollback()
        return False, f"Error inserting contact: {e}"
    finally:
        cur.close()
        conn.close()

# -----------------------
# STREAMLIT FRONTEND
# -----------------------
st.set_page_config(page_title="Join APLGO South Africa", layout="centered")

st.markdown("<h2 style='text-align:center;'>🌟 Join APLGO South Africa</h2>", unsafe_allow_html=True)
st.markdown("Complete the form below to get started:")

with st.form("prospect_form"):
    st.subheader("Your Information")
    full_name = st.text_input("Full Name *")
    phone = st.text_input("Phone Number *", placeholder="e.g., 0712345678")
    email = st.text_input("Email Address", placeholder="your@email.com")

    st.subheader("Location Details")
    city = st.text_input("City", placeholder="Your city")
    province = st.text_input("Province", placeholder="Gauteng, Western Cape, etc.")
    country = st.text_input("Country", value="South Africa")

    st.subheader("APLGO Information")
    sponsor = st.text_input("Sponsor Name (if any)")
    interest = st.selectbox("Interest Level", ["Just Curious", "Interested", "Very Interested"])

    submitted = st.form_submit_button("🚀 Join APLGO Now")

    if submitted:
        if not full_name or not phone:
            st.error("Please fill in all required fields marked with *.")
        else:
            prospect_data = {
                "FullName": full_name.strip(),
                "PhoneNumber": phone.strip(),
                "EmailAddress": email.strip(),
                "City": city.strip(),
                "Province": province.strip(),
                "Country": country.strip(),
                "SponsorName": sponsor.strip(),
                "InterestLevel": interest
            }
            success, message = safe_insert_contact(prospect_data)
            if success:
                st.success(message)
                st.balloons()
            else:
                st.error(message)

