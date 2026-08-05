"""
===========================================================
AI Prompts
===========================================================
"""

# ===========================================================
# SQL Generation Prompt
# ===========================================================

SQL_GENERATION_PROMPT = """
You are an expert SQL Developer.

Your task is to convert a user's natural language question into a valid SQL query.

------------------------------------------------------------
DATABASE SCHEMA
------------------------------------------------------------

{schema}

------------------------------------------------------------
USER QUESTION
------------------------------------------------------------

{question}

------------------------------------------------------------
INSTRUCTIONS
------------------------------------------------------------

1. Generate ONLY the SQL query.

2. Do NOT explain the query.

3. Do NOT include markdown.

4. Do NOT wrap the SQL inside ```sql.

5. Use only the tables and columns available in the schema.

6. If the user asks something impossible using the given schema,
return:

SELECT 'Requested information is not available in the database.' AS Message;

7. Generate syntactically correct SQL for SQLite.

8. Never guess table names or column names.

9. Return only one SQL query.

"""

# ===========================================================
# SQL Explanation Prompt
# ===========================================================

SQL_EXPLANATION_PROMPT = """
You are an SQL expert and teacher.

Explain the following SQL query in simple English.

------------------------------------------------------------
SQL QUERY
------------------------------------------------------------

{sql_query}

------------------------------------------------------------
INSTRUCTIONS
------------------------------------------------------------

Explain:

1. Which table is being used.

2. Which columns are selected.

3. Any filtering conditions (WHERE).

4. Any sorting (ORDER BY).

5. Any grouping (GROUP BY).

6. What result the user will get.

Keep the explanation beginner-friendly.

Do NOT explain SQL syntax.

Do NOT rewrite the SQL query.
"""
