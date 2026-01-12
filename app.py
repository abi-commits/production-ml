"""
Streamlit Dashboard for Housing Price Prediction
"""

import streamlit as st
import requests
import pandas as pd
import os
from typing import Dict, Any

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000/predict")
API_KEY = os.getenv("API_KEY", "")

st.set_page_config(
    page_title="Housing Price Predictor",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Housing Price Prediction Dashboard")
st.markdown("Predict housing prices using machine learning")

# Sidebar for input
st.sidebar.header("Property Details")

# Input fields
date = st.sidebar.date_input("Date")
bedrooms = st.sidebar.number_input("Bedrooms", min_value=1, max_value=10, value=3)
bathrooms = st.sidebar.number_input("Bathrooms", min_value=1, max_value=5, value=2)
sqft_living = st.sidebar.number_input("Square Feet Living", min_value=500, max_value=10000, value=2000)
zipcode = st.sidebar.text_input("Zipcode", value="98101")

# API Key input
api_key_input = st.sidebar.text_input("API Key", type="password", value=API_KEY)

# Prediction button
if st.sidebar.button("Predict Price"):
    if not api_key_input:
        st.error("Please provide an API Key")
    else:
        # Prepare data
        data = [{
            "date": str(date),
            "price": 0,  # Not used for prediction
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "sqft_living": sqft_living,
            "zipcode": zipcode
        }]

        # Make API call
        headers = {"X-API-Key": api_key_input}
        try:
            response = requests.post(API_URL, json=data, headers=headers, timeout=10)

            if response.status_code == 200:
                result = response.json()
                predicted_price = result["predictions"][0]

                st.success("Prediction completed!")
                st.metric("Predicted Price", f"${predicted_price:,.2f}")

                # Display input summary
                st.subheader("Property Summary")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Bedrooms", bedrooms)
                with col2:
                    st.metric("Bathrooms", bathrooms)
                with col3:
                    st.metric("Sqft Living", sqft_living)

            else:
                st.error(f"API Error: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            st.error(f"Connection Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("Built with Streamlit and FastAPI")