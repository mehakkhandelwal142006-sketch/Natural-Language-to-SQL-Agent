"""
===========================================================
AI SQL Chatbot
Natural Language to SQL Query Generator
===========================================================
"""

import streamlit as st

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
    execute_query
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
# Session State
# ===========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

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

    st.markdown("### 🔑 Gemini API Key")

    api_key = st.text_input(
        "Enter your Gemini API Key",
        type="password",
        placeholder="Paste your API Key here"
    )

    st.markdown("---")

    st.markdown("### 🤖 Gemini Model")

    selected_model = st.selectbox(
        "Choose Model",
        AVAILABLE_MODELS,
        index=AVAILABLE_MODELS.index(DEFAULT_MODEL)
    )

    st.markdown("---")

    st.markdown("### 🗄️ Database")

    database_type = st.selectbox(
        "Database Type",
        [
            "SQLite",
            "MySQL (Coming Soon)"
        ],
        index=0
    )

    st.markdown("---")

    if api_key:

        st.success("✅ API Key Loaded")

    else:

        st.warning("⚠️ Please enter your Gemini API Key")

    st.markdown("---")

    st.info(
        """
        💡 Example Questions

        • Show all employees

        • Show employees from HR

        • Count employees

        • Show average salary

        • Show employees earning more than 60000
        """
    )

# ===========================================================
# Welcome Section
# ===========================================================

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

    # -------------------------------------------------------
    # Check API Key
    # -------------------------------------------------------

    if not api_key:

        st.error("⚠️ Please enter your Gemini API Key from the sidebar.")

        st.stop()

    # -------------------------------------------------------
    # Display User Message
    # -------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_question
        }
    )

    with st.chat_message("user"):

        st.write(user_question)

    # -------------------------------------------------------
    # Generate SQL
    # -------------------------------------------------------

    with st.spinner("🤖 Generating SQL Query..."):

        try:

            generated_sql = generate_sql(
                question=user_question,
                model_name=selected_model,
                api_key=api_key
            )

        except Exception as e:

            st.error(f"Error while generating SQL:\n\n{e}")

            st.stop()

    # -------------------------------------------------------
    # Execute SQL
    # -------------------------------------------------------

    with st.spinner("📊 Executing SQL Query..."):

        try:

            query_result = execute_query(generated_sql)

        except Exception as e:

            query_result = None

            database_error = str(e)

    # -------------------------------------------------------
    # Explain SQL
    # -------------------------------------------------------

    with st.spinner("🧠 Explaining SQL Query..."):

        try:

            sql_explanation = explain_sql(
                sql_query=generated_sql,
                model_name=selected_model,
                api_key=api_key
            )

        except Exception:

            sql_explanation = "Explanation could not be generated."

# ===========================================================
# Display Assistant Response
# ===========================================================

    with st.chat_message("assistant"):

        # ----------------------------
        # Generated SQL
        # ----------------------------

        st.subheader("📝 Generated SQL")

        st.code(
            generated_sql,
            language="sql"
        )

        # ----------------------------
        # Query Results
        # ----------------------------

        st.subheader("📊 Query Results")

        if query_result is not None:

            if query_result.empty:

                st.info("No records found.")

            else:

                st.dataframe(
                    query_result,
                    use_container_width=True
                )

        else:

            st.error("Failed to execute SQL query.")

            st.code(database_error)

        # ----------------------------
        # SQL Explanation
        # ----------------------------

        with st.expander(
            "💡 SQL Explanation",
            expanded=True
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
