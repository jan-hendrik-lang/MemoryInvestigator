import streamlit as st

import google.generativeai as genai

# Streamlit page title and description
st.title("Report Generator")
st.caption("Generate a report summarizing your findings.")

# Select an LLM model
left, right = st.columns(2)
llm_options = ["gemini-1.5-flash", "gemini-2.0-flash-exp", "gpt-4o"]
llm_option = left.selectbox(
    "Select an LLM of your choice:",
    options=llm_options,
    index=0
)

# Input field for API key
api_key = right.text_input("API LLM Key Input:", type="password")

if api_key:
    # Google LLM Options
    if llm_option == "gemini-1.5-flash" or llm_option == "gemini-2.0-flash-exp":
        genai.configure(api_key=api_key)
        prompt = st.chat_input("Ask Gemini about helping to summarize your key findings:")

        # Define the model and instructions for forensic analysis report generation
        model = genai.GenerativeModel(model_name=llm_option, system_instruction="You are a forensic RAM Analyst Assistant. Help summarizing the key findings to a LaTeX file.")
        convo = model.start_chat(history=[])

        # Send user prompt
        if prompt:
            with st.spinner("Fetching response..."):
                answer = convo.send_message(prompt)
                word_content = convo.last.text

            # Save output as Word file
            word_filename = "O:/gemini_analysis.docx"

            try:
                with open(word_filename, "w", encoding="utf-8") as word_file:
                    word_file.write(word_filename)
                st.success(f"Word file saved to {word_filename}")
            except Exception as e:
                st.error(f"Failed to save Word file: {e}")

            st.write("**Gemini says:**", word_content)
