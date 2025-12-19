import streamlit as st
import os
import json
import requests
import time
import re
from openai import OpenAI
from dotenv import load_dotenv

# --- 1. CONFIGURATION & SETUP ---
load_dotenv()

st.set_page_config(
    page_title="NodeGuard | Support Dashboard", page_icon="⚡", layout="wide"
)

# --- 2. CSS STYLING ---
st.markdown(
    """
    <style>
    .bug-card {
        background-color: #f9f9f9;
        border-left: 5px solid #673ab7;
        padding: 20px;
        border-radius: 8px;
        margin-top: 20px;
        color: #333;
    }
    .status-indicator {
        padding: 10px;
        border-radius: 5px;
        background-color: #f0f2f6;
        margin-bottom: 10px;
        font-weight: 500;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# --- 3. HELPER FUNCTIONS ---
def clean_json_output(raw_text):
    """Fallback mechanism to extract JSON from markdown."""
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        raise ValueError("The AI response could not be parsed as JSON.")


def check_rpc_status(url):
    """Pings the RPC endpoint to check health."""
    if not url:
        return False, "No URL Configured"
    try:
        start = time.time()
        payload = {"jsonrpc": "2.0", "method": "eth_blockNumber", "params": [], "id": 1}
        resp = requests.post(
            url, json=payload, headers={"Content-Type": "application/json"}, timeout=3
        )
        if resp.status_code == 200:
            lat = (time.time() - start) * 1000
            return True, f"{lat:.0f}ms"
        return False, f"HTTP {resp.status_code}"
    except Exception:
        return False, "Connection Failed"


def analyze_issue(client, model_id, desc, logs):
    """Sends the context to OpenAI."""
    # UPDATED PROMPT: Neutral persona, no specific company affiliation.
    system_prompt = """
    You are a Senior Blockchain Support Engineer.
    Analyze the technical issue and logs provided by the user.
    
    Output a STRICT JSON object with this schema:
    {
        "analysis_summary": "Technical root cause explanation.",
        "suggested_steps": ["Step 1", "Step 2", "Step 3"],
        "script_required": boolean,
        "python_script": "Full Python script code if needed, else null.",
        "bug_report": {
            "title": "Concise Bug Title",
            "description": "Formal description for the ticket.",
            "severity": "Integer 1-5 (1=Critical, 5=Minor)",
            "category": "Category String (e.g., API Error, Latency)"
        }
    }
    """

    user_content = f"""
    [ISSUE DESCRIPTION]
    {desc}

    [LOGS]
    {logs[:5000]}
    """

    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        return clean_json_output(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}


# --- 4. SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.header("🛡️ NodeGuard")

    # A. API Key Check
    env_key = os.environ.get("OPENAI_API_KEY", "")
    if env_key:
        st.success("🔑 OpenAI API Key: Loaded")
        api_key = env_key
    else:
        st.warning("⚠️ OpenAI API Key: Missing")
        api_key = st.text_input("Enter Key", type="password")

    # B. QuickNode RPC Status Check
    st.divider()
    st.markdown("### Infrastructure Status")

    rpc_url = os.environ.get("QUICKNODE_RPC_URL", "")

    if rpc_url:
        is_online, details = check_rpc_status(rpc_url)
        if is_online:
            st.markdown("🟢 **RPC Endpoint Online**")
            st.caption(f"Latency: {details}")
        else:
            st.markdown("🔴 **RPC Endpoint Offline**")
            st.caption(f"Error: {details}")
    else:
        st.info("⚪ RPC URL Not Configured")

    st.divider()
    if st.button("Refresh Status"):
        st.rerun()

# --- 5. MAIN INTERFACE ---
st.title("⚡ Blockchain Support Agent")
st.markdown("Provide the issue details below.")

st.subheader("1. Issue Description")
issue_desc = st.text_area(
    "Paste the customer's message or error description:",
    height=200,
    placeholder="e.g. Getting -32000 execution reverted on estimateGas...",
)

st.subheader("2. Upload Artifacts")
uploaded_log = st.file_uploader(
    "Upload Log File (txt/json/log)", type=["txt", "log", "json"]
)

# --- 6. EXECUTION LOGIC ---
if st.button("🚀 Analyse Support Request", type="primary", use_container_width=True):
    # Validation
    if not api_key:
        st.error("❌ OpenAI API Key is missing.")
        st.stop()

    if not issue_desc and not uploaded_log:
        st.warning("⚠️ Please provide an issue description or a log file.")
        st.stop()

    # Initialize Client
    try:
        client = OpenAI(api_key=api_key)
    except Exception as e:
        st.error(f"Failed to initialise OpenAI Client: {e}")
        st.stop()

    # Prepare Data
    log_text = ""
    if uploaded_log:
        log_text = uploaded_log.read().decode("utf-8")

    # --- RUN ANALYSIS ---
    # We use a status container for the 'processing' state
    result = None
    with st.status("🤖 Analysing...", expanded=True) as status:
        model_used = "gpt-4.1-mini"
        result = analyze_issue(client, model_used, issue_desc, log_text)

        if "error" in result:
            status.update(label="Analysis Failed", state="error")
            st.error("AI Error Occurred:")
            st.code(result["error"])
            st.stop()
        else:
            status.update(label="Analysis Complete", state="complete", expanded=False)

    # --- DISPLAY RESULTS ---
    if result:
        st.divider()

        # A. Summary
        st.subheader("🔍 Root Cause Analysis")
        st.info(result.get("analysis_summary", "No summary returned."))

        # B. Steps
        steps = result.get("suggested_steps", [])
        if steps:
            with st.expander("✅ Remediation Steps", expanded=True):
                for step in steps:
                    st.write(f"- {step}")

        # C. Bug Report
        report = result.get("bug_report", {})
        if report:
            sev_map = {
                1: "🔴 Critical",
                2: "🟠 High",
                3: "🟡 Medium",
                4: "🔵 Low",
                5: "⚪ Info",
            }

            st.markdown(
                f"""
            <div class="bug-card">
                <h3 style="margin-top:0; color:#673ab7;">🐛 {report.get("title", "Untitled")}</h3>
                <p><strong>Category:</strong> {report.get("category", "General")} | 
                   <strong>Severity:</strong> {sev_map.get(report.get("severity", 3), 3)}</p>
                <hr>
                <p>{report.get("description", "No description.")}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

        # D. Script
        if result.get("script_required") and result.get("python_script"):
            st.subheader("🐍 Fix Script")
            st.code(result["python_script"], language="python")
            st.download_button("Download Script", result["python_script"], "fix.py")