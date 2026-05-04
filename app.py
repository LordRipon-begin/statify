import streamlit as st
import pandas as pd

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Statify",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Session state bootstrap ───────────────────────────────────────────────────
# These keys persist across reruns and (later) across pages
if "df" not in st.session_state:
    st.session_state.df = None          # will hold the pandas DataFrame
if "page" not in st.session_state:
    st.session_state.page = 1           # current page number
if "filename" not in st.session_state:
    st.session_state.filename = ""      # original file name for display

# ── CSS styling ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* Reset & base */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0a0f;
    color: #f0ede8;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    max-width: 640px !important;
    padding-top: 3rem !important;
    padding-bottom: 4rem !important;
}

/* Logo / title */
.statify-logo {
    font-family: 'Syne', sans-serif;
    font-size: 3.2rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: #f0ede8;
    line-height: 1;
    margin-bottom: 0.25rem;
}
.statify-logo span {
    color: #c8f55a;   /* acid green accent */
}
.statify-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem;
    font-weight: 300;
    color: #7c7a75;
    margin-bottom: 2.5rem;
    letter-spacing: 0.01em;
}

/* Upload zone */
.upload-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.72rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #7c7a75;
    margin-bottom: 0.5rem;
}

/* Status cards */
.status-card {
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    font-size: 0.9rem;
    margin: 0.75rem 0;
    font-family: 'DM Sans', sans-serif;
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
}
.status-success {
    background: #0f1f05;
    border: 1px solid #3a5c10;
    color: #c8f55a;
}
.status-error {
    background: #1f0505;
    border: 1px solid #5c1010;
    color: #f55a5a;
}
.status-idle {
    background: #13131a;
    border: 1px solid #2a2a35;
    color: #7c7a75;
}

/* Stat pills */
.stat-row {
    display: flex;
    gap: 0.6rem;
    margin-top: 0.5rem;
    flex-wrap: wrap;
}
.stat-pill {
    background: #1a1a24;
    border: 1px solid #2a2a35;
    border-radius: 20px;
    padding: 0.25rem 0.75rem;
    font-size: 0.78rem;
    color: #c8f55a;
    font-family: 'DM Sans', sans-serif;
}

/* Primary button */
.stButton > button {
    background: #c8f55a !important;
    color: #0a0a0f !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.03em !important;
    padding: 0.7rem 2rem !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: opacity 0.15s !important;
    margin-top: 0.5rem !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
}
.stButton > button:disabled {
    background: #1e1e28 !important;
    color: #3a3a48 !important;
    cursor: not-allowed !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #13131a !important;
    border: 1.5px dashed #2a2a3a !important;
    border-radius: 12px !important;
    padding: 0.5rem !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #c8f55a !important;
}

/* Divider */
.divider {
    border: none;
    border-top: 1px solid #1e1e28;
    margin: 1.5rem 0;
}
</style>
""", unsafe_allow_html=True)


# ── Helper: validate the uploaded file ───────────────────────────────────────
def validate_csv(uploaded_file) -> tuple[pd.DataFrame | None, str, str]:
    """
    Try to read and validate the uploaded file.

    Returns
    -------
    df       : DataFrame if valid, else None
    status   : 'success' | 'error'
    message  : human-readable feedback
    """
    try:
        df = pd.read_csv(uploaded_file)
    except Exception:
        return None, "error", "Could not read the file. Make sure it is a valid CSV."

    if df.empty:
        return None, "error", "The file is empty. Please upload a CSV with data."

    if len(df.columns) < 2:
        return None, "error", "The file must have at least 2 columns."

    return df, "success", ""


# ── Page 1 renderer ───────────────────────────────────────────────────────────
def render_page1():
    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="statify-logo">Stati<span>fy</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="statify-sub">Upload your dataset to begin analysis</div>',
        unsafe_allow_html=True,
    )

    # ── File uploader ─────────────────────────────────────────────────────────
    st.markdown('<div class="upload-label">Your dataset</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        label="Upload CSV",          # required by Streamlit
        type=["csv"],                # only accept .csv
        label_visibility="collapsed",
        key="csv_uploader",
    )

    # ── Validation & status display ───────────────────────────────────────────
    df = None  # local variable; only saved to session on button click

    if uploaded is None:
        # Nothing uploaded yet
        st.markdown(
            '<div class="status-card status-idle">'
            '○&nbsp; No file selected — upload a .csv file to continue'
            '</div>',
            unsafe_allow_html=True,
        )

    else:
        # File received — validate it
        df, status, error_msg = validate_csv(uploaded)

        if status == "success":
            rows, cols = df.shape
            missing = int(df.isna().sum().sum())

            # Success card with file stats
            st.markdown(
                f'<div class="status-card status-success">'
                f'✓&nbsp; <div>'
                f'<strong>{uploaded.name}</strong> uploaded successfully'
                f'<div class="stat-row">'
                f'<span class="stat-pill">{rows} rows</span>'
                f'<span class="stat-pill">{cols} columns</span>'
                f'<span class="stat-pill">{missing} missing values</span>'
                f'</div></div></div>',
                unsafe_allow_html=True,
            )

        else:
            # Error card
            st.markdown(
                f'<div class="status-card status-error">'
                f'✕&nbsp; {error_msg}'
                '</div>',
                unsafe_allow_html=True,
            )

    # ── Statify It button ─────────────────────────────────────────────────────
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Button is disabled when no valid dataframe is ready
    button_disabled = (df is None)

    if st.button(
        "Statify It →",
        disabled=button_disabled,
        key="statify_btn",
    ):
        # Save everything to session state and move to next page
        st.session_state.df = df
        st.session_state.filename = uploaded.name
        st.session_state.page = 2
        st.rerun()  # triggers a rerun so the page change takes effect immediately


# ── Router ────────────────────────────────────────────────────────────────────
# Later you will add: elif st.session_state.page == 2: render_page2() etc.

if st.session_state.page == 1:
    render_page1()

elif st.session_state.page == 2:
    # Placeholder — Page 2 will be built next
    st.markdown("### ✅ File loaded. Page 2 coming next!")
    st.write(f"**File:** {st.session_state.filename}")
    st.write(f"**Shape:** {st.session_state.df.shape}")
    st.dataframe(st.session_state.df.head())

    if st.button("← Back to Upload"):
        st.session_state.page = 1
        st.rerun()
      
