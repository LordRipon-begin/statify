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
    # EDIT ROW PANEL (shown only when p2_show_row is True)
    # ══════════════════════════════════════════════════════════════════════════
    if st.session_state.p2_show_row:

        st.markdown('<div class="upload-label">— Edit Row</div>', unsafe_allow_html=True)

        # Row 0 = column/variable names | Row 1..N = data rows (1-based for user)
        row_options = ["Row 0 — Column Names"] + [f"Row {i}" for i in range(1, len(df) + 1)]

        selected_row = st.selectbox(
            "Select row",
            options=row_options,
            label_visibility="collapsed",
            key="p2_row_selector",
        )

        # Reset change flag only when user picks a DIFFERENT row
        if st.session_state.p2_row_sel != selected_row:
            st.session_state.p2_row_sel     = selected_row
            st.session_state.p2_has_changes = False

        col_list = df.columns.tolist()
        ui       = st.columns(len(col_list))

        # ── Row 0: variable names ─────────────────────────────────────────────
        if selected_row == "Row 0 — Column Names":
            new_names = []
            for i, col_name in enumerate(col_list):
                with ui[i]:
                    st.markdown(f'<div class="cell-lbl">Col {i+1}</div>', unsafe_allow_html=True)
                    v = st.text_input("_", value=col_name,
                                      label_visibility="collapsed",
                                      key=f"p2_ri_{i}")
                    new_names.append(v.strip())
            st.session_state.p2_has_changes = (new_names != col_list)

        # ── Data row — KEY FIX ────────────────────────────────────────────────
        # "Row 5" → user_num=5 → iloc[4]
        # Always use iloc (position-based), never loc (label-based)
        else:
            user_num     = int(selected_row.split(" ")[1])   # e.g. 5
            row_idx      = user_num - 1                       # iloc index: 4
            row_data     = df.iloc[row_idx]                   # ← FIXED: iloc

            original_map = {c: ("" if pd.isna(row_data[c]) else str(row_data[c])) for c in col_list}
            edited_map   = {}

            for i, col_name in enumerate(col_list):
                with ui[i]:
                    st.markdown(f'<div class="cell-lbl">{col_name}</div>', unsafe_allow_html=True)
                    v = st.text_input("_", value=original_map[col_name],
                                      label_visibility="collapsed",
                                      key=f"p2_ri_{i}")
                    edited_map[col_name] = v

            st.session_state.p2_has_changes = (edited_map != original_map)

        # ── SAVE button ───────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        sc = "save-on" if st.session_state.p2_has_changes else "save-off"
        st.markdown(f'<div class="{sc}">', unsafe_allow_html=True)
        save_row = st.button("SAVE", key="p2_save_row", disabled=not st.session_state.p2_has_changes)
        st.markdown('</div>', unsafe_allow_html=True)

        if save_row:
            if selected_row == "Row 0 — Column Names":
                if any(n == "" for n in new_names):
                    st.error("Column names cannot be empty.")
                elif len(new_names) != len(set(new_names)):
                    st.error("Duplicate column names found.")
                else:
                    st.session_state.df_edit    = df.rename(columns=dict(zip(col_list, new_names)))
                    st.session_state.p2_has_changes = False
                    st.success("Column names saved.")
                    st.rerun()
            else:
                new_df = df.copy()
                for col_name, val in edited_map.items():
                    col_pos = col_list.index(col_name)
                    new_df.iat[row_idx, col_pos] = cast(val, df[col_name].dtype)
                st.session_state.df_edit    = new_df.reset_index(drop=True)
                st.session_state.p2_has_changes = False
                st.success(f"Row {user_num} saved.")
                st.rerun()

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # EDIT COLUMN PANEL (shown only when p2_show_col is True)
    # ══════════════════════════════════════════════════════════════════════════
    if st.session_state.p2_show_col:

        st.markdown('<div class="upload-label">— Edit Column</div>', unsafe_allow_html=True)

        selected_col = st.selectbox(
            "Select column",
            options=df.columns.tolist(),
            label_visibility="collapsed",
            key="p2_col_selector",
        )

        # Reset change flag only when column changes
        if st.session_state.p2_col_sel != selected_col:
            st.session_state.p2_col_sel     = selected_col
            st.session_state.p2_has_changes = False

        n_vals = len(df)
        st.markdown(f'<div class="upload-label" style="margin-top:0.5rem">{selected_col} — {n_vals} values (scroll →)</div>', unsafe_allow_html=True)

        col_data     = df[selected_col]
        # Use integer position i (0-based) everywhere — no raw index labels
        original_col = {i: ("" if pd.isna(col_data.iat[i]) else str(col_data.iat[i])) for i in range(n_vals)}
        edited_col   = {}

        ui = st.columns(n_vals)
        for i in range(n_vals):
            with ui[i]:
                st.markdown(f'<div class="cell-lbl">Row {i+1}</div>', unsafe_allow_html=True)
                v = st.text_input("_", value=original_col[i],
                                  label_visibility="collapsed",
                                  key=f"p2_cv_{i}")
                edited_col[i] = v

        st.session_state.p2_has_changes = (edited_col != original_col)

        # ── SAVE button ───────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        sc = "save-on" if st.session_state.p2_has_changes else "save-off"
        st.markdown(f'<div class="{sc}">', unsafe_allow_html=True)
        save_col = st.button("SAVE", key="p2_save_col", disabled=not st.session_state.p2_has_changes)
        st.markdown('</div>', unsafe_allow_html=True)

        if save_col:
            new_df  = df.copy()
            col_pos = df.columns.tolist().index(selected_col)
            dtype   = df[selected_col].dtype
            for i, val in edited_col.items():
                new_df.iat[i, col_pos] = cast(val, dtype)
            st.session_state.df_edit    = new_df.reset_index(drop=True)
            st.session_state.p2_has_changes = False
            st.success(f"Column '{selected_col}' saved.")
            st.rerun()

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── No panel open ─────────────────────────────────────────────────────────
    if not st.session_state.p2_show_row and not st.session_state.p2_show_col:
        st.markdown(
            '<div class="status-card status-idle">○&nbsp; Click <b>Edit Row</b> or <b>Edit Column</b> to open the editing panel.</div>',
            unsafe_allow_html=True,
        )

    # ── Navigation ────────────────────────────────────────────────────────────
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])

    with c1:
        if st.button("BACK", key="p2_back"):
            for k in ["df_edit","p2_show_row","p2_show_col","p2_has_changes","p2_row_sel","p2_col_sel"]:
                st.session_state.pop(k, None)
            st.session_state.page = 1
            st.rerun()

    with c2:
        if st.button("NEXT", key="p2_next"):
            st.session_state.df = st.session_state.df_edit.copy().reset_index(drop=True)
            for k in ["p2_show_row","p2_show_col","p2_has_changes","p2_row_sel","p2_col_sel"]:
                st.session_state.pop(k, None)
            st.session_state.page = 3
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