import pandas as pd
import re 
def clean_file(uploaded_file):
    df=pd.read_csv(uploaded_file, encoding="utf-8",dtype=str,keep_default_na=False, na_values=[])
    ##RENAME COLUMNS
    Renamecolumns={"Display Name":"Full Name","Reference Number":"Candidaite Referance No.",
"Category":"Role Type","Assign Candidate To Cluster":"Assigned Cluster","Created At":"Application Date","Source Name":"Agency Name","Source Type":"Source Channel"}
    df=df.rename(columns=Renamecolumns)
    NA_TOKENS = {"", "n/a", "na", "n.a", "nil", "-", "none", "null"}

    def clean_val(v):
        if v is None:
          return None
        v = str(v).strip()
        return None if v.lower() in NA_TOKENS else v

    possible_columns = ["National Id ", "National Id  National Id", "National Id  Niu"]
    df[possible_columns] = df[possible_columns].map(clean_val)
    df["National ID"] = df[possible_columns].bfill(axis=1).iloc[:, 0]
   
    
    Rank={"Assistant Nurse":1,
"Midwife Nurse":2,
"Registered Nurse":3,
"Staff Nurse":3,
"Charge Nurse":4,
"Head Nurse":5,
"General Practitioner (GP)":6,
"Resident":7,
"Specialist":8,
"Registrar":8,
"Senior Specialist":9,
"Senior Registrar":9,
"Consultant":10
    }
    NORMALIZE_LEVEL = {
    "assistant nurse": "Assistant Nurse",
    "midwife": "Midwife Nurse",
    "midwife nurse": "Midwife Nurse",
    "registered nurse": "Registered Nurse",
    "staff nurse": "Staff Nurse",
    "charge nurse": "Charge Nurse",
    "head nurse": "Head Nurse",
    "general practitioner (gp)": "General Practitioner (GP)",
    "resident": "Resident",
    "specialist": "Specialist",
    "sepcialist": "Specialist",         # typo fix
    "registrar": "Registrar",
    "senior registrar": "Senior Registrar",  # <-- fixed: same tier as Senior Specialist (rank 9)
    "senior specialist": "Senior Specialist",
    "consultant": "Consultant",
}
    professional_columns=[col for col in df.columns if "Professional Level" in col or "Proofessional Level" in col]
    def extract_professional_level(row):
        highest, highest_rank = None, -1
        for col in professional_columns:
                    value = row[col]
                    if value is None or str(value).strip() == '':
                          continue
                    key = str(value).strip().lower()          # "Sepcialist" -> "sepcialist"
                    canon = NORMALIZE_LEVEL.get(key)            # "sepcialist" -> "Specialist"
                    if canon and Rank[canon] > highest_rank:
                      highest_rank = Rank[canon]
                      highest = canon
    
        return highest



    
        return professional_level
    df["Professional Level (Rank)"]=df.apply(extract_professional_level,axis=1)
    df.loc[(df["Has No Education"]=="True") & (df["Professional Level (Rank)"].isna()),
       "Professional Level (Rank)"] = "Has no education"
    df["Medical Specialty"] = (
    df[["Medical Specialty","Specialty "]]
    .replace('', pd.NA)
    .bfill(axis=1)
    .iloc[:,0]
    .fillna('')
)
    df.loc[(df["Has No Professional Experience"]=="True")&(df["Medical Specialty"]==""),
       "Medical Specialty"]="No professional Experience"
    
    def add_educational_qualification(df):
        degree_groups = {}
        for c in df.columns:
            m = re.match(r'^Education(?: (\d+))? - (.*[Dd]egree.*)$', c.strip())
            if m:
                idx = int(m.group(1)) if m.group(1) else 1
                degree_groups.setdefault(idx, []).append(c)

        fromto_col_map = {}
        for c in df.columns:
            m = re.match(r'^Education(?: (\d+))? - From To$', c.strip())
            if m:
                idx = int(m.group(1)) if m.group(1) else 1
                fromto_col_map[idx] = c

        slots = sorted(set(degree_groups) & set(fromto_col_map))

        def parse_end_date(ft):
            ft = str(ft).strip()
            if ft == '' or ft.lower() == 'nan':
                return None
            if ' - ' in ft:
                _, end = ft.split(' - ', 1)
            else:
                end = ft
            d = pd.to_datetime(end.strip(), errors='coerce')
            return None if pd.isna(d) else d

        def first_nonempty(row, cols):
            for c in cols:
                v = row[c]
                v = '' if pd.isna(v) else str(v).strip()
                if v != '':
                    return v
            return ''

        def get_recent_degree(row):
            best_date = None
            best_degree = ''
            for idx in slots:
                d = parse_end_date(row[fromto_col_map[idx]])
                if d is None:
                    continue
                if best_date is None or d > best_date:
                    deg = first_nonempty(row, degree_groups[idx])
                    if deg != '':
                        best_date = d
                        best_degree = deg
            return best_degree

        df["Educational Qualification"] = df.apply(get_recent_degree, axis=1)
        return df  
    df = add_educational_qualification(df)
    df.loc[(df["Has No Education"]=="True") & (df["Educational Qualification"]==""),
       "Educational Qualification"] = "Has no education"   









    output_columns=["Candidaite Referance No.",
"Company Name",
"Full Name",
"National ID","Date Of Birth",
"Gender",
"Marital Status","Nationality ","Phone Number","Email",
"Role Type","Educational Qualification","Professional Level (Rank)",
"Medical Specialty","Has No Professional Experience","Total Years Of Experience","Years Since First Education Ended","Application Date","Job Name","Source Channel","Agency Name","Stage Name","Country","Assigned Cluster"]
    return df[output_columns]



