import os
import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("BACKEND_URL", "http://localhost:8000/upload")

st.title("Data Classification Dashboard")

uploaded_file = st.file_uploader("Upload Excel File", type="xlsx")

if uploaded_file is not None:
    with st.spinner("Classifying..."):
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        resp = requests.post(API_URL, files=files)
        if resp.status_code != 200:
            st.error(f"Error from API: {resp.text}")
        else:
            data = resp.json()["results"]
            df = pd.DataFrame(data)
            st.subheader("Results")
            st.dataframe(df)

            counts = df["classification"].value_counts()
            st.subheader("Summary")
            st.bar_chart(counts)

