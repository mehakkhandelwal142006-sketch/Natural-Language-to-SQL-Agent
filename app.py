"""
===========================================================
AI SQL Chatbot
Natural Language to SQL Query Generator

Features
---------
✔ Gemini AI
✔ Default Company Database
✔ Upload CSV / Excel / SQLite
✔ Database Explorer
✔ Suggested Questions
✔ SQL Generation
✔ SQL Explanation
✔ Query Results
✔ CSV Download
===========================================================
"""

import streamlit as st
from datetime import datetime

from config import (
    APP_NAME,
    APP_DESCRIPTION,
    AVAILABLE_MODELS,
    DEFAULT_MODEL,
    PAGE_TITLE,
    PAGE_ICON,
    LAYOUT,
    CHAT_PLACEHOLDER,
    WELCOME_MESSAGE
)

from ai_agent import (
    generate_sql,
    explain_sql
)

from database import (
    execute_query,
    get_database_schema,
    load_custom_file_to_sqlite,
    get_tables,
    preview_table,
    table_info
)

# ===========================================================
# Page Configuration
# ===========================================================

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state="expanded"
)

# ===========================================================
# Session State Initialization
# ===========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

# Active Database
# None = Default company.db
if "active_db" not in st.session_state:
    st.session_state.active_db = None

# Uploaded filename
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None

# Currently selected preview table
if "selected_table" not in st.session_state:
    st.session_state.selected_table = None

# Query history
if "query_history" not in st.session_state:
    st.session_state.query_history = []

# Suggested questions
if "suggested_questions" not in st.session_state:
    st.session_state.suggested_questions = []

# ===========================================================
# Header
# ===========================================================

st.title(APP_NAME)

st.caption(APP_DESCRIPTION)

st.markdown("---")

# ===========================================================
# Sidebar
# ===========================================================

with st.sidebar:

    st.header("⚙️ Configuration")

    # -------------------------------------------------------
    # Gemini API Key
    # -------------------------------------------------------

    st.subheader("🔑 Gemini API Key")

    api_key = st.text_input(
        "Enter your Gemini API Key",
        type="password",
        placeholder="Paste your Gemini API Key here..."
    )

    if api_key:
        st.success("✅ API Key Loaded")
    else:
        st.warning("⚠️ API Key Required")

    st.markdown("---")

    # -------------------------------------------------------
    # Model Selection
    # -------------------------------------------------------

    st.subheader("🤖 Gemini Model")

    selected_model = st.selectbox(
        "Choose Gemini Model",
        AVAILABLE_MODELS,
        index=AVAILABLE_MODELS.index(DEFAULT_MODEL)
    )

    st.markdown("---")

    # -------------------------------------------------------
    # Upload Dataset
    # -------------------------------------------------------

    st.subheader("📂 Upload Dataset")

    st.caption(
        "Upload a CSV, Excel, or SQLite database to query your own data."
    )

    uploaded_file = st.file_uploader(
        "Choose File",
        type=[
            "csv",
            "xlsx",
            "xls",
            "db",
            "sqlite",
            "sqlite3"
        ]
    )

    if uploaded_file is not None:

        if st.session_state.uploaded_file_name != uploaded_file.name:

            try:

                target_db = "data/uploaded.db"

                message = load_custom_file_to_sqlite(
                    uploaded_file,
                    target_db
                )

                st.session_state.active_db = target_db
                st.session_state.uploaded_file_name = uploaded_file.name

                st.success(message)

            except Exception as e:

                st.error(f"❌ {e}")

    st.markdown("---")

    # -------------------------------------------------------
    # Active Database
    # -------------------------------------------------------

    st.subheader("📊 Current Database")

    if st.session_state.active_db:

        st.success(
            f"Using: {st.session_state.uploaded_file_name}"
        )

    else:

        st.info("Using: Default Company Database")

    # -------------------------------------------------------
    # Reset Database
    # -------------------------------------------------------

    if st.button(
        "🔄 Reset to Default Database",
        use_container_width=True
    ):

        st.session_state.active_db = None
        st.session_state.uploaded_file_name = None
        st.session_state.selected_table = None

        st.success("Default database restored.")

        st.rerun()

    st.markdown("---")

    # -------------------------------------------------------
    # About
    # -------------------------------------------------------

    with st.expander("ℹ️ About This Project"):

        st.write(
            """
This application converts natural language into SQL queries
using Google's Gemini AI.

### Supported Files

- CSV
- Excel (.xlsx/.xls)
- SQLite Database

### Features

- AI SQL Generation
- SQL Explanation
- Dataset Preview
- Database Explorer
- Download Results as CSV
"""
        )

    st.markdown("---")

    # -------------------------------------------------------
    # Sample Questions
    # -------------------------------------------------------

    with st.expander("💡 Example Questions"):

        st.markdown("""
- Show all employees

- Count total employees

- Show employees earning more than 50000

- Find average salary

- Group employees by department

- Show top 10 records
""")

