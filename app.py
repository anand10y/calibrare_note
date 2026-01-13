import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------
# CONFIGURARE PAGINĂ
# -----------------------------------------------------------
st.set_page_config(
    page_title="Analiză Media vs Examen – Pe Profesor",
    layout="wide"
)

# -----------------------------------------------------------
# COLOANE NECESARE
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
# FUNCȚII
# -----------------------------------------------------------
@st.cache_data
def load_excel(file, sheet_name=None):
    df = pd.read_excel(file, sheet_name=sheet_name, engine="openpyxl")
    if isinstance(df, dict):
        df = df[list(df.keys())[0]]
    return df


def compute_indicators(df):
    nr_elevi = df["Numele și prenumele elevului"].nunique()
    medie_media = round(df["Media_numeric"].mean(), 2)
    medie_examen = round(df["Examen_numeric"].mean(), 2)
    progres = round((df["Examen_numeric"] - df["Media_numeric"]).mean(), 2)
    return nr_elevi, medie_media, medie_examen, progres


def plotly_boxplot_diferenta_profesori(df):
    ordine = (
        df.groupby("Profesor")["Diferenta"]
        .median()
        .sort_values(ascending=True)
        .index.tolist()
    )

    fig = px.box(
        df,
        x="Diferenta",
        y="Profesor",
        orientation="h",
        category_orders={"Profesor": ordine},
        points="outliers",
        hover_data={
            "Numele și prenumele elevului": True,
            "Clasa": True,
            "Unitatea de învățământ": True,
            "Media_numeric": ':.2f',
            "Examen_numeric": ':.2f',
            "Diferenta": ':.2f',
        },
    )

    fig.add_vline(x=0, line_dash="dash", line_color="black")

    fig.update_layout(
        title="Diferența Examen – Media la matematică (Boxplot interactiv pe Profesor)",
        xaxis_title="Diferență (Examen – Media)",
        yaxis_title="Profesor",
        height=max(500, 35 * len(ordine)),
        margin=dict(l=20, r=20, t=60, b=20),
    )

    return fig


def plotly_bar_diferenta_profesori(df):
    grouped = df.groupby("Profesor")["Diferenta"].mean().reset_index()
    grouped = grouped.sort_values("Diferenta", ascending=True)
    ordine = grouped["Profesor"].tolist()

    fig = px.bar(
        grouped,
        x="Diferenta",
        y="Profesor",
        orientation="h",
        text=grouped["Diferenta"].round(2),
        color="Diferenta",
        color_continuous_scale=["red", "lightgray", "green"],
        category_orders={"Profesor": ordine},
    )

    fig.add_vline(x=0, line_color="black")

    fig.update_layout(
        title="Diferența medie Examen – Media la matematică (Bar chart interactiv)",
        xaxis_title="Diferență medie",
        yaxis_title="Profesor",
        height=max(500, 35 * len(grouped)),
    )

    return fig


def color_diferenta(val):
    try:
        v = float(val)
    except:
        return ""
    if v > 0:
        return "color: green; font-weight: bold"
    if v < 0:
        return "color: red; font-weight: bold"
    return "color: black; font-weight: bold"

# -----------------------------------------------------------
# UI
# -----------------------------------------------------------
st.title("📊 Analiză: Media la matematică vs Nota la Examen – Pe Profesor")

with st.sidebar:
    st.header("📂 Încărcare date")
    uploaded = st.file_uploader("Fișier Excel (.xlsx)", type=["xlsx"])
    sheet = st.text_input("Nume foaie (opțional)", "")

if uploaded is None:
    st.info("Încarcă un fișier Excel pentru a începe.")
    st.stop()

df = load_excel(uploaded, sheet.strip() or None)

missing = [c for c in REQUIRED_COLS if c not in df.columns]
if missing:
    st.error(f"Lipsesc coloane obligatorii: {missing}")
    st.stop()

# -----------------------------------------------------------
# PRELUCRARE DATE
# -----------------------------------------------------------
df["Media_numeric"] = pd.to_numeric(
    df["Media la matematică (an școlar 2024-2025)"], errors="coerce"
)
df["Examen_numeric"] = pd.to_numeric(
    df["Nota la Examen - Matematică"], errors="coerce"
)
df["Diferenta"] = df["Examen_numeric"] - df["Media_numeric"]
df["Nr. crt."] = df["Nr. crt."].astype(int)

df["Media_disp"] = df["Media_numeric"].map(lambda x: f"{x:.2f}")
df["Examen_disp"] = df["Examen_numeric"].map(lambda x: f"{x:.2f}")
df["Diferenta_disp"] = df["Diferenta"].map(lambda x: f"{x:.2f}")

# -----------------------------------------------------------
# FILTRARE ȘCOLI & PROFESORI
# -----------------------------------------------------------
scoli = sorted(df["Unitatea de învățământ"].dropna().unique())
sel_scoli = st.multiselect("🏫 Alege școlile", scoli, default=scoli)
df = df[df["Unitatea de învățământ"].isin(sel_scoli)]

profesori = sorted(df["Profesor"].dropna().unique())
sel_profesori = st.multiselect("👨‍🏫 Alege profesorii", profesori, default=profesori)
df_sel = df[df["Profesor"].isin(sel_profesori)]

if df_sel.empty:
    st.warning("Nu există date pentru selecția curentă.")
    st.stop()

# -----------------------------------------------------------
# INDICATORI
# -----------------------------------------------------------
nr, med_m, med_e, prog = compute_indicators(df_sel)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Număr elevi", nr)
c2.metric("Medie matematică", f"{med_m:.2f}")
c3.metric("Medie examen", f"{med_e:.2f}")
c4.metric("Progres", f"{prog:.2f}")

st.markdown("---")

# -----------------------------------------------------------
# SELECTOR TIP GRAFIC + AFIȘARE (Bar chart implicit)
# -----------------------------------------------------------
tip_grafic = st.radio(
    "Alege tipul de grafic",
    ["Diferență medie (bar chart)", "Boxplot diferență (opțional)"],
    index=0,  # Bar chart implicit
    horizontal=True
)

if tip_grafic == "Boxplot diferență (opțional)":
    st.plotly_chart(
        plotly_boxplot_diferenta_profesori(df_sel),
        use_container_width=True
    )
else:
    st.plotly_chart(
        plotly_bar_diferenta_profesori(df_sel),
        use_container_width=True
    )

st.markdown("---")

# -----------------------------------------------------------
# TABEL FINAL
# -----------------------------------------------------------
st.subheader("📄 Tabel elevi (sortat după Diferență)")

df_sel = df_sel.sort_values("Diferenta")

st.dataframe(
    df_sel[
        [
            "Nr. crt.",
            "Numele și prenumele elevului",
            "Unitatea de învățământ",
            "Clasa",
            "Media_disp",
            "Examen_disp",
            "Profesor",
            "Diferenta_disp",
        ]
    ]
    .style.applymap(color_diferenta, subset=["Diferenta_disp"]),
    use_container_width=True
)
