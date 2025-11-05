import streamlit as st
import psycopg2
from datetime import datetime

# Database connection
def get_connection():
    return psycopg2.connect(
        host=st.secrets["supabase"]["host"],
        database=st.secrets["supabase"]["database"], 
        user=st.secrets["supabase"]["user"],
        password=st.secrets["supabase"]["password"],
        port=st.secrets["supabase"]["port"]
    )

# Simple insert function
def insert_contact(data):
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO contacts 
            (FullName, PhoneNumber, EmailAddress, City, Province, Country, SponsorName, InterestLevel, DateAdded)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data["FullName"], data["PhoneNumber"], data["EmailAddress"],
            data["City"], data["Province"], data["Country"], 
            data["SponsorName"], data["InterestLevel"], datetime.now()
        ))
        conn.commit()
        return True, "Success!"
    except Exception as e:
        conn.rollback()
        return False, f"Error: {e}"
    finally:
        cur.close()
        conn.close()

# Your form
st.set_page_config(page_title="Join APLGO", layout="centered")
st.title("🌟 Join APLGO South Africa")

with st.form("signup_form"):
    st.subheader("Your Information")
    
    full_name = st.text_input("Full Name *")
    phone = st.text_input("Phone Number *") 
    email = st.text_input("Email Address")
    city = st.text_input("City")
    province = st.text_input("Province")
    country = st.text_input("Country", value="South Africa")
    sponsor = st.text_input("Sponsor Name (if any)")
    interest = st.selectbox("Interest Level", ["Very Interested", "Interested", "Just Curious"])
    
    submitted = st.form_submit_button("🚀 Join APLGO Now")
    
    if submitted:
        if not full_name or not phone:
            st.error("Please fill in Name and Phone Number")
        else:
            success, message = insert_contact({
                "FullName": full_name, "PhoneNumber": phone, "EmailAddress": email,
                "City": city, "Province": province, "Country": country,
                "SponsorName": sponsor, "InterestLevel": interest
            })
            
            if success:
                st.success("🎉 Welcome to APLGO! We'll contact you soon.")
                st.balloons()
            else:
                st.error(message)
