import os
import sqlite3
import html
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# ── Load env ──────────────────────────────────────────────────────────
load_dotenv()

_default_db = str(Path(__file__).resolve().parent.parent / "app" / "attacks.db")
DB_PATH = os.getenv("DB_PATH", _default_db)

# ── Page config ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="SentinelTrap SOC Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.shields.io/badge/SentinelTrap-SOC%20Panel-blue?style=for-the-badge&logo=shield")
    st.markdown("---")
    st.markdown("**Services**")
    st.success("✅ Dashboard: Online")
    st.info("🔗 Flask Honeypot → :5000")
    st.markdown("---")
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    st.markdown("---")
    st.caption("⚠️ For authorized security research only.")

# ── Header ────────────────────────────────────────────────────────────
st.title("[SOC] SentinelTrap Dashboard")
st.markdown("**Real-time honeypot attack monitoring & threat analysis panel**")
st.markdown("---")

# ── Data loading ──────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def load_attacks() -> pd.DataFrame:
    if not os.path.exists(DB_PATH):
        return pd.DataFrame(columns=["ID", "Endpoint", "Attack Type", "IP", "Payload", "Timestamp"])
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT id, endpoint, attack_type, ip, payload, timestamp "
        "FROM attacks ORDER BY timestamp DESC",
        conn,
    )
    conn.close()
    df.columns = ["ID", "Endpoint", "Attack Type", "IP", "Payload", "Timestamp"]
    # Sanitize displayed output
    df["Payload"] = df["Payload"].apply(lambda x: html.escape(str(x))[:200])
    df["IP"] = df["IP"].apply(lambda x: html.escape(str(x)))
    return df


df = load_attacks()

# ── Metrics ───────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Attacks", len(df))
with col2:
    st.metric("SQL Injection", len(df[df["Attack Type"] == "SQLi"]) if not df.empty else 0)
with col3:
    st.metric("XSS", len(df[df["Attack Type"] == "XSS"]) if not df.empty else 0)
with col4:
    other = len(df[~df["Attack Type"].isin(["SQLi", "XSS"])]) if not df.empty else 0
    st.metric("Scanner / Other", other)

st.markdown("---")

# ── Attack table ──────────────────────────────────────────────────────
if not df.empty:
    st.subheader("🔴 Recent Attacks")
    st.dataframe(df, hide_index=True, use_container_width=True)

    st.subheader("📊 Attack Type Distribution")
    chart_data = df["Attack Type"].value_counts().reset_index()
    chart_data.columns = ["Attack Type", "Count"]
    st.bar_chart(chart_data.set_index("Attack Type"))
else:
    st.info("No attacks logged yet. Send requests to the honeypot to start collecting data.")

st.markdown("---")
st.caption(f"Last refreshed: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
