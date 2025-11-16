import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Progres Bacalaureat – Analytics", layout="wide")

# ------------------------
# Helper functions
# ------------------------
REQUIRED_COLS = ["Nume", "Clasa", "Proba", "Evaluare", "Simulare", "Bacalaureat"]

@st.cache_data
def load_excel(file, sheet_name=None):
    if sheet_name is None:
        df = pd.read_excel(file, engine="openpyxl")
    else:
        df = pd.read_excel(file, sheet_name=sheet_name, engine="openpyxl")
    return df

def check_columns(df):
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    return missing

def as_number(series):
    s = series.astype(str).str.replace(",", ".", regex=False)
    return pd.to_numeric(s, errors="coerce")

# ------------------------
# Compute indicators (metoda diferenței mediilor claselor)
# ------------------------
def compute_indicators_class_means(df):
    for col in ["Evaluare", "Simulare", "Bacalaureat"]:
        df[col] = as_number(df[col])

    n_elevi = df["Nume"].nunique()
    class_means = df.groupby("Clasa")[["Evaluare", "Simulare", "Bacalaureat"]].mean()

    mean_eval = class_means["Evaluare"].mean()
    mean_sim = class_means["Simulare"].mean()
    mean_bac = class_means["Bacalaureat"].mean()

    prog_eval_bac = mean_bac - mean_eval
    prog_sim_eval = mean_sim - mean_eval
    prog_bac_sim = mean_bac - mean_sim

    with np.errstate(divide='ignore', invalid='ignore'):
        pct_eval_bac = np.nanmean((class_means["Bacalaureat"] - class_means["Evaluare"]) / class_means["Evaluare"] * 100.0)
        pct_sim_eval = np.nanmean((class_means["Simulare"] - class_means["Evaluare"]) / class_means["Evaluare"] * 100.0)
        pct_bac_sim = np.nanmean((class_means["Bacalaureat"] - class_means["Simulare"]) / class_means["Simulare"] * 100.0)

    return {
        "n_elevi": n_elevi,
        "mean_eval": mean_eval,
        "mean_sim": mean_sim,
        "mean_bac": mean_bac,
        "prog_eval_bac": prog_eval_bac,
        "prog_sim_eval": prog_sim_eval,
        "prog_bac_sim": prog_bac_sim,
        "pct_eval_bac": pct_eval_bac,
        "pct_sim_eval": pct_sim_eval,
        "pct_bac_sim": pct_bac_sim,
    }

# ------------------------
# Plot functions
# ------------------------
def plot_stage_means(means_dict, title="Medii pe etape (selecție curentă)"):
    stages = ["Evaluare", "Simulare", "Bacalaureat"]
    values = [means_dict["mean_eval"], means_dict["mean_sim"], means_dict["mean_bac"]]
    fig, ax = plt.subplots()
    ax.bar(stages, values)
    ax.set_title(title)
    ax.set_ylabel("Medie")
    ax.set_xlabel("Etapă")
    return fig

def plot_progress_by_class_class_mean(df, title="Progres mediu pe clasă"):
    grouped = df.groupby("Clasa")[["Evaluare", "Simulare", "Bacalaureat"]].mean()
    grouped["Bac_minus_Eval"] = grouped["Bacalaureat"] - grouped["Evaluare"]
    grouped = grouped.sort_values("Bac_minus_Eval", ascending=False)
    fig, ax = plt.subplots()
    grouped["Bac_minus_Eval"].plot(kind="bar", ax=ax)
    ax.set_title(title)
    ax.set_ylabel("Progres (puncte)")
    ax.set_xlabel("Clasa")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    return fig

def plot_progress_by_proba_class_mean(df, title="Progres mediu pe probă"):
    grouped = df.groupby("Proba")[["Evaluare", "Simulare", "Bacalaureat"]].mean()
    grouped["Bac_minus_Eval"] = grouped["Bacalaureat"] - grouped["Evaluare"]
    grouped = grouped.sort_values("Bac_minus_Eval", ascending=False)
    fig, ax = plt.subplots()
    grouped["Bac_minus_Eval"].plot(kind="bar", ax=ax)
    ax.set_title(title)
    ax.set_ylabel("Progres (puncte)")
    ax.set_xlabel("Proba")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    return fig

def plot_line_by_class_class_mean(df, title="Evoluția mediilor pe clase (medie clase)"):
    grouped = df.groupby("Clasa")[["Evaluare", "Simulare", "Bacalaureat"]].mean()
    fig, ax = plt.subplots()
    x = ["Evaluare", "Simulare", "Bacalaureat"]
    for clasa, row in grouped.iterrows():
        y = row.values
        ax.plot(x, y, marker="o", label=clasa)
    ax.set_title(title)
    ax.set_ylabel("Medie")
    ax.set_xlabel("Etapă")
    ax.legend(title="Clasa", bbox_to_anchor=(1.05,1), loc="upper left")
    plt.tight_layout()
    return fig

