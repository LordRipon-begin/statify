import streamlit as st
import pandas as pd
# ← ADD THIS RIGHT HERE, after imports, before anything else

STAT_TOOLS = {
    "Descriptive Statistics": {
        "fields": []
    },
    "Correlation Analysis": {
        "fields": [
            {"key": "method", "label": "Method", "type": "select",
             "options": ["pearson", "spearman", "kendall"]}
        ]
    },
    "Hypothesis Testing (t-test)": {
        "fields": [
            {"key": "confidence", "label": "Confidence Level", "type": "select",
             "options": ["0.90", "0.95", "0.99"]},
            {"key": "tail", "label": "Tail", "type": "select",
             "options": ["two-tailed", "one-tailed (left)", "one-tailed (right)"]}
        ]
    },
    "Linear Regression": {
        "fields": [
            {"key": "target", "label": "Target Variable (Y)", "type": "text"}
        ]
    },
    "ANOVA": {
        "fields": [
            {"key": "confidence", "label": "Confidence Level", "type": "select",
             "options": ["0.90", "0.95", "0.99"]}
        ]
    },
}


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Statify",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Session state bootstrap ───────────────────────────────────────────────────
if "df"       not in st.session_state: st.session_state.df       = None
if "page"     not in st.session_state: st.session_state.page     = 1
if "filename" not in st.session_state: st.session_state.filename = ""
if "p3_blocks" not in st.session_state:
    st.session_state.p3_blocks = []

