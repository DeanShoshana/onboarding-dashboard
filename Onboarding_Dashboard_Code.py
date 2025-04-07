import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Set Streamlit layout
st.set_page_config(layout="wide")

# Page title and description in Hebrew
st.title("📊 דשבורד ניתוח מקרי חוסר")
st.markdown("העלה קובץ T0 (ואופציונלית גם T1) לניתוח והשוואה. הדשבורד כולל מדדים, טבלאות וגרפים אינטראקטיביים.")

# File upload components for T0 and T1 (CSV or Excel)
uploaded_t0 = st.file_uploader("העלה קובץ T0", type=["csv", "xlsx"])
uploaded_t1 = st.file_uploader("העלה קובץ T1 (אופציונלי)", type=["csv", "xlsx"])

# Load file depending on format
def load_file(uploaded_file):
    if uploaded_file.name.endswith(".xlsx"):
        return pd.read_excel(uploaded_file)
    else:
        return pd.read_csv(uploaded_file)

# Process data and calculate metrics
def process_df(df):
    df = df.dropna(subset=["duration_hours", "polycount", "messages_sent"])
    df["duration_rounded"] = df["duration_hours"].round().astype(int)
    metrics = {}

    metrics["כמות ימים נבדקת"] = df["date"].nunique()
    metrics["סך מקרי חוסר"] = df["polycount"].sum()
    metrics["זמן תגובה ממוצע (שעות)"] = df["duration_hours"].mean()
    metrics["סך שעות חוסר"] = df["duration_hours"].sum()
    metrics["טווח שעות חוסר"] = df["duration_hours"].max() - df["duration_hours"].min()

    filtered = df[df["duration_hours"] > 1]
    if not filtered.empty:
        metrics["הקטגוריה עם הכי הרבה חוסרים"] = filtered["sub_category"].value_counts().idxmax()
        metrics["הקטגוריה עם הכי מעט חוסרים"] = filtered["sub_category"].value_counts().idxmin()

    filtered_date = df[df["duration_hours"] > 0]
    if not filtered_date.empty:
        metrics["היום עם הכי הרבה חוסרים"] = filtered_date["date"].value_counts().idxmax()
        metrics["היום עם הכי מעט חוסרים"] = filtered_date["date"].value_counts().idxmin()

    metrics["אחוז פתוחים אחרי שעה"] = round((df["duration_hours"] > 1).sum() / len(df) * 100, 2)
    metrics["כמות קטגוריות"] = df["category"].nunique()
    metrics["כמות תתי קטגוריות"] = df["sub_category"].nunique()
    metrics["כמות ערכים חסרים ב-polycount"] = df["polycount"].isnull().sum()
    metrics["אחוז חסרים ב-polycount"] = round(df["polycount"].isnull().sum() / len(df) * 100, 2)

    return df, metrics

# Display metrics in 3-column layout
def show_metrics(metrics, title):
    st.subheader(title)
    cols = st.columns(3)
    for i, (key, val) in enumerate(metrics.items()):
        with cols[i % 3]:
            st.metric(key, val)

# Generate summary tables and line charts for rounded hours
def summary_tables(df):
    st.subheader("📈 התפלגות לפי משך חוסר (שעות עגולות)")

    count_table = df.groupby("duration_rounded")["messages_sent"].sum().reset_index()
    count_table.columns = ["שעה עגולה", "כמות הודעות שנשלחו"]
    st.markdown("**טבלה 1 – הודעות לפי שעות חוסר עגולות**")
    st.dataframe(count_table, use_container_width=True)
    fig1 = px.line(count_table, x="שעה עגולה", y="כמות הודעות שנשלחו", markers=True)
    st.plotly_chart(fig1, use_container_width=True)

    poly_table = df.groupby("duration_rounded")["polycount"].sum().reset_index()
    poly_table.columns = ["שעה עגולה", "סך מקרי חוסר (polycount)"]
    st.markdown("**טבלה 2 – סכימת מקרי חוסר לפי שעות חוסר עגולות**")
    st.dataframe(poly_table, use_container_width=True)
    fig2 = px.line(poly_table, x="שעה עגולה", y="סך מקרי חוסר (polycount)", markers=True)
    st.plotly_chart(fig2, use_container_width=True)

# Main logic for displaying results
if uploaded_t0:
    df_t0 = load_file(uploaded_t0)
    df_t0, metrics_t0 = process_df(df_t0)

    if uploaded_t1:
        df_t1 = load_file(uploaded_t1)
        df_t1, metrics_t1 = process_df(df_t1)

        st.header("🔄 השוואה בין T0 ל-T1")

        comparison_df = pd.DataFrame({
            "מדד": metrics_t0.keys(),
            "T0": metrics_t0.values(),
            "T1": metrics_t1.values()
        })
        comparison_df["שינוי מספרי"] = comparison_df["T1"] - comparison_df["T0"]
        comparison_df["שינוי באחוזים"] = round(((comparison_df["T1"] - comparison_df["T0"]) / comparison_df["T0"]) * 100, 2)
        st.dataframe(comparison_df, use_container_width=True)
    else:
        show_metrics(metrics_t0, "📊 מדדים עבור קובץ T0")
        summary_tables(df_t0)
else:
    st.info("נא להעלות לפחות קובץ T0 כדי להתחיל.")
