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
    Attempts utf-8 first, falls back to latin1 if that fails.

    Returns
    -------
    df       : DataFrame if valid, else None
    status   : 'success' | 'error'
    message  : human-readable feedback
    """
    df = None

    # ── Step 1: try reading with utf-8 encoding ───────────────────────────────
    try:
        uploaded_file.seek(0)           # reset pointer to start of file
        df = pd.read_csv(uploaded_file, encoding="utf-8")
    except UnicodeDecodeError:
        # utf-8 failed — try latin1 (handles most European special characters)
        try:
            uploaded_file.seek(0)       # reset pointer again before retry
            df = pd.read_csv(uploaded_file, encoding="latin1")
        except Exception:
            return None, "error", "Could not read the file. Make sure it is a valid CSV."
    except Exception:
        return None, "error", "Could not read the file. Make sure it is a valid CSV."

    # ── Step 2: validate the dataframe ───────────────────────────────────────
    if df is None or df.empty:
        return None, "error", "The file is empty. Please upload a CSV with data."

    if len(df.columns) < 2:
        return None, "error", "The file must have at least 2 columns."

    # Strip whitespace from column names (common formatting issue)
    df.columns = df.columns.str.strip()

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

            # Preview — first 5 rows so user confirms it loaded correctly
            st.markdown(
                '<div class="upload-label" style="margin-top:1rem">Preview — first 5 rows</div>',
                unsafe_allow_html=True,
            )
            st.dataframe(df.head(5), use_container_width=True)

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



# ── Page 2: Edit Your Data ────────────────────────────────────────────────────
def render_page2():

    # ── Guard ─────────────────────────────────────────────────────────────────
    if st.session_state.df is None:
        st.markdown('<div class="status-card status-error">&#10005;&nbsp; No data found. Go back and upload a file.</div>', unsafe_allow_html=True)
        if st.button("BACK", key="p2_guard_back"):
            st.session_state.page = 1
            st.rerun()
        return

    # ── Session state init ────────────────────────────────────────────────────
    if "df_edit"        not in st.session_state: st.session_state.df_edit        = st.session_state.df.copy()
    if "p2_has_changes" not in st.session_state: st.session_state.p2_has_changes = False
    if "p2_saved"       not in st.session_state: st.session_state.p2_saved       = False
    if "p2_selection"   not in st.session_state: st.session_state.p2_selection   = None

    df = st.session_state.df_edit

    # ── CSS ───────────────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    .hcell-label {
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.09em;
        color: #7c7a75;
        margin-bottom: 3px;
        white-space: nowrap;
    }
    div.save-btn-active > div > button {
        background: #c8f55a !important;
        color: #0a0a0f !important;
        font-weight: 700 !important;
    }
    div.save-btn-inactive > div > button {
        background: #1e1e28 !important;
        color: #3a3a48 !important;
        border: 1px solid #2a2a35 !important;
        pointer-events: none !important;
        cursor: not-allowed !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown('<div class="statify-logo" style="font-size:2.2rem">Edit Your <span>Data</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="upload-label">Step 2 of 5 &mdash; Review and clean your dataset</div>', unsafe_allow_html=True)

    n_rows, n_cols = df.shape
    n_missing = int(df.isna().sum().sum())
    st.markdown(
        f'<div class="stat-row" style="margin-bottom:1.5rem">'
        f'<span class="stat-pill">{n_rows} rows</span>'
        f'<span class="stat-pill">{n_cols} columns</span>'
        f'<span class="stat-pill" style="color:{"#f55a5a" if n_missing>0 else "#c8f55a"}">'
        f'{"&#9888; "+str(n_missing)+" missing" if n_missing>0 else "&#10003; No missing"}'
        f'</span></div>',
        unsafe_allow_html=True,
    )

    # ── READ-ONLY PREVIEW — index starts at 1 ────────────────────────────────
    st.markdown('<div class="upload-label">Preview (read-only)</div>', unsafe_allow_html=True)
    preview_df = df.copy()
    preview_df.index = range(1, len(preview_df) + 1)
    st.dataframe(preview_df, use_container_width=True, hide_index=False)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── EDIT MODE — radio buttons ─────────────────────────────────────────────
    st.markdown('<div class="upload-label">Select edit mode</div>', unsafe_allow_html=True)
    edit_mode = st.radio(
        "edit_mode",
        options=["Edit Row", "Edit Column"],
        horizontal=True,
        label_visibility="collapsed",
        key="p2_edit_mode",
    )

    # Reset change tracking when mode switches
    if st.session_state.p2_selection != edit_mode:
        st.session_state.p2_selection   = edit_mode
        st.session_state.p2_has_changes = False

    st.markdown("<br>", unsafe_allow_html=True)

    # helper: safely cast string → original dtype
    def cast(val, dtype):
        if val == "":
            if pd.api.types.is_integer_dtype(dtype): return pd.NA
            if pd.api.types.is_float_dtype(dtype):   return float("nan")
            return pd.NA
        try:
            if pd.api.types.is_integer_dtype(dtype): return int(val)
            if pd.api.types.is_float_dtype(dtype):   return float(val)
        except (ValueError, TypeError):
            pass
        return val

    # ══════════════════════════════════════════════════════════════════════════
    # EDIT ROW MODE
    # ══════════════════════════════════════════════════════════════════════════
    if edit_mode == "Edit Row":

        # Row 0 = column names | Row 1..N = data rows (1-based, matches preview)
        row_options = ["Row 0 — Column Names"] + [f"Row {i}" for i in range(1, len(df) + 1)]

        selected = st.selectbox(
            "Select row to edit",
            options=row_options,
            label_visibility="collapsed",
            key="p2_row_selector",
        )

        st.markdown(f'<div class="upload-label" style="margin-top:1rem">Editing: {selected}</div>', unsafe_allow_html=True)
        col_list = df.columns.tolist()
        ui       = st.columns(len(col_list))

        # ── Row 0: edit column/variable names ─────────────────────────────────
        if selected == "Row 0 — Column Names":
            new_names = []
            for i, col_name in enumerate(col_list):
                with ui[i]:
                    st.markdown(f'<div class="hcell-label">Col {i+1}</div>', unsafe_allow_html=True)
                    v = st.text_input("_", value=col_name,
                                      label_visibility="collapsed",
                                      key=f"p2_ri_{i}")
                    new_names.append(v.strip())
            st.session_state.p2_has_changes = (new_names != col_list)

        # ── Data row (Row 1, Row 2 … matches preview numbering exactly) ───────
        else:
            # "Row 5" → df index 4  (user sees 1-based, Python uses 0-based)
            row_idx      = int(selected.split(" ")[1]) - 1
            row_data     = df.iloc[row_idx]
            original_map = {c: ("" if pd.isna(row_data[c]) else str(row_data[c])) for c in col_list}
            edited_map   = {}

            for i, col_name in enumerate(col_list):
                with ui[i]:
                    st.markdown(f'<div class="hcell-label">{col_name}</div>', unsafe_allow_html=True)
                    v = st.text_input("_", value=original_map[col_name],
                                      label_visibility="collapsed",
                                      key=f"p2_ri_{i}")
                    edited_map[col_name] = v

            st.session_state.p2_has_changes = (edited_map != original_map)

        # ── SAVE button ───────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        cls = "save-btn-active" if st.session_state.p2_has_changes else "save-btn-inactive"
        st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
        save_clicked = st.button("SAVE", key="p2_save_row",
                                 disabled=not st.session_state.p2_has_changes)
        st.markdown('</div>', unsafe_allow_html=True)

        if save_clicked:
            if selected == "Row 0 — Column Names":
                if any(n == "" for n in new_names):
                    st.error("Column names cannot be empty.")
                elif len(new_names) != len(set(new_names)):
                    st.error("Duplicate column names found.")
                else:
                    st.session_state.df_edit = df.rename(columns=dict(zip(col_list, new_names)))
                    st.session_state.p2_has_changes = False
                    st.session_state.p2_saved = True
                    st.success("Column names saved.")
                    st.rerun()
            else:
                new_df = df.copy()
                for col_name, val in edited_map.items():
                    new_df.at[row_idx, col_name] = cast(val, df[col_name].dtype)
                st.session_state.df_edit = new_df
                st.session_state.p2_has_changes = False
                st.session_state.p2_saved = True
                st.success(f"Row {row_idx + 1} saved.")
                st.rerun()

    # ══════════════════════════════════════════════════════════════════════════
    # EDIT COLUMN MODE
    # ══════════════════════════════════════════════════════════════════════════
    else:

        selected_col = st.selectbox(
            "Select column to edit",
            options=df.columns.tolist(),
            label_visibility="collapsed",
            key="p2_col_selector",
        )

        n_vals = len(df)
        st.markdown(f'<div class="upload-label" style="margin-top:1rem">Editing: {selected_col} &mdash; {n_vals} values</div>', unsafe_allow_html=True)

        col_data     = df[selected_col]
        original_col = {idx: ("" if pd.isna(col_data[idx]) else str(col_data[idx])) for idx in df.index}
        edited_col   = {}

        # All values in ONE horizontal row — labels show Row 1, Row 2 … (1-based)
        ui = st.columns(n_vals)
        for i, idx in enumerate(df.index):
            with ui[i]:
                st.markdown(f'<div class="hcell-label">Row {i+1}</div>', unsafe_allow_html=True)
                v = st.text_input("_", value=original_col[idx],
                                  label_visibility="collapsed",
                                  key=f"p2_cv_{idx}")
                edited_col[idx] = v

        st.session_state.p2_has_changes = (edited_col != original_col)

        # ── SAVE button ───────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        cls = "save-btn-active" if st.session_state.p2_has_changes else "save-btn-inactive"
        st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
        save_clicked = st.button("SAVE", key="p2_save_col",
                                 disabled=not st.session_state.p2_has_changes)
        st.markdown('</div>', unsafe_allow_html=True)

        if save_clicked:
            new_df = df.copy()
            dtype  = df[selected_col].dtype
            for idx, val in edited_col.items():
                new_df.at[idx, selected_col] = cast(val, dtype)
            st.session_state.df_edit = new_df
            st.session_state.p2_has_changes = False
            st.session_state.p2_saved = True
            st.success(f"Column '{selected_col}' saved.")
            st.rerun()

    # ── Navigation ────────────────────────────────────────────────────────────
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    c_back, c_next = st.columns([1, 1])

    with c_back:
        if st.button("BACK", key="p2_back"):
            for k in ["df_edit","p2_has_changes","p2_saved","p2_selection"]:
                st.session_state.pop(k, None)
            st.session_state.page = 1
            st.rerun()

    with c_next:
        if st.button("NEXT", key="p2_next"):
            st.session_state.df = st.session_state.df_edit.copy()
            for k in ["p2_has_changes","p2_saved","p2_selection"]:
                st.session_state.pop(k, None)
            st.session_state.page = 3
            st.rerun()
            



            

# ── Router ────────────────────────────────────────────────────────────────────
if st.session_state.page == 1:
    render_page1()

elif st.session_state.page == 2:
    render_page2()

elif st.session_state.page >= 3:
    # Placeholder — Page 3 coming next session
    st.markdown(
        '<div class="statify-logo" style="font-size:2rem">Data <span>Saved</span></div>',
        unsafe_allow_html=True,
    )
    r, c = st.session_state.df.shape
    st.markdown(
        f'<div class="status-card status-success">'
        f'&#10003;&nbsp; Working dataset ready &mdash; {r} rows x {c} columns'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.dataframe(st.session_state.df.head(), use_container_width=True)
    if st.button("Back to Edit Data"):
        st.session_state.page = 2
        st.rerun()
    