def plot_line_by_proba_class_mean(df, title="Evoluția mediilor pe probe (medie clase)"):
    grouped = df.groupby("Proba")[["Evaluare", "Simulare", "Bacalaureat"]].mean()
    fig, ax = plt.subplots()
    x = ["Evaluare", "Simulare", "Bacalaureat"]
    for proba, row in grouped.iterrows():
        y = row.values
        ax.plot(x, y, marker="o", label=proba)
    ax.set_title(title)
    ax.set_ylabel("Medie")
    ax.set_xlabel("Etapă")
    ax.legend(title="Proba", bbox_to_anchor=(1.05,1), loc="upper left")
    plt.tight_layout()
    return fig

def plot_per_student_lines(df, title="Evoluția fiecărui elev"):
    temp = df.copy()
    temp["Evaluare"] = as_number(temp["Evaluare"])
    temp["Simulare"] = as_number(temp["Simulare"])
    temp["Bacalaureat"] = as_number(temp["Bacalaureat"])
    fig, ax = plt.subplots()
    x = ["Evaluare", "Simulare", "Bacalaureat"]
    for nume, g in temp.groupby("Nume"):
        y = [g["Evaluare"].mean(), g["Simulare"].mean(), g["Bacalaureat"].mean()]
        ax.plot(x, y, marker="o", alpha=0.6)
    ax.set_title(title)
    ax.set_ylabel("Notă")
    ax.set_xlabel("Etapă")
    ax.grid(True, linestyle="--", alpha=0.3)
    return fig

