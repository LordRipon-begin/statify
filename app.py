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
    # ── Guard: must have data ─────────────────────────────────────────────────
    if st.session_state.df is None:
        st.markdown(
            '<div class="status-card status-error">'
            '&#10005;&nbsp; No data found. Please go back and upload a CSV file.'
            '</div>',
            unsafe_allow_html=True,
        )
        if st.button("Back to Upload", key="p2_back_guard"):
            st.session_state.page = 1
            st.rerun()
        return

    # Work on a dedicated edit copy so the original upload is preserved
    if "df_edit" not in st.session_state:
        st.session_state.df_edit = st.session_state.df.copy()

    df = st.session_state.df_edit

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="statify-logo" style="font-size:2.2rem">Edit Your <span>Data</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="upload-label">Step 2 of 5 &mdash; Review and clean your dataset</div>',
        unsafe_allow_html=True,
    )

    # Info pills
    n_rows, n_cols = df.shape
    n_missing = int(df.isna().sum().sum())
    missing_color = "#f55a5a" if n_missing > 0 else "#c8f55a"
    missing_icon  = "! " if n_missing > 0 else "ok "
    st.markdown(
        f'<div class="stat-row" style="margin-bottom:1.25rem">'
        f'<span class="stat-pill">{n_rows} rows</span>'
        f'<span class="stat-pill">{n_cols} columns</span>'
        f'<span class="stat-pill" style="color:{missing_color}">'
        f'{missing_icon}{n_missing} missing</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── Editable table ────────────────────────────────────────────────────────
    st.markdown(
        '<div class="upload-label">Edit cells directly &mdash; click any cell to change it</div>',
        unsafe_allow_html=True,
    )
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",   # lets user add / remove rows inside the table itself
        key="data_editor_p2",
    )
    # Persist every inline edit back to session immediately
    st.session_state.df_edit = edited_df.copy()
    df = st.session_state.df_edit   # keep local reference in sync

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Delete rows ───────────────────────────────────────────────────────────
    st.markdown('<div class="upload-label">Delete rows by index number</div>', unsafe_allow_html=True)

    rows_to_delete = st.multiselect(
        label="Select rows",
        options=df.index.tolist(),
        label_visibility="collapsed",
        placeholder="Select row numbers to delete...",
        key="rows_to_delete",
    )

    if st.button("Delete Selected Rows", key="btn_delete_rows"):
        if not rows_to_delete:
            st.warning("No rows selected. Pick at least one row number above.")
        elif len(rows_to_delete) >= len(df):
            st.error("Cannot delete all rows. Keep at least one.")
        else:
            st.session_state.df_edit = (
                df.drop(index=rows_to_delete).reset_index(drop=True)
            )
            st.success(f"Deleted {len(rows_to_delete)} row(s).")
            st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Add column ────────────────────────────────────────────────────────────
    st.markdown('<div class="upload-label">Add a new column</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns([2, 2])
    with col_a:
        new_col_name = st.text_input(
            "Column name",
            placeholder="e.g. FinalGrade",
            label_visibility="collapsed",
            key="new_col_name",
        )
    with col_b:
        new_col_default = st.text_input(
            "Default value",
            placeholder="Default value (e.g. 0 or N/A)",
            label_visibility="collapsed",
            key="new_col_default",
        )

    if st.button("Add Column", key="btn_add_col"):
        name = new_col_name.strip()
        if not name:
            st.error("Column name cannot be empty.")
        elif name in df.columns:
            st.error(f'A column named "{name}" already exists. Choose a different name.')
        else:
            # Store as number if possible, else as string
            try:
                default_val = float(new_col_default) if new_col_default.strip() else ""
            except ValueError:
                default_val = new_col_default.strip()
            st.session_state.df_edit[name] = default_val
            st.success(f'Column "{name}" added with default value: {default_val!r}')
            st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Drop columns ──────────────────────────────────────────────────────────
    st.markdown('<div class="upload-label">Remove columns</div>', unsafe_allow_html=True)

    cols_to_drop = st.multiselect(
        label="Select columns",
        options=df.columns.tolist(),
        label_visibility="collapsed",
        placeholder="Select columns to remove...",
        key="cols_to_drop",
    )

    if st.button("Drop Selected Columns", key="btn_drop_cols"):
        if not cols_to_drop:
            st.warning("No columns selected.")
        elif len(cols_to_drop) >= len(df.columns):
            st.error("Must keep at least one column.")
        else:
            st.session_state.df_edit = df.drop(columns=cols_to_drop)
            st.success(f"Removed {len(cols_to_drop)} column(s): {', '.join(cols_to_drop)}")
            st.rerun()

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Navigation: back + next ───────────────────────────────────────────────
    col_back, col_next = st.columns([1, 2])

    with col_back:
        if st.button("Back", key="p2_back"):
            # Clear edit copy so a fresh upload starts clean
            if "df_edit" in st.session_state:
                del st.session_state["df_edit"]
            st.session_state.page = 1
            st.rerun()

    with col_next:
        if st.button("Next: Variable Selection", key="p2_next"):
            # Promote edited data as the working dataset for all future pages
            st.session_state.df = st.session_state.df_edit.copy()
            st.session_state.page = 3
            st.rerun()
def render_page2():

    # ── Guard ─────────────────────────────────────────────────────────────────
    if st.session_state.df is None:
        st.markdown('<div class="status-card status-error">&#10005;&nbsp; No data found. Go back and upload a file.</div>', unsafe_allow_html=True)
        if st.button("← Back to Upload", key="p2_guard_back"):
            st.session_state.page = 1
            st.rerun()
        return

    # Keep a working copy separate from the raw upload
    if "df_edit" not in st.session_state:
        st.session_state.df_edit = st.session_state.df.copy()

    # Track whether a save just happened (controls Next button visibility)
    if "p2_saved" not in st.session_state:
        st.session_state.p2_saved = False

    df = st.session_state.df_edit

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown('<div class="statify-logo" style="font-size:2.2rem">Edit Your <span>Data</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="upload-label">Step 2 of 5 &mdash; Review and clean your dataset before analysis</div>', unsafe_allow_html=True)

    n_rows, n_cols = df.shape
    n_missing = int(df.isna().sum().sum())
    st.markdown(
        f'<div class="stat-row" style="margin-bottom:1.5rem">'
        f'<span class="stat-pill">{n_rows} rows</span>'
        f'<span class="stat-pill">{n_cols} columns</span>'
        f'<span class="stat-pill" style="color:{"#f55a5a" if n_missing > 0 else "#c8f55a"}">'
        f'{"⚠ " + str(n_missing) + " missing" if n_missing > 0 else "✓ No missing values"}'
        f'</span></div>',
        unsafe_allow_html=True,
    )

    # ── READ-ONLY PREVIEW ─────────────────────────────────────────────────────
    st.markdown('<div class="upload-label">Dataset preview (read-only)</div>', unsafe_allow_html=True)
    st.dataframe(df, use_container_width=True, hide_index=False)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── EDIT MODE SELECTOR ────────────────────────────────────────────────────
    st.markdown('<div class="upload-label">Choose edit mode</div>', unsafe_allow_html=True)
    edit_mode = st.radio(
        "edit_mode",
        options=["Edit Row", "Edit Column"],
        horizontal=True,
        label_visibility="collapsed",
        key="edit_mode_radio",
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # EDIT ROW MODE
    # ══════════════════════════════════════════════════════════════════════════
    if edit_mode == "Edit Row":

        # Row 0 in the selector = Column Names (special case)
        row_options = ["Row 0 — Column Names"] + [f"Row {i+1}" for i in range(len(df))]

        selected_row_label = st.selectbox(
            "Select a row to edit",
            options=row_options,
            label_visibility="collapsed",
            key="row_selector",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Special case: editing column names ────────────────────────────────
        if selected_row_label == "Row 0 — Column Names":
            st.markdown('<div class="upload-label">Editing: Column Names</div>', unsafe_allow_html=True)
            st.markdown('<div class="status-card status-idle">&#9432;&nbsp; These are your variable names. Edit carefully — they are used throughout the analysis.</div>', unsafe_allow_html=True)

            new_col_names = {}
            cols_per_row = 3
            col_list = df.columns.tolist()
            # Render inputs in rows of 3 for horizontal layout
            for i in range(0, len(col_list), cols_per_row):
                chunk = col_list[i:i + cols_per_row]
                ui_cols = st.columns(len(chunk))
                for j, col_name in enumerate(chunk):
                    with ui_cols[j]:
                        new_val = st.text_input(
                            f"Column {i+j+1}",
                            value=col_name,
                            key=f"colname_{i+j}",
                        )
                        new_col_names[col_name] = new_val.strip()

            if st.button("💾  Save Column Names", key="save_col_names"):
                # Validate: no empty names, no duplicates
                new_names = list(new_col_names.values())
                if any(n == "" for n in new_names):
                    st.error("Column names cannot be empty.")
                elif len(new_names) != len(set(new_names)):
                    st.error("Duplicate column names found. Each name must be unique.")
                else:
                    st.session_state.df_edit = df.rename(columns=new_col_names)
                    st.session_state.p2_saved = True
                    st.success("✓ Column names updated.")
                    st.rerun()

        # ── Normal row editing ────────────────────────────────────────────────
        else:
            # Convert "Row 3" → index 2
            row_idx = int(selected_row_label.split(" ")[1]) - 1
            row_data = df.iloc[row_idx]

            st.markdown(f'<div class="upload-label">Editing: Row {row_idx + 1}</div>', unsafe_allow_html=True)

            edited_values = {}
            cols_per_row = 2
            col_list = df.columns.tolist()

            for i in range(0, len(col_list), cols_per_row):
                chunk = col_list[i:i + cols_per_row]
                ui_cols = st.columns(len(chunk))
                for j, col_name in enumerate(chunk):
                    with ui_cols[j]:
                        current_val = row_data[col_name]
                        # Show blank string for NaN so the field is editable
                        display_val = "" if pd.isna(current_val) else str(current_val)
                        new_val = st.text_input(
                            col_name,
                            value=display_val,
                            key=f"row_edit_{i+j}",
                        )
                        edited_values[col_name] = new_val

            if st.button("💾  Save Row", key="save_row"):
                new_df = st.session_state.df_edit.copy()
                for col_name, new_val in edited_values.items():
                    original = df[col_name].dtype
                    # Try to cast back to original dtype
                    try:
                        if pd.api.types.is_integer_dtype(original):
                            new_df.at[row_idx, col_name] = int(new_val) if new_val != "" else pd.NA
                        elif pd.api.types.is_float_dtype(original):
                            new_df.at[row_idx, col_name] = float(new_val) if new_val != "" else float("nan")
                        else:
                            new_df.at[row_idx, col_name] = new_val if new_val != "" else pd.NA
                    except (ValueError, TypeError):
                        # If cast fails, save as string — better than losing data
                        new_df.at[row_idx, col_name] = new_val
                st.session_state.df_edit = new_df
                st.session_state.p2_saved = True
                st.success(f"✓ Row {row_idx + 1} saved.")
                st.rerun()

    # ══════════════════════════════════════════════════════════════════════════
    # EDIT COLUMN MODE
    # ══════════════════════════════════════════════════════════════════════════
    else:
        selected_col = st.selectbox(
            "Select a column to edit",
            options=df.columns.tolist(),
            label_visibility="collapsed",
            key="col_selector",
        )

        st.markdown(f'<div class="upload-label">Editing: {selected_col} &mdash; all {len(df)} values shown horizontally</div>', unsafe_allow_html=True)

        col_data = df[selected_col]
        edited_col_values = {}

        # Display column values horizontally in rows of 5
        values_per_row = 5
        indices = col_data.index.tolist()

        for i in range(0, len(indices), values_per_row):
            chunk = indices[i:i + values_per_row]
            ui_cols = st.columns(len(chunk))
            for j, idx in enumerate(chunk):
                with ui_cols[j]:
                    current_val = col_data[idx]
                    display_val = "" if pd.isna(current_val) else str(current_val)
                    new_val = st.text_input(
                        f"[{idx}]",          # row index label above each input
                        value=display_val,
                        key=f"col_edit_{idx}",
                    )
                    edited_col_values[idx] = new_val

        if st.button("💾  Save Column", key="save_col"):
            new_df = st.session_state.df_edit.copy()
            original_dtype = df[selected_col].dtype
            for idx, new_val in edited_col_values.items():
                try:
                    if pd.api.types.is_integer_dtype(original_dtype):
                        new_df.at[idx, selected_col] = int(new_val) if new_val != "" else pd.NA
                    elif pd.api.types.is_float_dtype(original_dtype):
                        new_df.at[idx, selected_col] = float(new_val) if new_val != "" else float("nan")
                    else:
                        new_df.at[idx, selected_col] = new_val if new_val != "" else pd.NA
                except (ValueError, TypeError):
                    new_df.at[idx, selected_col] = new_val
            st.session_state.df_edit = new_df
            st.session_state.p2_saved = True
            st.success(f"✓ Column '{selected_col}' saved.")
            st.rerun()

    # ── Navigation ────────────────────────────────────────────────────────────
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    col_back, col_next = st.columns([1, 2])

    with col_back:
        if st.button("← Back", key="p2_back"):
            if "df_edit" in st.session_state:
                del st.session_state["df_edit"]
            st.session_state.p2_saved = False
            st.session_state.page = 1
            st.rerun()

    with col_next:
        # Next is always available — save is optional (user may not need to edit)
        if st.button("Next → Variable Selection", key="p2_next"):
            st.session_state.df = st.session_state.df_edit.copy()
            st.session_state.p2_saved = False
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
    
