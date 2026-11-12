import streamlit as st
from cleaner_ import clean_file, scorecards, offers, merge_all
from io import BytesIO
import pandas as pd

st.title("HRCO Data Cleaner")


# Cache each file's cleaning by its content, so Streamlit doesn't re-clean the
# big applicant file from scratch on every rerun (every upload / button click).
@st.cache_data(show_spinner=False, max_entries=3)
def cached_clean_file(data: bytes):
    return clean_file(BytesIO(data))


@st.cache_data(show_spinner=False, max_entries=3)
def cached_scorecards(data: bytes):
    return scorecards(BytesIO(data))


@st.cache_data(show_spinner=False, max_entries=3)
def cached_offers(data: bytes):
    return offers(BytesIO(data))


@st.cache_data(show_spinner=False, max_entries=3)
def cached_merge_to_excel(app_bytes: bytes, sc_bytes: bytes, off_bytes: bytes):
    merged_df = merge_all(
        cached_clean_file(app_bytes),
        cached_offers(off_bytes),
        cached_scorecards(sc_bytes),
    )
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        merged_df.to_excel(writer, sheet_name="Merged", index=False)
    return merged_df, output.getvalue()


cleaned_df = None
cleaned_scorecard = None
cleaned_offers = None

uploaded_file = st.file_uploader("Upload applicant file", type=["csv"])
if uploaded_file is not None:
    try:
        with st.spinner("Cleaning applicant file..."):
            cleaned_df = cached_clean_file(uploaded_file.getvalue())
    except Exception as e:
        st.error(f"Error processing applicant file: {e}")

uploaded_file2 = st.file_uploader("Upload scorecards file", type=["csv"])
if uploaded_file2 is not None:
    try:
        with st.spinner("Cleaning scorecards file..."):
            cleaned_scorecard = cached_scorecards(uploaded_file2.getvalue())
    except Exception as e:
        st.error(f"Error processing scorecards file: {e}")

uploaded_file3 = st.file_uploader("Upload offers file", type=["csv"])
if uploaded_file3 is not None:
    try:
        with st.spinner("Cleaning offers file..."):
            cleaned_offers = cached_offers(uploaded_file3.getvalue())
    except Exception as e:
        st.error(f"Error processing offers file: {e}")

# All three files are required before merging.
all_ready = cleaned_df is not None and cleaned_scorecard is not None and cleaned_offers is not None

if all_ready:
    try:
        with st.spinner("Merging and building the Excel file..."):
            merged_df, excel_bytes = cached_merge_to_excel(
                uploaded_file.getvalue(), uploaded_file2.getvalue(), uploaded_file3.getvalue()
            )
    except Exception as e:
        st.error(f"Error merging files: {e}")
    else:
        st.success(f"Merged {len(merged_df)} rows.")
        st.dataframe(merged_df.head(20))

        st.download_button(
            "Download Cleaned & Merged File",
            excel_bytes,
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
