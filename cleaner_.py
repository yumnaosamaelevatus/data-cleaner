import pandas as pd
import re 
def clean_file(uploaded_file):
    df=pd.read_csv(uploaded_file, encoding="utf-8",dtype=str,keep_default_na=False, na_values=[])
    ##RENAME COLUMNS
    Renamecolumns={"Display Name":"Full Name","Reference Number":"Candidaite Referance No.",
"Category":"Role Type","Assign Candidate To Cluster":"Assigned Cluster","Created At":"Application Date","Source Name":"Agency Name","Source Type":"Source Channel",
"Stage Name":"Current Stage"}
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
"Senior Specialist":9,
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
    "senior registrar": "Senior Specialist",  # <-- fixed: same tier as Senior Specialist (rank 9)
    "senior specialist": "Senior Specialist",
    "consultant": "Consultant",
}
    professional_columns=[
    col for col in df.columns
    if "Professional Level" in col
]
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
"Medical Specialty","Has No Professional Experience","Total Years Of Experience","Years Since First Education Ended","Application Date","Job Name","Source Channel","Agency Name","Current Stage","Country","Assigned Cluster"]
    return df[output_columns]