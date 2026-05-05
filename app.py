import streamlit as st
import pandas as pd

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Statify",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Session state bootstrap ───────────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = None
if "page" not in st.session_state:
    st.session_state.page = 1
if "filename" not in st.session_state:
    st.session_state.filename = ""

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
    max-width: 640px !important;
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
    font-family: 'DM Sans', sans-serif;
    font-size: 1rem;
    font-weight: 300;
    color: #7c7a75;
    margin-bottom: 2.5rem;
    letter-spacing: 0.01em;
}

.upload-label {
    font-family: 'DM Sans', sans-serif;
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
    font-family: 'DM Sans', sans-serif;
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
}
.status-success { background: #0f1f05; border: 1px solid #3a5c10; color: #c8f55a; }
.status-error   { background: #1f0505; border: 1px solid #5c1010; color: #f55a5a; }
.status-idle    { background: #13131a; border: 1px solid #2a2a35; color: #7c7a75; }

.stat-row { display: flex; gap: 0.6rem; margin-top: 0.5rem; flex-wrap: wrap; }
.stat-pill {
    background: #1a1a24;
    border: 1px solid #2a2a35;
    border-radius: 20px;
    padding: 0.25rem 0.75rem;
    font-size: 0.78rem;
    color: #c8f55a;
    font-family: 'DM Sans', sans-serif;
}

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
.stButton > button:hover { opacity: 0.88 !important; }
.stButton > button:disabled {
    background: #1e1e28 !important;
    color: #3a3a48 !important;
    cursor: not-allowed !important;
}

[data-testid="stFileUploader"] {
    background: #13131a !important;
    border: 1.5px dashed #2a2a3a !important;
    border-radius: 12px !important;
    padding: 0.5rem !important;
}
[data-testid="stFileUploader"]:hover { border-color: #c8f55a !important; }

.divider { border: none; border-top: 1px solid #1e1e28; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)


# ── Helper ────────────────────────────────────────────────────────────────────
def validate_csv(uploaded_file):
    df = None
    try:
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding="utf-8")
    except UnicodeDecodeError:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding="latin1")
        except Exception:
            return None, "error", "Could not read the file. Make sure it is a valid CSV."
    except Exception:
        return None, "error", "Could not read the file. Make sure it is a valid CSV."

    if df is None or df.empty:
        return None, "error", "The file is empty. Please upload a CSV with data."
    if len(df.columns) < 2:
        return None, "error", "The file must have at least 2 columns."

    df.columns = df.columns.str.strip()
    return df, "success", ""


# ── Page 1 ────────────────────────────────────────────────────────────────────
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

            st.markdown('<div class="upload-label" style="margin-top:1rem">Preview — first 5 rows</div>', unsafe_allow_html=True)

            # FIX 1: index from 1 in preview
            preview = df.head(5).copy()
            preview.index = range(1, len(preview) + 1)
            st.dataframe(preview, use_container_width=True)
        else:
            st.markdown(
                f'<div class="status-card status-error">✕&nbsp; {error_msg}</div>',
                unsafe_allow_html=True,
            )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    if st.button("Statify It →", disabled=(df is None), key="statify_btn"):
        st.session_state.df = df
        st.session_state.filename = uploaded.name
        st.session_state.page = 2
        st.rerun()


# ── Page 2 ────────────────────────────────────────────────────────────────────
def render_page2():
    if st.session_state.df is None:
        st.markdown('<div class="status-card status-error">✕&nbsp; No data found. Go back and upload a file.</div>', unsafe_allow_html=True)
        if st.button("← Back to Upload", key="p2_guard_back"):
            st.session_state.page = 1
            st.rerun()
        return

    # Session state init
    if "df_edit" not in st.session_state:
        st.session_state.df_edit = st.session_state.df.copy()
    if "p2_mode" not in st.session_state:
        st.session_state.p2_mode = None        # None | "row" | "col"
    if "p2_selection" not in st.session_state:
        st.session_state.p2_selection = None
    if "p2_saved" not in st.session_state:
        st.session_state.p2_saved = False
    if "p2_has_changes" not in st.session_state:
        st.session_state.p2_has_changes = False

    df = st.session_state.df_edit

    # Page 2 CSS
    st.markdown("""
    <style>
    .hscroll { overflow-x: auto; -webkit-overflow-scrolling: touch; padding-bottom: 8px; }
    .hscroll-inner { display: flex; flex-direction: row; gap: 10px; min-width: max-content; padding: 4px 2px; }
    .cell-box { display: flex; flex-direction: column; min-width: 110px; max-width: 140px; }
    .cell-label {
        font-size: 0.68rem; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.08em; color: #7c7a75; margin-bottom: 4px;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .save-active > button { background: #c8f55a !important; color: #0a0a0f !important; }
    .save-inactive > button {
        background: #1e1e28 !important; color: #3a3a48 !important;
        cursor: not-allowed !important; pointer-events: none !important;
    }

    /* FIX 2: Edit mode toggle buttons — OFF state (default) */
    div[data-testid="column"] .stButton > button {
        border: 1.5px solid #2a2a35 !important;
        background: #13131a !important;
        color: #f0ede8 !important;
        font-size: 0.88rem !important;
        padding: 0.5rem 1rem !important;
    }
    div[data-testid="column"] .stButton > button:hover {
        border-color: #c8f55a !important;
        color: #c8f55a !important;
    }

    /* FIX 2: Active/ON state for edit buttons */
    .btn-active-row div[data-testid="column"]:nth-child(1) .stButton > button,
    .btn-active-col div[data-testid="column"]:nth-child(2) .stButton > button {
        background: #c8f55a !important;
        color: #0a0a0f !important;
        border-color: #c8f55a !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown('<div class="statify-logo" style="font-size:2.2rem">Edit Your <span>Data</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="upload-label">Step 2 of 5 — Review and clean your dataset</div>', unsafe_allow_html=True)

    n_rows, n_cols = df.shape
    n_missing = int(df.isna().sum().sum())
    st.markdown(
        f'<div class="stat-row" style="margin-bottom:1.5rem">'
        f'<span class="stat-pill">{n_rows} rows</span>'
        f'<span class="stat-pill">{n_cols} columns</span>'
        f'<span class="stat-pill" style="color:{"#f55a5a" if n_missing>0 else "#c8f55a"}">'
        f'{"⚠ "+str(n_missing)+" missing" if n_missing>0 else "✓ No missing values"}'
        f'</span></div>',
        unsafe_allow_html=True,
    )

    # FIX 1: index from 1 in page 2 preview
    st.markdown('<div class="upload-label">Preview (read-only)</div>', unsafe_allow_html=True)
    display_df = df.copy()
    display_df.index = range(1, len(display_df) + 1)
    st.dataframe(display_df, use_container_width=True, hide_index=False)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── FIX 2: Toggle-style Edit buttons ─────────────────────────────────────
    st.markdown('<div class="upload-label">Select edit mode</div>', unsafe_allow_html=True)

    # Wrap in a div that CSS can target for active state
    active_class = ""
    if st.session_state.p2_mode == "row":
        active_class = "btn-active-row"
    elif st.session_state.p2_mode == "col":
        active_class = "btn-active-col"

    st.markdown(f'<div class="{active_class}">', unsafe_allow_html=True)
    btn_col1, btn_col2, _ = st.columns([1, 1, 2])

    with btn_col1:
        row_label = "✎  Edit Row  ✓" if st.session_state.p2_mode == "row" else "✎  Edit Row"
        if st.button(row_label, key="btn_mode_row"):
            # Toggle: if already in row mode → turn off, else turn on
            if st.session_state.p2_mode == "row":
                st.session_state.p2_mode = None
            else:
                st.session_state.p2_mode = "row"
            st.session_state.p2_selection = None
            st.session_state.p2_has_changes = False
            st.rerun()

    with btn_col2:
        col_label = "⊟  Edit Col  ✓" if st.session_state.p2_mode == "col" else "⊟  Edit Column"
        if st.button(col_label, key="btn_mode_col"):
            # Toggle: if already in col mode → turn off, else turn on
            if st.session_state.p2_mode == "col":
                st.session_state.p2_mode = None
            else:
                st.session_state.p2_mode = "col"
            st.session_state.p2_selection = None
            st.session_state.p2_has_changes = False
            st.rerun()

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
        if current_col not in col_options:
            current_col = col_options[0]

        selected_col = st.selectbox(
            "Select column",
            options=col_options,
            index=col_options.index(current_col),
            label_visibility="collapsed",
            key="p2_col_selector",
        )

        # FIX 3: reset when selection changes
        if st.session_state.p2_selection != selected_col:
            st.session_state.p2_selection = selected_col
            st.session_state.p2_has_changes = False
            for k in list(st.session_state.keys()):
                if k.startswith("p2_colval_"):
                    del st.session_state[k]
            st.rerun()

        st.markdown(
            f'<div class="upload-label" style="margin-top:1rem">Editing column: {selected_col} — {len(df)} values</div>',
            unsafe_allow_html=True,
        )

        col_data = df[selected_col]
        edited_col = {}
        original_col = {}

        # FIX 1: show row labels as 1-based
        ui_cols = st.columns(len(df))
        for i in range(len(df)):
            with ui_cols[i]:
                current = col_data.iloc[i]
                display = "" if pd.isna(current) else str(current)
                original_col[i] = display
                st.markdown(f'<div class="cell-label">Row {i+1}</div>', unsafe_allow_html=True)
                new_val = st.text_input(
                    f"cv_{i}",
                    value=display,
                    label_visibility="collapsed",
                    key=f"p2_colval_{i}",
                )
                edited_col[i] = new_val

        has_changes = edited_col != original_col
        st.session_state.p2_has_changes = has_changes

        # ── Save button ───────────────────────────────────────────────────────
      # ── Save button ───────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        save_class = "save-active" if has_changes else "save-inactive"
        st.markdown(f'<div class="{save_class}">', unsafe_allow_html=True)
        save_clicked = st.button("💾  Save", key="p2_save_col", disabled=not has_changes)
        st.markdown('</div>', unsafe_allow_html=True)

        if save_clicked:
            new_df = df.copy()
            dtype = df[selected_col].dtype
            for i, new_val in edited_col.items():
                try:
                    if pd.api.types.is_integer_dtype(dtype):
                        new_df.iloc[i, new_df.columns.get_loc(selected_col)] = int(new_val) if new_val != "" else pd.NA
                    elif pd.api.types.is_float_dtype(dtype):
                        new_df.iloc[i, new_df.columns.get_loc(selected_col)] = float(new_val) if new_val != "" else float("nan")
                    else:
                        new_df.iloc[i, new_df.columns.get_loc(selected_col)] = new_val if new_val != "" else pd.NA
                except (ValueError, TypeError):
                    new_df.iloc[i, new_df.columns.get_loc(selected_col)] = new_val
            st.session_state.df_edit = new_df
            st.session_state.p2_saved = True
            st.session_state.p2_has_changes = False
            st.success(f"✓ Column '{selected_col}' saved.")
            st.rerun()

    # ── No mode selected ──────────────────────────────────────────────────────
    else:
        st.markdown(
            '<div class="status-card status-idle">ℹ&nbsp; Click <b>Edit Row</b> or <b>Edit Column</b> above to start editing.</div>',
            unsafe_allow_html=True,
        )

    # ── Navigation ────────────────────────────────────────────────────────────
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    col_back, col_next = st.columns([1, 1])

    with col_back:
        if st.button("← Back", key="p2_back"):
            for key in ["df_edit", "p2_mode", "p2_selection", "p2_saved", "p2_has_changes"]:
                st.session_state.pop(key, None)
            st.session_state.page = 1
            st.rerun()

    with col_next:
        if st.button("Next →", key="p2_next"):
            st.session_state.df = st.session_state.df_edit.copy()
            for key in ["p2_mode", "p2_selection", "p2_saved", "p2_has_changes"]:
                st.session_state.pop(key, None)
            st.session_state.page = 3
            st.rerun()


# ── Router ────────────────────────────────────────────────────────────────────
if st.session_state.page == 1:
    render_page1()

elif st.session_state.page == 2:
    render_page2()

elif st.session_state.page >= 3:
    st.markdown('<div class="statify-logo" style="font-size:2rem">Data <span>Saved</span></div>', unsafe_allow_html=True)
    r, c = st.session_state.df.shape
    st.markdown(
        f'<div class="status-card status-success">✓&nbsp; Working dataset ready — {r} rows × {c} columns</div>',
        unsafe_allow_html=True,
    )
    display_df = st.session_state.df.head().copy()
    display_df.index = range(1, len(display_df) + 1)
    st.dataframe(display_df, use_container_width=True)
    if st.button("Back to Edit Data"):
        st.session_state.page = 2
        st.rerun()