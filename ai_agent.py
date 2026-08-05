"""
===========================================================
AI Agent
Natural Language → SQL → Explanation
===========================================================
"""

from langchain_google_genai import ChatGoogleGenerativeAI

from prompts import (
    SQL_GENERATION_PROMPT,
    SQL_EXPLANATION_PROMPT
)

from database import get_database_schema


# ===========================================================
# Create Gemini Model
# ===========================================================

def create_llm(model_name, api_key):
    """
    Creates a Gemini LLM instance.
    """

    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=0
    )


# ===========================================================
# Clean SQL Response
# ===========================================================

def clean_sql(sql):
    """
    Removes markdown formatting if Gemini returns it.
    """

    if not sql:
        return ""

    sql = sql.replace("```sql", "")
    sql = sql.replace("```", "")
    sql = sql.strip()

    return sql


# ===========================================================
# Generate SQL
# ===========================================================

def generate_sql(question, model_name, api_key):
    """
    Converts a natural language question into SQL.
    """

    # Read schema from database
    schema = get_database_schema()

    # Create prompt
    prompt = SQL_GENERATION_PROMPT.format(
        schema=schema,
        question=question
    )

    # Create Gemini model
    llm = create_llm(model_name, api_key)

    # Generate response
    response = llm.invoke(prompt)

    # Handle Gemini response
    if isinstance(response.content, list):

        output = ""

        for item in response.content:

            if hasattr(item, "text"):
                output += item.text

            elif isinstance(item, dict):
                output += item.get("text", "")

            else:
                output += str(item)

    else:

        output = response.content

    return clean_sql(output)


# ===========================================================
# Explain SQL
# ===========================================================

def explain_sql(sql_query, model_name, api_key):
    """
    Explains the generated SQL query in simple English.
    """

    prompt = SQL_EXPLANATION_PROMPT.format(
        sql_query=sql_query
    )

    llm = create_llm(model_name, api_key)

    response = llm.invoke(prompt)

    if isinstance(response.content, list):

        explanation = ""

        for item in response.content:

            if hasattr(item, "text"):
                explanation += item.text

            elif isinstance(item, dict):
                explanation += item.get("text", "")

            else:
                explanation += str(item)

    else:

        explanation = response.content

    return explanation.strip()
