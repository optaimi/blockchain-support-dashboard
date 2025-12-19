# NodeGuard Pro 🛡️

**NodeGuard Pro** is an AI-powered Tier 3 Support Dashboard designed to automate root-cause analysis for blockchain infrastructure issues. It acts as an intelligent layer between support engineers and raw JSON-RPC logs, capable of diagnosing complex EVM errors, checking endpoint health, and generating production-ready fix scripts.

![Dashboard Demo](https://via.placeholder.com/800x400.png?text=NodeGuard+Pro+Dashboard+Preview)

## 🚀 Features

- **Automated Root Cause Analysis:** Instantly translates vague error messages (e.g., `-32000 execution reverted`) into technical explanations.
- **Infrastructure Health Checks:** Live latency and block height monitoring for QuickNode/EVM endpoints.
- **Smart Log Parsing:** Ingests `.json`, `.log`, and `.txt` files to identify specific JSON-RPC error codes (429, 413, -32601).
- **Auto-Remediation Scripts:** Automatically generates Python scripts (using `web3.py`) to fix user code errors, such as implementing backoff strategies or batching.
- **Bug Ticket Generation:** drafts formal bug reports with Severity, Category, and Description suitable for Jira/Linear.

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Intelligence:** OpenAI `gpt-4.1-mini`
- **Connectivity:** Python `requests` & `httpx`
- **Environment:** `python-dotenv`

## 📦 Installation

1.  **Clone the repository**

    ```bash
    git clone https://github.com/optaimi/blockchain-support-dashboard
    cd nodeguard-pro
    ```

2.  **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**
    Create a `.env` file in the root directory:
    ```ini
    # .env
    OPENAI_API_KEY="sk-..."
    QUICKNODE_RPC_URL="https://your-endpoint.quicknode.pro/..."
    ```

## ⚡ Usage

1.  **Run the Dashboard**

    ```bash
    streamlit run app.py
    ```

2.  **Workflow**
    - **Status Check:** Verify your endpoint status in the sidebar.
    - **Input:** Paste a customer support ticket or error description.
    - **Upload:** Attach relevant log files.
    - **Analyse:** Click "Analyse Support Request" to generate a diagnosis, bug report, and fix script.

## 📄 License

This project is open-source and available under the MIT License.
