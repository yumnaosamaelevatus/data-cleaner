import streamlit as st
from cleaner_ import clean_file, scorecards, offers, merge_all
from io import BytesIO
import pandas as pd

st.title("HRCO Data Cleaner")

cleaned_df = None
cleaned_scorecard = None
cleaned_offers = None

uploaded_file = st.file_uploader("Upload applicant file", type=["csv"])
if uploaded_file is not None:
    try:
        cleaned_df = clean_file(uploaded_file)
    except Exception as e:
        st.error(f"Error processing applicant file: {e}")

uploaded_file2 = st.file_uploader("Upload scorecards file", type=["csv"])
if uploaded_file2 is not None:
    try:
        cleaned_scorecard = scorecards(uploaded_file2)
    except Exception as e:
        st.error(f"Error processing scorecards file: {e}")

uploaded_file3 = st.file_uploader("Upload offers file", type=["csv"])
if uploaded_file3 is not None:
    try:
        cleaned_offers = offers(uploaded_file3)
    except Exception as e:
        st.error(f"Error processing offers file: {e}")

# All three files are required before merging.
all_ready = cleaned_df is not None and cleaned_scorecard is not None and cleaned_offers is not None

if all_ready:
    merged_df = merge_all(cleaned_df, cleaned_offers, cleaned_scorecard)

    st.success(f"Merged {len(merged_df)} rows.")
    st.dataframe(merged_df.head(20))

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        merged_df.to_excel(writer, sheet_name="Merged", index=False)

    st.download_button(
        "Download Cleaned & Merged File",
        output.getvalue(),
        file_name="merged_cleaned_file.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
else:
    missing = []
    if cleaned_df is None:
        missing.append("Applicant file")
    if cleaned_scorecard is None:
        missing.append("Scorecards file")
    if cleaned_offers is None:
        missing.append("Offers file")
    st.info(f"Upload all three files to continue. Still missing: {', '.join(missing)}")
