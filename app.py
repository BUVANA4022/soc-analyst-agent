import streamlit as st
import requests
import time

# Page Configuration
st.set_page_config(page_title="SOC Analyst Terminal", layout="wide", page_icon="🛡️")

# API Configuration - Internal Docker network uses port 8000 for the FastAPI brain
API_URL = "http://localhost:8000"

# --- CUSTOM CSS FOR PROFESSIONAL LOOK ---
st.markdown("""
    <style>
    /* Dark Terminal Background */
    .stCode {
        background-color: #0e1117 !important;
        color: #00ff00 !important;
        border: 2px solid #1f2937;
        border-radius: 5px;
    }
    /* Metric styling */
    [data-testid="stMetricValue"] {
        color: #60a5fa;
    }
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #111827;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ CyberSentinel: SOC Incident Response")
st.markdown("---")

# --- SIDEBAR: ENVIRONMENT CONTROL ---
st.sidebar.header("🕹️ Environment Control")
task = st.sidebar.selectbox("Select Mission", ["easy", "medium", "hard"])

if st.sidebar.button("Reset Environment", use_container_width=True):
    try:
        res = requests.post(f"{API_URL}/reset?task_id={task}")
        st.session_state.obs = res.json()
        st.session_state.history = [] # Clear history on reset
        st.sidebar.success(f"Mission {task.upper()} Initialized!")
    except Exception as e:
        st.sidebar.error(f"Error connecting to Brain: {e}")

st.sidebar.markdown("---")
st.sidebar.info("""
**Mission Intelligence:**
- **Easy**: Signature analysis.
- **Medium**: Lateral movement trace.
- **Hard**: Full remediation & block.
""")

# --- MAIN LAYOUT ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💻 System Console")
    
    if "obs" not in st.session_state:
        st.info("⚠️ System Offline. Please use the sidebar to 'Reset Environment' and begin the mission.")
    else:
        # The Styled Terminal Output
        st.code(st.session_state.obs['terminal_output'], language="bash")
        
        # Action Input Form
        with st.form("action_form", clear_on_submit=True):
            st.write("📤 **Send Command to Agent**")
            c1, c2 = st.columns([1, 2])
            with c1:
                cmd = st.text_input("Command", placeholder="e.g., ps")
            with c2:
                args = st.text_input("Arguments", placeholder="e.g., 4022 (comma separated)")
            
            submit = st.form_submit_button("Execute Action", use_container_width=True)
            
            if submit and cmd:
                arg_list = [a.strip() for a in args.split(",")] if args else []
                payload = {"command": cmd, "args": arg_list}
                
                try:
                    res = requests.post(f"{API_URL}/step", json=payload)
                    st.session_state.obs = res.json()
                    
                    # Track history
                    if "history" not in st.session_state:
                        st.session_state.history = []
                    st.session_state.history.append(f"> {cmd} {args}")
                    
                    st.rerun()
                except Exception as e:
                    st.error(f"API Connection Lost: {e}")

    # Command History Log
    if "history" in st.session_state and st.session_state.history:
        with st.expander("📜 Action History Log", expanded=False):
            for h in st.session_state.history:
                st.text(h)

with col2:
    st.subheader("📊 System Telemetry")
    
    if "obs" in st.session_state:
        obs = st.session_state.obs
        
        # Visual Metrics
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Reward Score", f"{obs['reward']:.2f}")
        with m2:
            status_color = "green" if obs['system_status'] == "Remediated" else "orange"
            st.markdown(f"**Status:** :{status_color}[{obs['system_status']}]")
        
        # Alerts Section
        st.markdown("---")
        st.write("**Active Security Alerts:**")
        if not obs['active_alerts']:
            st.success("✅ No active threats detected.")
        else:
            for alert in obs['active_alerts']:
                st.error(f"🔥 {alert}")
        
        # Progress Bar (Visualizing the path to 1.0 reward)
        st.write("**Task Completion Progress**")
        st.progress(min(max(obs['reward'], 0.0), 1.0))
