import streamlit as st
from cleaner_ import clean_file
from io import BytesIO
import pandas as pd
st.title("HRCO Data Cleaner")


uploaded_file = st.file_uploader("Upload an Excel or CSV file", type=["xlsx", "csv"])
if uploaded_file is not None:
    cleaned_df = clean_file(uploaded_file)
    st.success("File cleaned successfully!")
    st.dataframe(cleaned_df.head(5))

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        cleaned_df.to_excel(writer, index=False)
        
    st.download_button(
        "Download Cleaned File"
        ,output.getvalue()
        ,file_name="cleaned_file.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
        
        