"""
===========================================================
AI SQL Chatbot
Natural Language to SQL Query Generator
Supports Default DB & User Custom File Uploads (CSV, Excel, SQLite)
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
    layout=LAYOUT
)

# ===========================================================
# Session State Initialization
# ===========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "active_db" not in st.session_state:
    st.session_state.active_db = None  # None = use default company.db

if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None

# ===========================================================
# Header
# ===========================================================

st.title(APP_NAME)
st.caption(APP_DESCRIPTION)
st.markdown("---")

# ===========================================================
# Sidebar
# ===========================================================

# Current Database

if st.session_state.active_db:
    st.success(f"📂 Using: {st.session_state.uploaded_file_name}")
else:
    st.success("📂 Using: Default Company Database")

if st.button("🔄 Reset to Default Database"):

    st.session_state.active_db = None
    st.session_state.uploaded_file_name = None
    st.rerun()

    st.markdown("---")

    if api_key:
        st.success("✅ API Key Loaded")
    else:
        st.warning("⚠️ Please enter your Gemini API Key")

    st.markdown("---")

    st.info(
        """
        💡 Example Questions

        • Show all records
        • Count total rows
        • Group by category and show average
        • Filter records where amount > 500
        """
    )

# ===========================================================
# Welcome Section
# ===========================================================
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

st.subheader("📊 Database Explorer")

st.success(f"Currently Using: **{current_db_name}**")

try:

    tables = get_tables(current_db)

    if tables:

        selected_table = st.selectbox(
            "Select Table",
            tables,
            key="table_preview"
        )

        rows, columns = table_info(
            selected_table,
            current_db
        )

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Rows", rows)

        with col2:
            st.metric("Columns", len(columns))

        st.write("### 🏷 Available Columns")

        st.write(", ".join(columns))

        st.write("### 👀 Dataset Preview")

        preview = preview_table(
            selected_table,
            current_db
        )

        st.dataframe(
            preview,
            use_container_width=True,
            height=350
        )

        st.caption("Showing first 100 rows")

except Exception as e:

    st.warning(f"Unable to load database preview: {e}")

st.markdown("---")
if len(st.session_state.messages) == 0:
    st.info(WELCOME_MESSAGE)

# ===========================================================
# Display Previous Chat Messages
# ===========================================================

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.write(message["content"])
        else:
            st.markdown("### 📝 Generated SQL")
            st.code(
                message["sql"],
                language="sql"
            )

            st.markdown("### 📊 Query Results")
            st.dataframe(
                message["result"],
                use_container_width=True
            )

            with st.expander(
                "💡 SQL Explanation",
                expanded=True
            ):
                st.write(message["explanation"])

# ===========================================================
# Chat Input
# ===========================================================

user_question = st.chat_input(CHAT_PLACEHOLDER)

# ===========================================================
# Process User Question
# ===========================================================

if user_question:

    # Check API Key
    if not api_key:
        st.error("⚠️ Please enter your Gemini API Key from the sidebar.")
        st.stop()

    # Save and display User Message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_question
        }
    )

    with st.chat_message("user"):
        st.write(user_question)

    # Active DB Path (None = default company.db)
    active_db = st.session_state.active_db

    # Generate SQL
    with st.spinner("🤖 Generating SQL Query..."):
        try:
            generated_sql = generate_sql(
                question=user_question,
                model_name=selected_model,
                api_key=api_key,
                db_path=active_db
            )
        except Exception as e:
            st.error(f"Error while generating SQL:\n\n{e}")
            st.stop()

    # Execute SQL
    with st.spinner("📊 Executing SQL Query..."):
        try:
            query_result = execute_query(generated_sql, db_path=active_db)
            database_error = None
        except Exception as e:
            query_result = None
            database_error = str(e)

    # Explain SQL
    with st.spinner("🧠 Explaining SQL Query..."):
        try:
            sql_explanation = explain_sql(
                sql_query=generated_sql,
                model_name=selected_model,
                api_key=api_key
            )
        except Exception:
            sql_explanation = "Explanation could not be generated."

    # Display Assistant Response
    with st.chat_message("assistant"):

        # Generated SQL
        st.subheader("📝 Generated SQL")
        st.code(
            generated_sql,
            language="sql"
        )
        st.info("💡 Select the SQL above and copy it (Ctrl+C / Cmd+C).")

        # Query Results
        st.subheader("📊 Query Results")

        if query_result is not None:
            if query_result.empty:
                st.info("No records found for this query.")
            else:
                st.dataframe(
                    query_result,
                    use_container_width=True
                )
                st.success(f"✅ {len(query_result)} record(s) retrieved successfully.")

                csv = query_result.to_csv(index=False).encode("utf-8")
                filename = f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name=filename,
                    mime="text/csv",
                    use_container_width=True
                )
        else:
            st.error("❌ Failed to execute SQL query.")
            st.code(database_error)

        # SQL Explanation
        with st.expander(
            "💡 SQL Explanation",
            expanded=True
        ):
            st.write(sql_explanation)

    # Save Assistant Response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "sql": generated_sql,
            "result": query_result,
            "explanation": sql_explanation
        }
    )