# ===========================================================
# Database Explorer
# ===========================================================

# Determine active database
if st.session_state.active_db:
    current_db = st.session_state.active_db
    current_db_name = st.session_state.uploaded_file_name
else:
    current_db = None
    current_db_name = "Default Company Database"

with st.expander("📊 Database Explorer", expanded=True):

    st.success(f"Currently Using: **{current_db_name}**")

    try:

        tables = get_tables(current_db)

        if not tables:
            st.warning("No tables found in the selected database.")

        else:

            selected_table = st.selectbox(
                "📋 Select Table",
                tables,
                key="table_selector"
            )

            st.session_state.selected_table = selected_table

            rows, columns = table_info(
                selected_table,
                current_db
            )

            # --------------------------------------------------
            # Metrics
            # --------------------------------------------------

            metric1, metric2 = st.columns(2)

            with metric1:
                st.metric(
                    "📄 Rows",
                    rows
                )

            with metric2:
                st.metric(
                    "📑 Columns",
                    len(columns)
                )

            st.markdown("---")

            # --------------------------------------------------
            # Columns
            # --------------------------------------------------

            st.subheader("🏷 Available Columns")

            column_text = ""

            for column in columns:
                column_text += f"`{column}`   "

            st.markdown(column_text)

            st.markdown("---")

            # --------------------------------------------------
            # Suggested Questions
            # --------------------------------------------------

            st.subheader("💡 Suggested Questions")

            suggestions = [

                f"Show all records from {selected_table}",

                f"Count total records in {selected_table}"

            ]

            for column in columns:

                col = column.lower()

                if "name" in col:
                    suggestions.append(
                        f"Show only the {column} column"
                    )

                if "department" in col:
                    suggestions.append(
                        f"Group records by {column}"
                    )

                if "category" in col:
                    suggestions.append(
                        f"Group records by {column}"
                    )

                if "salary" in col:
                    suggestions.append(
                        f"Find average {column}"
                    )

                    suggestions.append(
                        f"Show records where {column} is greater than 50000"
                    )

                if "amount" in col:
                    suggestions.append(
                        f"Find average {column}"
                    )

                if "price" in col:
                    suggestions.append(
                        f"Find maximum {column}"
                    )

                if "age" in col:
                    suggestions.append(
                        f"Show records where {column} is greater than 30"
                    )

                if "date" in col:
                    suggestions.append(
                        f"Sort records by {column}"
                    )

            suggestions = list(dict.fromkeys(suggestions))

            st.session_state.suggested_questions = suggestions

            for question in suggestions[:6]:
                st.info(question)

            st.markdown("---")

            # --------------------------------------------------
            # Dataset Preview
            # --------------------------------------------------

            st.subheader("👀 Dataset Preview")

            preview_df = preview_table(
                selected_table,
                current_db
            )

            st.dataframe(
                preview_df,
                use_container_width=True,
                height=350
            )

            st.caption("Showing first 100 rows.")

    except Exception as e:

        st.error(f"Unable to load database preview.\n\n{e}")

st.markdown("---")

# ===========================================================
# Welcome Section
# ===========================================================

if len(st.session_state.messages) == 0:

    st.info(WELCOME_MESSAGE)

    st.markdown(
        """
### 🚀 What can you do?

You can ask questions in plain English such as:

- Show all employees
- Count total employees
- Show employees earning more than 50000
- Find average salary department-wise
- Sort employees by salary
- Show top 10 records

The AI will automatically convert your request into SQL,
execute it and explain the generated query.
"""
    )

# ===========================================================
# Chat Controls
# ===========================================================

col1, col2 = st.columns([4, 1])