def scorecards(uploaded_file2):
        df2=pd.read_csv(uploaded_file2, encoding="utf-8",dtype=str,keep_default_na=False, na_values=[])
        col_to_rename={
                "Created At":"Date Entered Interview","Decision Maker":"Interview Examiner","Score":"Interview Scorecard Score","Total Accepted":"Scorecard Decision"
            }
        df2=df2.rename(columns=col_to_rename)
        return df2[["Email","Date Entered Interview","Interview Examiner","Interview Scorecard Score","Scorecard Decision"]]


def offers(uploaded_file3):
    df3 = pd.read_csv(uploaded_file3, encoding="utf-8", dtype=str, keep_default_na=False, na_values=[])

   
    col_to_rename2 = {
        "Created At": "Evaluation Date",
        "Expiry Time": "Offer Expiry Date",
        "Form Status": "Offer Status",
        "Updated By": "Offer Updated By",
        "Rejection Reason": "Candidate Rejection Reason",
        "Rejection Note": "Rejection Notes",
    }
    df3 = df3.rename(columns=col_to_rename2)

    df3["Offer Owner"] = df3["Created By"]
    df3["Offer Created By"] = df3["Created By"]

    
    salary_Columns = [
        "Basic",
        "Basic Salary",
        "Equation",
        "Equation 2",
        "Equation 3",
        "Food",
        "Food Allowance",
        "Housing",
        "Housing Allowance",
        "Total",
        "Transportation",
        "Transportation "
    ]

    for col in salary_Columns:
        df3[col] = (
            df3[col].astype(str).str.replace("SAR", "", regex=True).str.strip()
        )
        df3[col] = pd.to_numeric(df3[col], errors="coerce")

    df3["Offered Salary (SAR)"] = df3[salary_Columns].max(axis=1)

    return df3[["Email",
        "Evaluation Date",
        "Offered Salary (SAR)",
        "Offer Expiry Date",
        "Offer Status",
        "Offer Owner",
        "Offer Created By",
        "Offer Updated By",
        "Candidate Rejection Reason",
        "Pending With",
        "Rejected By",
        "Rejection Notes"
    ]]
    

import pandas as pd
import uuid


def make_keys_unique_if_blank(df, key="Email"):
    """
    Give every blank/missing key a unique placeholder so blank-email rows
    never accidentally match each other during the merge.
    """
    df = df.copy()
    blank_mask = df[key].str.strip() == ""
    df.loc[blank_mask, key] = [f"__no_email_{uuid.uuid4()}__" for _ in range(blank_mask.sum())]
    return df


def merge_all(applicants_df, offers_df, scorecards_df):
    """
    Left join anchored on Applicants (one row per candidate).
    For candidates with multiple offers/scorecards, keeps the MOST RECENT
    one based on the underlying "Created At" date - not just first-in-file.
    """
    key = "Email"

    applicants_df = applicants_df.copy()
    offers_df = offers_df.copy()
    scorecards_df = scorecards_df.copy()

    for df in [applicants_df, offers_df, scorecards_df]:
        df[key] = df[key].astype(str).str.strip().str.lower()

    applicants_df = make_keys_unique_if_blank(applicants_df, key)
    offers_df = make_keys_unique_if_blank(offers_df, key)
    scorecards_df = make_keys_unique_if_blank(scorecards_df, key)

    # sort by date descending, then keep the first (= most recent) per candidate
    offers_dedup = (
        offers_df
        .assign(_sort_date=pd.to_datetime(offers_df["Evaluation Date"], errors="coerce"))
        .sort_values("_sort_date", ascending=False)
        .drop_duplicates(subset=key, keep="first")
        .drop(columns="_sort_date")
    )
    scorecards_dedup = (
        scorecards_df
        .assign(_sort_date=pd.to_datetime(scorecards_df["Date Entered Interview"], errors="coerce"))
        .sort_values("_sort_date", ascending=False)
        .drop_duplicates(subset=key, keep="first")
        .drop(columns="_sort_date")
    )

    merged = applicants_df.merge(offers_dedup, on=key, how="left", suffixes=("", "_offer"))
    merged = merged.merge(scorecards_dedup, on=key, how="left", suffixes=("", "_scorecard"))

    merged.loc[merged[key].str.startswith("__no_email_"), key] = ""

    return merged