if "p3_active_block" not in st.session_state:
    st.session_state.p3_active_block = 0

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0a0f;
    color: #f0ede8;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    max-width: 680px !important;
    padding-top: 3rem !important;
    padding-bottom: 4rem !important;
}
.statify-logo {
    font-family: 'Syne', sans-serif;
    font-size: 3.2rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: #f0ede8;
    line-height: 1;
    margin-bottom: 0.25rem;
}
.statify-logo span { color: #c8f55a; }
.statify-sub {
    font-size: 1rem;
    font-weight: 300;
    color: #7c7a75;
    margin-bottom: 2.5rem;
}
.upload-label {
    font-size: 0.72rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #7c7a75;
    margin-bottom: 0.5rem;
}
.status-card {
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    font-size: 0.9rem;
    margin: 0.75rem 0;
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
}
.status-success { background:#0f1f05; border:1px solid #3a5c10; color:#c8f55a; }
.status-error   { background:#1f0505; border:1px solid #5c1010; color:#f55a5a; }
.status-idle    { background:#13131a; border:1px solid #2a2a35; color:#7c7a75; }
.stat-row { display:flex; gap:0.6rem; margin-top:0.5rem; flex-wrap:wrap; }
.stat-pill {
    background:#1a1a24; border:1px solid #2a2a35; border-radius:20px;
    padding:0.25rem 0.75rem; font-size:0.78rem; color:#c8f55a;
}
/* Default button style */
.stButton > button {
    background: #c8f55a !important;
    color: #0a0a0f !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.7rem 2rem !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: opacity 0.15s !important;
    margin-top: 0.5rem !important;
}
.stButton > button:hover    { opacity: 0.88 !important; }
.stButton > button:disabled { background:#1e1e28 !important; color:#3a3a48 !important; cursor:not-allowed !important; }
[data-testid="stFileUploader"] {
    background:#13131a !important; border:1.5px dashed #2a2a3a !important; border-radius:12px !important;
}
[data-testid="stFileUploader"]:hover { border-color:#c8f55a !important; }
.divider { border:none; border-top:1px solid #1e1e28; margin:1.5rem 0; }

/* Edit panel toggle buttons */
.edit-btn-on  > div > button { background:#c8f55a !important; color:#0a0a0f !important; font-weight:700 !important; }
.edit-btn-off > div > button { background:#13131a !important; color:#f0ede8 !important; border:1.5px solid #2a2a35 !important; }

/* SAVE active / inactive */
.save-on  > div > button { background:#c8f55a !important; color:#0a0a0f !important; font-weight:700 !important; }
.save-off > div > button { background:#1e1e28 !important; color:#3a3a48 !important; border:1px solid #2a2a35 !important; pointer-events:none !important; cursor:not-allowed !important; }

/* Cell label above each input in edit panel */
.cell-lbl {
    font-size:0.62rem; font-weight:700; text-transform:uppercase;
    letter-spacing:0.09em; color:#7c7a75; margin-bottom:3px; white-space:nowrap;
}
</style>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═════════════════════════════════════════════════════════════════════════════

def validate_csv(uploaded_file):
    """Read CSV with utf-8 fallback to latin1. Returns (df, status, message)."""
    df = None
    try:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding="utf-8")
    except UnicodeDecodeError:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding="latin1")
        except Exception:
            return None, "error", "Could not read file. Make sure it is a valid CSV."
    except Exception:
        return None, "error", "Could not read file. Make sure it is a valid CSV."

    if df is None or df.empty:
        return None, "error", "File is empty. Please upload a CSV with data."
    if len(df.columns) < 2:
        return None, "error", "File must have at least 2 columns."

    df.columns = df.columns.str.strip()
    df = df.reset_index(drop=True)   # guarantee clean 0-based index internally
    return df, "success", ""


def cast(val, dtype):
    """Safely cast edited string back to a column's original dtype."""
    if str(val).strip() == "":
        if pd.api.types.is_integer_dtype(dtype): return pd.NA
        if pd.api.types.is_float_dtype(dtype):   return float("nan")
        return pd.NA
    try:
        if pd.api.types.is_integer_dtype(dtype): return int(float(val))
        if pd.api.types.is_float_dtype(dtype):   return float(val)
    except (ValueError, TypeError):
        pass
    return val


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 1 — UPLOAD
# ═════════════════════════════════════════════════════════════════════════════

def render_page1():
    st.markdown('<div class="statify-logo">Stati<span>fy</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="statify-sub">Upload your dataset to begin analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="upload-label">Your dataset</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        label="Upload CSV",
        type=["csv"],
        label_visibility="collapsed",
        key="csv_uploader",
    )

    df = None

    if uploaded is None:
        st.markdown(
            '<div class="status-card status-idle">○&nbsp; No file selected — upload a .csv file to continue</div>',
            unsafe_allow_html=True,
        )
    else:
        df, status, error_msg = validate_csv(uploaded)

        if status == "success":
            rows, cols = df.shape
            missing = int(df.isna().sum().sum())
            st.markdown(
                f'<div class="status-card status-success">✓&nbsp; <div>'
                f'<strong>{uploaded.name}</strong> uploaded successfully'
                f'<div class="stat-row">'
                f'<span class="stat-pill">{rows} rows</span>'
                f'<span class="stat-pill">{cols} columns</span>'
                f'<span class="stat-pill">{missing} missing values</span>'
                f'</div></div></div>',
                unsafe_allow_html=True,
            )
            # Preview with 1-based index
            st.markdown('<div class="upload-label" style="margin-top:1rem">Preview — first 5 rows</div>', unsafe_allow_html=True)
            preview = df.head(5).copy()
            preview.index = range(1, len(preview) + 1)   # ← index starts at 1
            st.dataframe(preview, use_container_width=True, hide_index=False)
        else:
            st.markdown(
                f'<div class="status-card status-error">✕&nbsp; {error_msg}</div>',
                unsafe_allow_html=True,
            )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    if st.button("Statify It →", disabled=(df is None), key="statify_btn"):
        st.session_state.df       = df
        st.session_state.filename = uploaded.name
        st.session_state.page     = 2
        st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# PAGE 2 — EDIT DATA
# ═════════════════════════════════════════════════════════════════════════════

def render_page2():

    # ── Guard ─────────────────────────────────────────────────────────────────
    if st.session_state.df is None:
        st.markdown('<div class="status-card status-error">✕&nbsp; No data. Go back and upload a file.</div>', unsafe_allow_html=True)
        if st.button("BACK", key="p2_guard_back"):
            st.session_state.page = 1
            st.rerun()
        return

    # ── Init session keys ─────────────────────────────────────────────────────
    if "df_edit"        not in st.session_state:
        st.session_state.df_edit = st.session_state.df.copy().reset_index(drop=True)
    if "p2_show_row"    not in st.session_state: st.session_state.p2_show_row    = False
    if "p2_show_col"    not in st.session_state: st.session_state.p2_show_col    = False
    if "p2_has_changes" not in st.session_state: st.session_state.p2_has_changes = False
    if "p2_row_sel"     not in st.session_state: st.session_state.p2_row_sel     = None
    if "p2_col_sel"     not in st.session_state: st.session_state.p2_col_sel     = None

    df = st.session_state.df_edit   # always 0-based internally

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown('<div class="statify-logo" style="font-size:2.2rem">Edit Your <span>Data</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="upload-label">Step 2 of 5 — Review and clean your dataset</div>', unsafe_allow_html=True)

    n_rows, n_cols = df.shape
    n_missing = int(df.isna().sum().sum())
    st.markdown(
        f'<div class="stat-row" style="margin-bottom:1.5rem">'
        f'<span class="stat-pill">{n_rows} rows</span>'
        f'<span class="stat-pill">{n_cols} columns</span>'
        f'<span class="stat-pill" style="color:{"#f55a5a" if n_missing>0 else "#c8f55a"}">'
        f'{"⚠ "+str(n_missing)+" missing" if n_missing>0 else "✓ No missing"}'
        f'</span></div>',
        unsafe_allow_html=True,
    )

    # ── READ-ONLY PREVIEW — index starts at 1 ────────────────────────────────
    st.markdown('<div class="upload-label">Preview (read-only)</div>', unsafe_allow_html=True)
    preview_df = df.copy()
    preview_df.index = range(1, len(preview_df) + 1)   # show 1-based
    st.dataframe(preview_df, use_container_width=True, hide_index=False)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div class="upload-label">Edit mode</div>', unsafe_allow_html=True)

    # ── TOGGLE BUTTONS — light on / light off ────────────────────────────────
    # Each button toggles its own panel. Selecting one does NOT close the other.
    b1, b2, _ = st.columns([1, 1, 2])

    with b1:
        row_cls = "edit-btn-on" if st.session_state.p2_show_row else "edit-btn-off"
        st.markdown(f'<div class="{row_cls}">', unsafe_allow_html=True)
        if st.button("Edit Row", key="p2_toggle_row"):
            st.session_state.p2_show_row    = not st.session_state.p2_show_row
            st.session_state.p2_has_changes = False
        st.markdown('</div>', unsafe_allow_html=True)

    with b2:
        col_cls = "edit-btn-on" if st.session_state.p2_show_col else "edit-btn-off"
        st.markdown(f'<div class="{col_cls}">', unsafe_allow_html=True)
        if st.button("Edit Column", key="p2_toggle_col"):
            st.session_state.p2_show_col    = not st.session_state.p2_show_col
            st.session_state.p2_has_changes = False
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

        # ══════════════════════════════════════════════════════════════════════════
    # EDIT ROW MODE
    # ══════════════════════════════════════════════════════════════════════════
    if st.session_state.p2_mode == "row":

        # FIX 1 + FIX 3: rows labelled 1..N (no "Row 0"); selecting row N loads df.iloc[N-1]
        row_options = ["Row 0 — Column Names"] + [f"Row {i+1}" for i in range(len(df))]

        # FIX 3: use index= to always control which option is shown
        current_sel = st.session_state.p2_selection
        if current_sel not in row_options:
            current_sel = row_options[0]

        selected = st.selectbox(
            "Select row",
            options=row_options,
            index=row_options.index(current_sel),
            label_visibility="collapsed",
            key="p2_row_selector",
        )

        # FIX 3: reset change flag when selection actually changes
        if st.session_state.p2_selection != selected:
            st.session_state.p2_selection = selected
            st.session_state.p2_has_changes = False
            # Clear per-cell widget keys so new data loads cleanly
            for k in list(st.session_state.keys()):
                if k.startswith("p2_rowval_") or k.startswith("p2_colname_"):
                    del st.session_state[k]
            st.rerun()

        st.markdown(f'<div class="upload-label" style="margin-top:1rem">Editing: {selected}</div>', unsafe_allow_html=True)

        # ── Row 0: edit column names ──────────────────────────────────────────
        if selected == "Row 0 — Column Names":
            col_list = df.columns.tolist()
            ui_cols = st.columns(len(col_list))
            new_names = []
            for i, col_name in enumerate(col_list):
                with ui_cols[i]:
                    st.markdown(f'<div class="cell-label">Col {i+1}</div>', unsafe_allow_html=True)
                    val = st.text_input(
                        f"cn_{i}",
                        value=col_name,
                        label_visibility="collapsed",
                        key=f"p2_colname_{i}",
                    )
                    new_names.append(val.strip())

            has_changes = new_names != col_list
            st.session_state.p2_has_changes = has_changes

        # ── Normal data row ───────────────────────────────────────────────────
        else:
            # FIX 1+3: "Row 1" → iloc[0], "Row 2" → iloc[1], etc.
            row_num = int(selected.split(" ")[1])   # 1-based number from label
            row_idx = row_num - 1                   # 0-based index into df
            row_data = df.iloc[row_idx]
            col_list = df.columns.tolist()

            ui_cols = st.columns(len(col_list))
            edited_vals = {}
            original_vals = {}

            for i, col_name in enumerate(col_list):
                with ui_cols[i]:
                    current = row_data[col_name]
                    display = "" if pd.isna(current) else str(current)
                    original_vals[col_name] = display
                    st.markdown(f'<div class="cell-label">{col_name}</div>', unsafe_allow_html=True)
                    new_val = st.text_input(
                        f"rv_{i}",
                        value=display,
                        label_visibility="collapsed",
                        key=f"p2_rowval_{i}",
                    )
                    edited_vals[col_name] = new_val

            has_changes = edited_vals != original_vals
            st.session_state.p2_has_changes = has_changes

        # ── Save button ───────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        save_class = "save-active" if st.session_state.p2_has_changes else "save-inactive"
        st.markdown(f'<div class="{save_class}">', unsafe_allow_html=True)
        save_clicked = st.button("💾  Save", key="p2_save_row", disabled=not st.session_state.p2_has_changes)
        st.markdown('</div>', unsafe_allow_html=True)

        if save_clicked:
            if selected == "Row 0 — Column Names":
                if any(n == "" for n in new_names):
                    st.error("Column names cannot be empty.")
                elif len(new_names) != len(set(new_names)):
                    st.error("Duplicate column names found. Each must be unique.")
                else:
                    rename_map = dict(zip(col_list, new_names))
                    st.session_state.df_edit = df.rename(columns=rename_map)
                    st.session_state.p2_saved = True
                    st.session_state.p2_has_changes = False
                    st.success("✓ Column names updated.")
                    st.rerun()
            else:
                new_df = df.copy()
                for col_name, new_val in edited_vals.items():
                    dtype = df[col_name].dtype
                    try:
                        if pd.api.types.is_integer_dtype(dtype):
                            new_df.at[row_idx, col_name] = int(new_val) if new_val != "" else pd.NA
                        elif pd.api.types.is_float_dtype(dtype):
                            new_df.at[row_idx, col_name] = float(new_val) if new_val != "" else float("nan")
                        else:
                            new_df.at[row_idx, col_name] = new_val if new_val != "" else pd.NA
                    except (ValueError, TypeError):
                        new_df.at[row_idx, col_name] = new_val
                st.session_state.df_edit = new_df
                st.session_state.p2_saved = True
                st.session_state.p2_has_changes = False
                st.success(f"✓ Row {row_num} saved.")
                st.rerun()

                # ══════════════════════════════════════════════════════════════════════════
    # EDIT COLUMN MODE
    # ══════════════════════════════════════════════════════════════════════════
    elif st.session_state.p2_mode == "col":

        col_options = df.columns.tolist()
        current_col = st.session_state.p2_selection

        # Default to first column if nothing valid is selected
        if current_col not in col_options:
            current_col = col_options[0]

        selected_col = st.selectbox(
            "Select column",
            options=col_options,
            index=col_options.index(current_col),
            label_visibility="collapsed",
            key="p2_col_selector",
        )

        # Reset editor when selected column changes
        if st.session_state.p2_selection != selected_col:
            st.session_state.p2_selection = selected_col
            st.session_state.p2_has_changes = False

            # Clear previous column editor widget states
            for k in list(st.session_state.keys()):
                if k.startswith("p2_colval_"):
                    del st.session_state[k]

            st.rerun()

        st.markdown(
            f'<div class="upload-label" style="margin-top:1rem">'
            f'Editing column: {selected_col} — {len(df)} values</div>',
            unsafe_allow_html=True,
        )

        col_data = df[selected_col]
        edited_col = {}
        original_col = {}

        # Safe column identifier for widget keys
        safe_col_key = "".join(ch if ch.isalnum() else "_" for ch in str(selected_col))

        # ── Vertical editor: each row gets [Row label | text input] ──────────
        st.markdown("""
        <style>
        .col-edit-row {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 6px;
        }
        .col-edit-label {
            min-width: 70px;
            font-size: 0.72rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #7c7a75;
        }
        </style>
         """, unsafe_allow_html=True)

        for i in range(len(df)):
            current = col_data.iloc[i]
            display = "" if pd.isna(current) else str(current)
            original_col[i] = display

            label_col, input_col = st.columns([1, 5])

            with label_col:
                st.markdown(
                    f'<div class="cell-label" style="margin-top:12px">Row {i+1}</div>',
                    unsafe_allow_html=True,
                )

            with input_col:
                new_val = st.text_input(
                    f"cv_{i}",
                    value=display,
                    label_visibility="collapsed",
                    key=f"p2_colval_{safe_col_key}_{i}",
                )

            edited_col[i] = new_val

        has_changes = edited_col != original_col
        st.session_state.p2_has_changes = has_changes

        # ── Save button ───────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        save_class = "save-active" if st.session_state.p2_has_changes else "save-inactive"
        st.markdown(f'<div class="{save_class}">', unsafe_allow_html=True)
        save_clicked = st.button(
            "💾  Save",
            key="p2_save_col",
            disabled=not st.session_state.p2_has_changes,
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if save_clicked:
            new_df = df.copy()
            dtype = df[selected_col].dtype
            col_idx = new_df.columns.get_loc(selected_col)

            for i, new_val in edited_col.items():
                try:
                    if pd.api.types.is_integer_dtype(dtype):
                        new_df.iloc[i, col_idx] = int(new_val) if new_val != "" else pd.NA
                    elif pd.api.types.is_float_dtype(dtype):
                        new_df.iloc[i, col_idx] = float(new_val) if new_val != "" else float("nan")
                    else:
                        new_df.iloc[i, col_idx] = new_val if new_val != "" else pd.NA
                except (ValueError, TypeError):
                    new_df.iloc[i, col_idx] = new_val

            st.session_state.df_edit = new_df
            st.session_state.p2_saved = True
            st.session_state.p2_has_changes = False
            st.success(f"✓ Column '{selected_col}' saved.")
            st.rerun()   



 
#--------page3--------
def render_page3():
    if st.session_state.df is None:
        st.markdown('<div class="status-card status-error">✕ No data. Go back.</div>', unsafe_allow_html=True)
        if st.button("← Back", key="p3_guard"):
            st.session_state.page = 2; st.rerun()
        return

    df = st.session_state.df
    all_cols = df.columns.tolist()
    blocks = st.session_state.p3_blocks
    active = st.session_state.p3_active_block
    MAX_BLOCKS = 5

    # ── Header ────────────────────────────────────────────────────────────
    st.markdown('<div class="statify-logo" style="font-size:2.2rem">Configure <span>Analysis</span></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="upload-label">Step 3 of 5 — Build up to {MAX_BLOCKS} analysis configurations</div>', unsafe_allow_html=True)

    # Progress pills for saved blocks
    if blocks:
        pills = "".join([
            f'<span class="stat-pill" style="color:#c8f55a">✓ Block {i+1}</span>'
            for i in range(len(blocks))
        ])
        st.markdown(f'<div class="stat-row" style="margin-bottom:1rem">{pills}</div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Active block editor ───────────────────────────────────────────────
    block_num = active + 1  # 1-based for display
    st.markdown(f'<div class="upload-label">Block {block_num} of {MAX_BLOCKS}</div>', unsafe_allow_html=True)

    # A. Variable selection
    st.markdown("**Select Variables**", unsafe_allow_html=False)
    selected_vars = st.multiselect(
        "Choose one or more columns",
        options=all_cols,
        default=None,
        label_visibility="collapsed",
        key=f"p3_vars_{active}",
    )

    # B. Tool selection
    st.markdown("**Select Statistical Tools**")
    selected_tools = st.multiselect(
        "Choose tools to apply",
        options=list(STAT_TOOLS.keys()),
        default=None,
        label_visibility="collapsed",
        key=f"p3_tools_{active}",
    )

    # C. Dynamic config per tool
    tool_configs = {}
    if selected_tools:
        st.markdown("**Configure Tools**")
        for tool in selected_tools:
            fields = STAT_TOOLS[tool]["fields"]
            if not fields:
                st.markdown(f'<div class="status-card status-idle">ℹ {tool} — no extra configuration needed.</div>', unsafe_allow_html=True)
                continue
            with st.expander(f"⚙ {tool}", expanded=True):
                cfg = {}
                for field in fields:
                    if field["type"] == "select":
                        cfg[field["key"]] = st.selectbox(
                            field["label"],
                            options=field["options"],
                            key=f"p3_{active}_{tool}_{field['key']}",
                        )
                    elif field["type"] == "text":
                        cfg[field["key"]] = st.text_input(
                            field["label"],
                            key=f"p3_{active}_{tool}_{field['key']}",
                        )
                tool_configs[tool] = cfg

    # D. Save block button
    st.markdown("<br>", unsafe_allow_html=True)
    can_save = bool(selected_vars and selected_tools)
    save_class = "save-active" if can_save else "save-inactive"
    st.markdown(f'<div class="{save_class}">', unsafe_allow_html=True)
    if st.button(f"💾 Save Block {block_num}", key=f"p3_save_{active}", disabled=not can_save):
        config = {
            "block": block_num,
            "variables": selected_vars,
            "tools": selected_tools,
            "tool_configs": tool_configs,
        }
        # Replace or append
        if active < len(blocks):
            blocks[active] = config
        else:
            blocks.append(config)
        st.session_state.p3_blocks = blocks
        st.success(f"✓ Block {block_num} saved.")

        # Auto-advance to next block if under limit
        if active + 1 < MAX_BLOCKS:
            st.session_state.p3_active_block = active + 1
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Saved blocks summary (collapsible) ───────────────────────────────
    if blocks:
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown('<div class="upload-label">Saved Configurations</div>', unsafe_allow_html=True)
        for i, b in enumerate(blocks):
            with st.expander(f"Block {b['block']} — {', '.join(b['variables'][:3])}{'...' if len(b['variables'])>3 else ''}", expanded=False):
                st.markdown(f"**Variables:** {', '.join(b['variables'])}")
                st.markdown(f"**Tools:** {', '.join(b['tools'])}")
                for tool, cfg in b["tool_configs"].items():
                    if cfg:
                        st.markdown(f"*{tool}:* " + ", ".join(f"{k}={v}" for k, v in cfg.items()))
                if st.button(f"✎ Edit Block {b['block']}", key=f"p3_edit_{i}"):
                    st.session_state.p3_active_block = i
                    st.rerun()

    # ── Navigation ────────────────────────────────────────────────────────
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    col_back, col_next = st.columns([1, 2])

    with col_back:
        if st.button("← Back", key="p3_back"):
            st.session_state.page = 2
            st.rerun()

    with col_next:
        can_proceed = len(blocks) >= 1
        proceed_class = "save-active" if can_proceed else "save-inactive"
        st.markdown(f'<div class="{proceed_class}">', unsafe_allow_html=True)
        if st.button("Next → Run Analysis", key="p3_next", disabled=not can_proceed):
            st.session_state.page = 4
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# ROUTER
# ═════════════════════════════════════════════════════════════════════════════

if st.session_state.page == 1:
    render_page1()

elif st.session_state.page == 2:
    render_page2()

elif st.session_state.page == 3:
    render_page3()

elif st.session_state.page >= 4:
    st.markdown('<div class="statify-logo" style="font-size:2rem">Analysis <span>Ready</span></div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="status-card status-success">✓ {len(st.session_state.p3_blocks)} configuration(s) queued.</div>',
        unsafe_allow_html=True,
    )
    if st.button("← Back to Configure"):
        st.session_state.page = 3
        st.rerun()