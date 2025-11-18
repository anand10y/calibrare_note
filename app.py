import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Analiză Media vs Bacalaureat – Pe Profesor", layout="wide")

# -----------------------------------------------------------
# Coloane necesare
# -----------------------------------------------------------
REQUIRED_COLS = [
    "Nr. crt.",
    "Numele și prenumele elevului",
    "Unitatea de învățământ",
    "Clasa",
    "Media la matematică (an școlar 2024-2025)",
    "Nota la Bacalaureat - Matematică",
    "Profesor",
]

# -----------------------------------------------------------
# Funcții helper
# -----------------------------------------------------------
@st.cache_data
def load_excel(file, sheet_name=None):
    df = pd.read_excel(file, sheet_name=sheet_name, engine="openpyxl")

    # Dacă există mai multe foi, Pandas returnează dict -> luăm prima foaie
    if isinstance(df, dict):
        df = df[list(df.keys())[0]]

    return df


def as_number(series):
    s = series.astype(str).str.replace(",", ".", regex=False)
    return pd.to_numeric(s, errors="coerce")

# -----------------------------------------------------------
# Indicatori
# -----------------------------------------------------------
def compute_indicators(df):
    df["Media"] = as_number(df["Media la matematică (an școlar 2024-2025)"])
    df["Bac"] = as_number(df["Nota la Bacalaureat - Matematică"])

    nr_elevi = df["Numele și prenumele elevului"].nunique()
    medie_media = df["Media"].mean()
    medie_bac = df["Bac"].mean()
    progres = medie_bac - medie_media

    return nr_elevi, medie_media, medie_bac, progres

# -----------------------------------------------------------
# Grafic unic: Media vs Bac pe Profesor
# -----------------------------------------------------------
def plot_medii_profesori(df):
    grouped = df.groupby("Profesor")[ ["Media", "Bac"] ].mean()

    fig, ax = plt.subplots(figsize=(8, 4))
    grouped.plot(kind="bar", ax=ax)

    ax.set_title("Media la matematică vs Nota la Bacalaureat - Matematică – Pe Profesor")
    ax.set_ylabel("Medie")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    return fig

# -----------------------------------------------------------
# UI
# -----------------------------------------------------------
st.title("📊 Analiză: Media la matematică vs Nota la Bacalaureat - Matematică – Pe Profesor")

with st.sidebar:
    st.header("Încărcare date")
    uploaded = st.file_uploader("Încarcă fișier Excel (.xlsx)", type=["xlsx"])
    sheet = st.text_input("Nume foaie (opțional)", "")

# Fără fișier -> stop
if uploaded is None:
    st.info("Încarcă un fișier pentru a începe.")
    st.stop()

sheet_arg = sheet.strip() if sheet.strip() else None

# Citire
df = load_excel(uploaded, sheet_name=sheet_arg)

# Verificare coloane
missing = [c for c in REQUIRED_COLS if c not in df.columns]
if missing:
    st.error(f"Fișierul nu are coloanele necesare: {missing}")
    st.stop()

# Pregătire valori numerice
df["Media"] = as_number(df["Media la matematică (an școlar 2024-2025)"])
df["Bac"] = as_number(df["Nota la Bacalaureat - Matematică"])

# Selectare profesori
profesori = sorted(df["Profesor"].dropna().unique().tolist())
sel_profesori = st.multiselect("Alege profesorii", profesori, default=profesori)

df_sel = df[df["Profesor"].isin(sel_profesori)].copy()

if df_sel.empty:
    st.warning("Selecția curentă nu conține date.")
    st.stop()

# Indicatori
nr_elevi, medie_med, medie_bac, progres = compute_indicators(df_sel)

st.subheader("📌 Indicatori generali (selecție actuală)")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Număr elevi", nr_elevi)
c2.metric("Medie la matematică", f"{medie_med:.2f}")
c3.metric("Medie Bacalaureat", f"{medie_bac:.2f}")
c4.metric("Progres (Bac – Media)", f"{progres:.2f}")

st.markdown("---")

# Grafic
st.subheader("📊 Media la matematică vs Nota la Bacalaureat - Matematică – pe Profesor")
st.pyplot(plot_medii_profesori(df_sel), clear_figure=True)

st.markdown("---")

# Tabel
st.subheader("📄 Tabel complet elevi")
st.dataframe(df_sel.sort_values(["Profesor", "Clasa", "Numele și prenumele elevului"]), use_container_width=True)