with col2:

    if st.button(
        "🗑 Clear Chat",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.session_state.query_history = []

        st.rerun()

st.markdown("---")

# ===========================================================
# Previous Chat Messages
# ===========================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        if message["role"] == "user":

            st.write(message["content"])

        else:

            st.subheader("📝 Generated SQL")

            st.code(
                message["sql"],
                language="sql"
            )

            st.subheader("📊 Query Results")

            if message["result"] is not None:

                st.dataframe(
                    message["result"],
                    use_container_width=True
                )

            with st.expander(
                "💡 SQL Explanation",
                expanded=False
            ):

                st.write(
                    message["explanation"]
                )

# ===========================================================
# Query History
# ===========================================================

if len(st.session_state.query_history) > 0:

    st.markdown("---")

    with st.expander(
        "📜 Query History",
        expanded=False
    ):

        for i, sql in enumerate(
            reversed(st.session_state.query_history),
            start=1
        ):

            st.code(
                sql,
                language="sql"
            )

# ===========================================================
# Suggested Questions
# ===========================================================

if len(st.session_state.suggested_questions) > 0:

    st.markdown("### 💡 Suggested Questions")

    cols = st.columns(2)

    for i, question in enumerate(
        st.session_state.suggested_questions[:6]
    ):

        with cols[i % 2]:

            st.info(question)

st.markdown("---")

# ===========================================================
# Chat Input
# ===========================================================

user_question = st.chat_input(CHAT_PLACEHOLDER)

# ===========================================================
# Process User Question
# ===========================================================

if user_question:

    # -------------------------------
    # Validate API Key
    # -------------------------------

    if not api_key:

        st.error("⚠ Please enter your Gemini API Key from the sidebar.")

        st.stop()

    # -------------------------------
    # Store User Message
    # -------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_question
        }
    )

    with st.chat_message("user"):

        st.write(user_question)

    # Active Database
    active_db = st.session_state.active_db

    # -------------------------------
    # Generate SQL
    # -------------------------------

    with st.spinner("🤖 Gemini is generating SQL..."):

        try:

            generated_sql = generate_sql(
                question=user_question,
                model_name=selected_model,
                api_key=api_key,
                db_path=active_db
            )

        except Exception as e:

            st.error(f"Failed to generate SQL.\n\n{e}")

            st.stop()

    # -------------------------------
    # Execute SQL
    # -------------------------------

    with st.spinner("📊 Executing SQL Query..."):

        try:

            query_result = execute_query(
                generated_sql,
                db_path=active_db
            )

            database_error = None

        except Exception as e:

            query_result = None

            database_error = str(e)

    # -------------------------------
    # Generate SQL Explanation
    # -------------------------------

    with st.spinner("🧠 Explaining SQL Query..."):

        try:

            sql_explanation = explain_sql(
                sql_query=generated_sql,
                model_name=selected_model,
                api_key=api_key
            )

        except Exception:

            sql_explanation = (
                "Explanation could not be generated."
            )

    # -------------------------------
    # Save Query History
    # -------------------------------

    st.session_state.query_history.append(
        generated_sql
    )

    # -------------------------------
    # Assistant Response
    # -------------------------------

    with st.chat_message("assistant"):

        st.success("✅ SQL Generated Successfully")

        st.subheader("📝 Generated SQL")

        st.code(
            generated_sql,
            language="sql"
        )

        st.info(
            "💡 Copy the SQL above using Ctrl+C / Cmd+C."
        )

        st.subheader("📊 Query Results")

        if query_result is not None:

            if query_result.empty:

                st.warning(
                    "No matching records found."
                )

            else:

                st.dataframe(
                    query_result,
                    use_container_width=True
                )

                st.success(
                    f"{len(query_result)} record(s) retrieved."
                )

                # CSV Download
                csv = query_result.to_csv(
                    index=False
                ).encode("utf-8")

                filename = (
                    f"query_results_"
                    f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                )

                st.download_button(
                    "📥 Download Results as CSV",
                    csv,
                    filename,
                    "text/csv",
                    use_container_width=True
                )

        else:

            st.error(
                "Database execution failed."
            )

            st.code(database_error)

        with st.expander(
            "💡 SQL Explanation",
            expanded=False
        ):

            st.write(sql_explanation)

# ===========================================================
# Save Assistant Response
# ===========================================================

    st.session_state.messages.append(
        {
            "role": "assistant",
            "sql": generated_sql,
            "result": query_result,
            "explanation": sql_explanation
        }
    )

# ===========================================================
# Footer
# ===========================================================

st.markdown("---")

footer_col1, footer_col2 = st.columns([3, 1])

with footer_col1:

    st.caption(
        """
Natural Language to SQL Agent

Powered by Google Gemini AI • Streamlit • SQLAlchemy
"""
    )

with footer_col2:

    st.caption("Version 1.0")

st.markdown(
    """
<style>

.block-container{

    padding-top:2rem;
    padding-bottom:2rem;

}

div[data-testid="stMetric"]{

    border:1px solid #E5E7EB;
    padding:15px;
    border-radius:12px;

}

div.stButton>button{

    border-radius:10px;
    height:45px;

}

div.stDownloadButton>button{

    border-radius:10px;
    height:45px;

}

.stCodeBlock{

    border-radius:12px;

}

</style>
""",
unsafe_allow_html=True
)