def heatmap_progress_class_proba(df, title="Progres mediu (Bac - Evaluare) pe Clasă și Probă"):
    grouped = df.groupby(["Clasa", "Proba"])[["Evaluare", "Bacalaureat"]].mean().reset_index()
    grouped["Progres"] = grouped["Bacalaureat"] - grouped["Evaluare"]
    pivot = grouped.pivot(index="Clasa", columns="Proba", values="Progres")
    fig, ax = plt.subplots(figsize=(8, max(4, len(pivot)*0.5)))
    cax = ax.matshow(pivot, cmap="YlGnBu")
    fig.colorbar(cax)
    ax.set_xticks(np.arange(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=45, ha="right")
    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            val = pivot.iloc[i, j]
            if not np.isnan(val):
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", color="black")
    ax.set_title(title)
    plt.tight_layout()
    return fig

def plot_scatter_by_group(df, group_col="Clasa", title="Distribuția notelor pe etape"):
    temp = df.copy()
    temp["Evaluare"] = as_number(temp["Evaluare"])
    temp["Simulare"] = as_number(temp["Simulare"])
    temp["Bacalaureat"] = as_number(temp["Bacalaureat"])
    fig, ax = plt.subplots()
    x = ["Evaluare", "Simulare", "Bacalaureat"]
    for grp, g in temp.groupby(group_col):
        y = [g["Evaluare"].mean(), g["Simulare"].mean(), g["Bacalaureat"].mean()]
        ax.scatter(x, y, label=grp, alpha=0.8)
    ax.set_title(title)
    ax.set_ylabel("Medie")
    ax.set_xlabel("Etapă")
    ax.legend(title=group_col, bbox_to_anchor=(1.05,1), loc="upper left")
    plt.tight_layout()
    return fig

# ------------------------
# UI
# ------------------------
st.title("📊 Progres Evaluare - Simulare - Bacalaureat – Analiză pe clase și probe")

with st.sidebar:
    st.header("🔧 Setări / Încărcare date")
    uploaded = st.file_uploader("Încarcă fișier Excel (.xlsx) cu coloanele: Nume, Clasa, Proba, Evaluare, Simulare, Bacalaureat", type=["xlsx"])
    sheet = st.text_input("Nume foaie (opțional, lasă gol pentru prima foaie)", value="")
    show_student_plots = st.checkbox("Afișează grafice pentru fiecare elev", value=False)
    show_all_students = st.checkbox("Afișează tabel cu toți elevii selecția curentă", value=True)
    st.markdown("---")
    st.caption("Dacă ai notele cu virgule, aplicația le normalizează automat.")

if uploaded is None:
    st.info("Încarcă un fișier Excel pentru a începe.")
    st.stop()

sheet_arg = sheet.strip() if sheet.strip() else None
df = load_excel(uploaded, sheet_name=sheet_arg)
missing = check_columns(df)
if missing:
    st.error(f"Fișierul nu are coloanele obligatorii: {missing}. Coloanele găsite sunt: {list(df.columns)}")
    st.stop()

for c in ["Evaluare", "Simulare", "Bacalaureat"]:
    df[c] = as_number(df[c])

classes = sorted(df["Clasa"].dropna().unique().tolist())
probes = sorted(df["Proba"].dropna().unique().tolist())
col1, col2 = st.columns(2)
with col1:
    clasa_sel = st.multiselect("Alege clasa/le", classes, default=classes)
with col2:
    proba_sel = st.multiselect("Alege proba/probele", probes, default=probes)

mask = df["Clasa"].isin(clasa_sel) & df["Proba"].isin(proba_sel)
df_sel = df.loc[mask].copy()
if df_sel.empty:
    st.warning("Selecția curentă nu are date. Alege alte clase/probe.")
    st.stop()

# Indicators
inds = compute_indicators_class_means(df_sel)

st.subheader("📌 Indicatori generali (selecție curentă)")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Număr elevi (unic)", f"{inds['n_elevi']}")
m2.metric("Medie Evaluare", f"{inds['mean_eval']:.2f}" if pd.notna(inds['mean_eval']) else "—")
m3.metric("Medie Simulare", f"{inds['mean_sim']:.2f}" if pd.notna(inds['mean_sim']) else "—")
m4.metric("Medie Bacalaureat", f"{inds['mean_bac']:.2f}" if pd.notna(inds['mean_bac']) else "—")

m5, m6, m7 = st.columns(3)
m5.metric("Progres mediu Bac vs Evaluare (puncte)", f"{inds['prog_eval_bac']:.2f}", delta=f"{inds['pct_eval_bac']:.1f}%")
m6.metric("Progres mediu Sim vs Evaluare (puncte)", f"{inds['prog_sim_eval']:.2f}", delta=f"{inds['pct_sim_eval']:.1f}%")
m7.metric("Progres mediu Bac vs Simulare (puncte)", f"{inds['prog_bac_sim']:.2f}", delta=f"{inds['pct_bac_sim']:.1f}%")

st.markdown("---")

# Plots
fig_means = plot_stage_means(inds)
st.pyplot(fig_means, clear_figure=True)
fig_prog_class = plot_progress_by_class_class_mean(df_sel)
st.pyplot(fig_prog_class, clear_figure=True)
fig_prog_proba = plot_progress_by_proba_class_mean(df_sel)
st.pyplot(fig_prog_proba, clear_figure=True)
fig_line_class = plot_line_by_class_class_mean(df_sel)
st.pyplot(fig_line_class, clear_figure=True)
fig_line_proba = plot_line_by_proba_class_mean(df_sel)
st.pyplot(fig_line_proba, clear_figure=True)

if show_student_plots:
    fig_students = plot_per_student_lines(df_sel)
    st.pyplot(fig_students, clear_figure=True)

# Top 10 îmbunătățiri
st.subheader("🏅 Top 10 îmbunătățiri (Bac - Evaluare) în selecția curentă")
df_sel["Progres_Bac_minus_Evaluare"] = as_number(df_sel["Bacalaureat"]) - as_number(df_sel["Evaluare"])
top_df = (df_sel
          .sort_values("Progres_Bac_minus_Evaluare", ascending=False)
          .loc[:, ["Nume", "Clasa", "Proba", "Evaluare", "Simulare", "Bacalaureat", "Progres_Bac_minus_Evaluare"]]
          .head(10))
st.dataframe(top_df, use_container_width=True)

# Heatmap progres Clasă x Probă
st.subheader("🗺️ Heatmap Progres (Bac - Evaluare) pe Clasă x Probă")
fig_heatmap = heatmap_progress_class_proba(df_sel)
st.pyplot(fig_heatmap, clear_figure=True)

# Scatter plots interactive
st.subheader("🔵 Distribuția notelor pe etape – pe clase")
fig_scatter_class = plot_scatter_by_group(df_sel, group_col="Clasa", title="Distribuția notelor pe clase")
st.pyplot(fig_scatter_class, clear_figure=True)

st.subheader("🔵 Distribuția notelor pe etape – pe probe")
fig_scatter_proba = plot_scatter_by_group(df_sel, group_col="Proba", title="Distribuția notelor pe probe")
st.pyplot(fig_scatter_proba, clear_figure=True)

# Tabel cu toți elevii
if show_all_students:
    st.subheader("👩‍🎓👨‍🎓 Tabel cu toți elevii (seleția curentă)")
    st.dataframe(df_sel.sort_values(["Clasa", "Proba", "Nume"]), use_container_width=True)

st.markdown("---")
# st.caption("Notă: Progres calculat cu metoda diferenței mediilor claselor. Valorile non-numerice sunt ignorate (NaN).")
