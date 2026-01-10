import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Analiză Media vs Examen – Pe Profesor", layout="wide")

# -----------------------------------------------------------
# Coloane necesare
# -----------------------------------------------------------
REQUIRED_COLS = [
    "Nr. crt.",
    "Numele și prenumele elevului",
    "Unitatea de învățământ",
    "Clasa",
    "Media la matematică (an școlar 2024-2025)",
    "Nota la Examen - Matematică",
    "Profesor",
]

# -----------------------------------------------------------
# Funcții helper
# -----------------------------------------------------------
@st.cache_data
def load_excel(file, sheet_name=None):
    df = pd.read_excel(file, sheet_name=sheet_name, engine="openpyxl")
    if isinstance(df, dict):
        df = df[list(df.keys())[0]]
    return df

def compute_indicators(df):
    nr_elevi = df["Numele și prenumele elevului"].nunique()
    medie_media = df["Media_numeric"].mean()
    medie_examen = df["Examen_numeric"].mean()
    progres = medie_examen - medie_media
    # Rotunjire la 2 zecimale
    medie_media = round(medie_media, 2) if pd.notna(medie_media) else 0
    medie_examen = round(medie_examen, 2) if pd.notna(medie_examen) else 0
    progres = round(progres, 2) if pd.notna(progres) else 0
    return nr_elevi, medie_media, medie_examen, progres

def plot_medii_profesori(df):
    # Grupăm pe profesor și calculăm medii
    grouped = df.groupby("Profesor")[["Media_numeric", "Examen_numeric", "Diferenta"]].mean()
    # Sortăm descrescător după Diferență
    grouped = grouped.sort_values(by="Diferenta", ascending=False)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    grouped[["Media_numeric", "Examen_numeric"]].plot(kind="bar", ax=ax)
    
    ax.set_title("Media la matematică vs Nota la Examen – Pe Profesor (ordonat descrescător după Diferență)")
    ax.set_ylabel("Medie")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    return fig

def color_diferenta(val):
    try:
        val = float(val)
    except:
        return ""
    if val > 0:
        color = "green"
    elif val < 0:
        color = "red"
    else:
        color = "black"
    return f"color: {color}; font-weight: bold"

# -----------------------------------------------------------
# UI
# -----------------------------------------------------------
st.title("📊 Analiză: Media la matematică vs Nota la Examen – Pe Profesor")

# -----------------------------------------------------------
# Încărcare fișier
# -----------------------------------------------------------
with st.sidebar:
    st.header("Încărcare date")
    uploaded = st.file_uploader("Încarcă fișier Excel (.xlsx)", type=["xlsx"])
    sheet = st.text_input("Nume foaie (opțional)", "")

if uploaded is None:
    st.info("Încarcă un fișier pentru a începe.")
    st.stop()

sheet_arg = sheet.strip() if sheet.strip() else None
df = load_excel(uploaded, sheet_name=sheet_arg)

missing = [c for c in REQUIRED_COLS if c not in df.columns]
if missing:
    st.error(f"Fișierul nu are coloanele necesare: {missing}")
    st.stop()

# -----------------------------------------------------------
# Convertim la numeric pentru calcule
# -----------------------------------------------------------
df["Media_numeric"] = pd.to_numeric(df["Media la matematică (an școlar 2024-2025)"], errors='coerce')
df["Examen_numeric"] = pd.to_numeric(df["Nota la Examen - Matematică"], errors='coerce')
df["Diferenta"] = df["Examen_numeric"] - df["Media_numeric"]

# Coloanele de afișare cu 2 zecimale
df["Media_disp"] = df["Media_numeric"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")
df["Examen_disp"] = df["Examen_numeric"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")
df["Diferenta_disp"] = df["Diferenta"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")

# Nr. crt. ca int
df["Nr. crt."] = df["Nr. crt."].astype(int)

# -----------------------------------------------------------
# Selectare ȘCOLI
# -----------------------------------------------------------
scoli = sorted(df["Unitatea de învățământ"].dropna().unique())
select_all = st.checkbox("✅ Selectează toate școlile", value=True)

if select_all:
    sel_scoli = st.multiselect("🏫 Alege unitatea/unitățile de învățământ", scoli, default=scoli)
else:
    sel_scoli = st.multiselect("🏫 Alege unitatea/unitățile de învățământ", scoli, default=[])

if not sel_scoli:
    st.info("Selectează cel puțin o unitate de învățământ.")
    st.stop()

df_scoli = df[df["Unitatea de învățământ"].isin(sel_scoli)]

# -----------------------------------------------------------
# Selectare PROFESORI
# -----------------------------------------------------------
profesori = sorted(df_scoli["Profesor"].dropna().unique())
sel_profesori = st.multiselect("👨‍🏫 Alege profesorii", profesori, default=profesori)

if not sel_profesori:
    st.info("Selectează cel puțin un profesor.")
    st.stop()

df_sel = df_scoli[df_scoli["Profesor"].isin(sel_profesori)]

# -----------------------------------------------------------
# Sortare crescătoare după Diferența numerică
# -----------------------------------------------------------
df_sel = df_sel.sort_values(by="Diferenta", ascending=True)

# -----------------------------------------------------------
# Indicatori
# -----------------------------------------------------------
nr_elevi, medie_med, medie_examen, progres = compute_indicators(df_sel)
st.subheader("📌 Indicatori generali (selecția curentă)")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Număr elevi", nr_elevi)  # int
c2.metric("Medie la matematică", f"{medie_med:.2f}")
c3.metric("Medie Examen", f"{medie_examen:.2f}")
c4.metric("Progres (Examen – Media)", f"{progres:.2f}")

st.markdown("---")

# -----------------------------------------------------------
# Grafic descrescător după Diferență
# -----------------------------------------------------------
st.subheader("📊 Media la matematică vs Nota la Examen – pe Profesor (ordonat descrescător după Diferență)")
st.pyplot(plot_medii_profesori(df_sel), clear_figure=True)

st.markdown("---")

# -----------------------------------------------------------
# Tabel final
# -----------------------------------------------------------
st.subheader("📄 Tabel elevi (sortat crescător după Diferența Examen – Media)")

display_cols = [
    "Nr. crt.",
    "Numele și prenumele elevului",
    "Unitatea de învățământ",
    "Clasa",
    "Media_disp",
    "Examen_disp",
    "Profesor",
    "Diferenta_disp"
]

st.dataframe(
    df_sel[display_cols].style.applymap(color_diferenta, subset=["Diferenta_disp"])
    # Primele 3 coloane ~2 cm (76px)
    .set_properties(**{'max-width':'76px', 'white-space':'nowrap'}, subset=["Nr. crt.", "Numele și prenumele elevului", "Unitatea de învățământ"])
    # Restul compacte
    .set_properties(**{'max-width':'50px'}, subset=["Media_disp", "Examen_disp", "Diferenta_disp"]),
    use_container_width=True
)
