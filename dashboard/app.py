import streamlit as st
import sqlite3
import os
import pandas as pd
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'app', 'attacks.db')

st.set_page_config(
    page_title='SentinelTrap SOC Dashboard',
    page_icon='🛡️',
    layout='wide',
    initial_sidebar_state='expanded'
)

st.title('[SOC] SentinelTrap Dashboard')
st.markdown('**Real-time honeypot attack monitoring & analysis panel**')

# ── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    st.header('🛡️ SentinelTrap')
    st.markdown('---')
    st.markdown('**Services**')
    st.success('✅ Dashboard: Online')
    st.info('🔗 Flask Honeypot: :5000')
    st.markdown('---')
    if st.button('🔄 Refresh Data'):
        st.cache_data.clear()
        st.rerun()

# ── Load data ─────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def load_attacks():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        'SELECT id, endpoint, attack_type, ip, payload, timestamp '
        'FROM attacks ORDER BY timestamp DESC',
        conn
    )
    conn.close()
    df.columns = ['ID', 'Endpoint', 'Attack Type', 'IP', 'Payload', 'Timestamp']
    return df

df = load_attacks()

# ── Metrics ───────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric('Total Attacks', len(df))
with col2:
    sqli_count = len(df[df['Attack Type'] == 'SQLi']) if not df.empty else 0
    st.metric('SQL Injection', sqli_count)
with col3:
    xss_count = len(df[df['Attack Type'] == 'XSS']) if not df.empty else 0
    st.metric('XSS', xss_count)
with col4:
    scanner_count = len(df[df['Attack Type'] == 'Scanner']) if not df.empty else 0
    st.metric('Scanner / Other', scanner_count)

st.markdown('---')

# ── Attack table ──────────────────────────────────────────────────────
if not df.empty:
    st.subheader('🔴 Recent Attacks')
    st.dataframe(df, hide_index=True, use_container_width=True)

    # ── Attack type distribution ──────────────────────────────────────
    st.subheader('📊 Attack Type Distribution')
    chart_data = df['Attack Type'].value_counts().reset_index()
    chart_data.columns = ['Attack Type', 'Count']
    st.bar_chart(chart_data.set_index('Attack Type'))
else:
    st.info('No attacks logged yet. Send requests to the honeypot to start collecting data.')

st.markdown('---')
st.caption(f"Last refreshed: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
