import os
import shutil

import streamlit as st
import google.generativeai as genai
from openai import OpenAI

# Import utility functions to divide the json file and to select the basic or costume tree
from utils.json_divider import divide_json
from utils.select_tree import choose_basic_or_costume_tree

def handle_llm_chat(llm_option, api_key, number_of_divided_jsons, prompt):
    """
    Handles interaction with an LLM (either Gemini or OpenAI models) for forensic RAM analysis.

    :param llm_option: The selected LLM model (Gemini or OpenAI).
    :param api_key: API key for authentication.
    :param number_of_divided_jsons: Number of parts the JSON should be divided into for processing.
    :param prompt: User input prompt for guiding the LLM response.
    :return: None, outputs results directly in Streamlit.
    """
    # Google LLM Options
    if llm_option.startswith("gemini"):
        genai.configure(api_key=api_key)
        tree = choose_basic_or_costume_tree()
        if tree is not None:
            if number_of_divided_jsons > 1:
                all_responses = []
                divide_json(number_of_divided_jsons, tree)
                for i in range(number_of_divided_jsons):
                    save_path = "O:\\03_trees\\temp"
                    file_name = os.path.join(save_path, f"temp_{i + 1:02d}.json")
                    with open(file_name, 'r', encoding='utf-8') as file:

                        # Read the entire contents of the file
                        chunk = file.read()

                        # Create an instance of the selected LLM model and process the divided JSON file chunk
                        model = genai.GenerativeModel(model_name=llm_option,
                                                      system_instruction=f"You are a forensic RAM Analyst Assistant. Travers the JSON Tree and help to find a intruder: {chunk}")
                        convo = model.start_chat(history=[])

                        # Send user prompt with each chunk
                        if prompt:
                            with st.spinner(f"Fetching response for part {i + 1}..."):
                                response = convo.send_message(prompt)
                                all_responses.append(convo.last.text)
                            st.write(f"**Gemini says (part {i + 1}):**", convo.last.text)
                if all_responses:
                    # Send prompt to summarize the findings
                    summary_prompt = "Summarize the findings from all parts of the JSON data. " + " ".join(
                        all_responses)  # Include previous responses in summary prompt
                    model = genai.GenerativeModel(model_name=llm_option,
                                                  system_instruction=f"You are a forensic RAM Analyst Assistant. Travers the JSON Tree and help to find a intruder.")
                    convo = model.start_chat(history=[])
                    with st.spinner("Fetching summary..."):
                        summary_response = convo.send_message(summary_prompt)
                    st.write("**Gemini's Summary:**", convo.last.text)
                    shutil.rmtree("O:\\03_trees\\temp")
            else:
                # Process the full JSON data using the selected LLM model
                with open(tree, 'r', encoding='utf-8') as file:
                    # Read the entire contents of the file
                    json_data = file.read()
                    model = genai.GenerativeModel(model_name=llm_option,
                                                  system_instruction=f"You are a forensic RAM Analyst Assistant. Travers the JSON Tree and help to find a intruder: {json_data}")

                    convo = model.start_chat(history=[])

                    if prompt:  # Send user prompt with each chunk
                        with st.spinner(f"Fetching response..."):
                            response = convo.send_message(prompt)
                        st.write(f"**Gemini says:**", convo.last.text)
        else:
            st.error("Please build a tree first.")

    # OpenAI LLM Options
    elif llm_option == "chatgpt-4o-latest" or llm_option == "gpt-3.5-turbo" or llm_option == "o1-preview":
        tree = choose_basic_or_costume_tree()
        client = OpenAI(api_key=api_key)
        if tree is not None:
            if number_of_divided_jsons > 1:
                all_responses = []
                divide_json(number_of_divided_jsons, tree)
                for i in range(number_of_divided_jsons):
                    save_path = "O:\\03_trees\\temp"
                    file_name = os.path.join(save_path, f"temp_{i + 1:02d}.json")
                    with open(file_name, 'r', encoding='utf-8') as file:

                        # Read the entire contents of the file
                        chunk = file.read()

                        # Send user prompt with each chunk
                        if prompt:
                            with st.spinner(f"Fetching response for part {i + 1}..."):
                                completion = client.chat.completions.create(
                                    model=llm_option,
                                    messages=[
                                        {"role": "system",
                                         "content": f"You are a forensic RAM Analyst Assistant. Travers the JSON Tree and help to find a intruder: {chunk}"},
                                        {
                                            "role": "user",
                                            "content": prompt
                                        }
                                    ]
                                )
                                all_responses.append(completion.choices[0].message.content)
                                print(f"Response append: {i + 1}", all_responses)
                            st.write(f"**ChatGPT says (part {i + 1}):**", completion.choices[0].message.content)

                if all_responses:
                    print("Summary:", all_responses)
                    # Send prompt to summarize the findings
                    summary_prompt = "Summarize the findings from all parts of the JSON data. " + " ".join(
                        all_responses)  # Include previous responses in summary prompt

                    with st.spinner("Fetching summary..."):
                        completion = client.chat.completions.create(
                            model=llm_option,
                            messages=[
                                {"role": "system",
                                 "content": f"You are a forensic RAM Analyst Assistant. Travers the JSON Tree and help to find a intruder: {chunk}"},
                                {
                                    "role": "user",
                                    "content": summary_prompt
                                }
                            ]
                        )
                    st.write("**ChatGPTs Summary:**", completion.choices[0].message.content)
                    shutil.rmtree("O:\\03_trees\\temp")
            else:
                # Process the full JSON data using the selected LLM model
                with open(tree, 'r', encoding='utf-8') as file:
                    # Read the entire contents of the file
                    json_data = file.read()

                    if prompt:  # Send user prompt with each chunk
                        with st.spinner(f"Fetching response..."):
                            completion = client.chat.completions.create(
                                model=llm_option,
                                messages=[
                                    {"role": "system",
                                     "content": f"You are a forensic RAM Analyst Assistant. Travers the JSON Tree and help to find a intruder: {json_data}"},
                                    {
                                        "role": "user",
                                        "content": prompt
                                    }
                                ]
                            )
                        st.write(f"**Gemini says:**", completion.choices[0].message.content)

        else:
            st.error("Please build a tree first.")

    else:
        st.error("Select a valid LLM.")
