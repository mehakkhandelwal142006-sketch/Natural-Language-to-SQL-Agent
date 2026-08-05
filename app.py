import streamlit as st
from config import APP_NAME, GOOGLE_API_KEY, DEFAULT_MODEL

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title=APP_NAME,
    page_icon="🧠",
    layout="wide"
)

# -----------------------------
# Header
# -----------------------------
st.title("🧠 Natural Language to SQL Agent")

st.markdown("""
Ask questions in **plain English** and let AI convert them into SQL queries.

This application will:

- 🔹 Generate SQL
- 🔹 Execute Queries
- 🔹 Explain SQL
- 🔹 Suggest Optimizations
- 🔹 Visualize Results
""")

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("⚙️ Configuration")

if GOOGLE_API_KEY:
    st.sidebar.success("✅ Gemini API Loaded")
else:
    st.sidebar.error("❌ API Key Missing")

model = st.sidebar.selectbox(
    "Select Model",
    [
        DEFAULT_MODEL,
        "gemini-2.5-flash-lite"
    ]
)

st.sidebar.markdown("---")
st.sidebar.write("Project Status")
st.sidebar.info("Phase 1 - Setup")

# -----------------------------
# Tabs
# -----------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📝 Generate SQL",
    "▶️ Execute",
    "📖 Explain",
    "📊 Visualize",
    "📜 History"
])

# -----------------------------
# Generate SQL
# -----------------------------
with tab1:

    st.subheader("Ask your database")

    user_question = st.text_area(
        "Enter your question",
        placeholder="Example: Show all employees working in the HR department."
    )

    if st.button("Generate SQL"):
        if user_question.strip():
            st.success("Great! AI integration will be added in Phase 3.")
            st.write("Your Question:")
            st.code(user_question)
        else:
            st.warning("Please enter a question.")

# -----------------------------
# Execute
# -----------------------------
with tab2:
    st.info("Coming in Phase 5")

# -----------------------------
# Explain
# -----------------------------
with tab3:
    st.info("Coming in Phase 6")

# -----------------------------
# Visualize
# -----------------------------
with tab4:
    st.info("Coming in Phase 7")

# -----------------------------
# History
# -----------------------------
with tab5:
    st.info("Coming in Phase 8")