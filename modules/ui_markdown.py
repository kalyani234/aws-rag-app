# Global CSS & minimal header/footer HTML

GLOBAL_CSS = """
<style>
  :root {
    --aws-bg:#0b0e11; --aws-panel:#111418; --aws-border:#1e2329;
    --aws-muted:#9aa4af; --aws-text:#e6edf3; --aws-orange:#ff9900;
  }
  .stApp,.main{background:var(--aws-bg)!important;color:var(--aws-text)!important}
  hr{border:0;border-top:1px solid var(--aws-border)}
  .aws-hero{margin:8px auto 16px;padding:18px 20px;max-width:1100px;
    background:linear-gradient(180deg,#0c1116 0%,#0b0e11 100%);
    border:1px solid var(--aws-border);border-radius:14px;box-shadow:0 8px 20px rgba(0,0,0,.25)}
  .aws-title{font-weight:800;margin:0}
  .aws-sub{color:var(--aws-muted);margin-top:6px;font-size:14px}
  [data-testid="stChatMessage"]{background:var(--aws-panel);border:1px solid var(--aws-border);
    border-radius:16px;box-shadow:0 6px 16px rgba(0,0,0,.2)}
  .stButton>button{background:linear-gradient(90deg,var(--aws-orange),#ffae33);
    color:#111!important;border:none;border-radius:10px;font-weight:700;padding:.55rem 1.1rem}
  section[data-testid="stSidebar"]{background:#0c1116;border-right:1px solid var(--aws-border)}
  .aws-side-title{color:var(--aws-orange);font-weight:800;margin-bottom:8px}
  .aws-footer{text-align:center;color:var(--aws-muted);font-size:13px}
</style>
"""

HEADER_HTML = """
<div class="aws-hero">
  <h2 class="aws-title">☁️ AWS RAG Assistant</h2>
  <p class="aws-sub">Ask questions about AWS architectures, data engineering, and cloud solutions.</p>
</div>
"""

FOOTER_HTML = """
<hr>
<div class="aws-footer">© 2025 AWS RAG Assistant · Powered by Amazon Bedrock</div>
"""
