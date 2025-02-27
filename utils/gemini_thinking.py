import re
import asyncio
import streamlit as st
from google import genai
from utils.select_tree import choose_basic_or_costume_tree


def build_prompt_from_history(chat_history, system_message=None):
    """
    Builds a single prompt string from the entire chat history.

    This function merges a list of messages (user, assistant, and possibly system)
    into a single text string. Because some LLM APIs require a single prompt instead
    of structured conversation, we convert each item of the chat history into a
    labeled string (e.g., "USER: ...", "ASSISTANT: ...", etc.). If a system message
    is passed in, it is placed at the beginning of the prompt.

    'system_message' can optionally be inserted additionally.
    :param chat_history: The list of messages so far in the conversation. Each message is typically a dictionary with the keys:
                - "role" (str): e.g. "user", "assistant", or "system"
                - "content" (str): The text content of the message.
    :param system_message: An additional message (often instructions or background context) that will be placed at the beginning of the final prompt under the label "SYSTEM".
    :return: A single string containing all messages labeled by their roles. Suitable for passing to an LLM that only accepts a single prompt.
    """
    prompt_parts = []

    # If we have a system message, add it at the beginning
    if system_message:
        prompt_parts.append(f"SYSTEM: {system_message}\n")

    # Go through chat history
    for msg in chat_history:
        role = msg.get("role")
        content = msg.get("content", "")

        if role == "assistant":
            # You could write “ASSISTANT” or “GEMINI” or “AI” - whatever you like
            prompt_parts.append(f"ASSISTANT: {content}\n")
        elif role == "user":
            prompt_parts.append(f"USER: {content}\n")
        elif role == "system":
            # If you also store system messages in st.session_state
            prompt_parts.append(f"SYSTEM: {content}\n")
        else:
            # Fallback
            prompt_parts.append(f"{role.upper()}: {content}\n")

    # Merge all strings
    return "".join(prompt_parts)


async def gemini_first_thinking(api_llm_key, prompt=None):
    """
    Performs the first LLM analysis and returns an initial response.

    This function is intended to handle the initial user query or analysis step
    by combining any existing chat history plus an optional user prompt,
    along with a memory structure from a tree file. Everything is merged into
    a single prompt string that is then sent to the Gemini model, which
    responds with a text message.

    :param api_llm_key: The API key required for accessing the Google GenAI service.
    :param prompt: An optional user prompt or question. If provided, it will be appended to the chat history with the role "user".
    :return: The Gemini LLM's response text. If no tree file is found, a message instructing the user to build a tree is returned.
    """
    client = genai.Client(api_key=api_llm_key, http_options={'api_version': 'v1alpha'})
    chat = client.aio.chats.create(model='gemini-2.0-flash-thinking-exp')

    # Get tree file
    tree = choose_basic_or_costume_tree()
    if tree is None:
        return "Please build a tree first."

    with open(tree, 'r', encoding='utf-8') as file:
        json_data = file.read()
        json_data = re.sub(r'"children": \[\]', ' ', json_data)
        json_data = re.sub(r'Required memory at 0x[0-9a-fA-F]+ is not valid \(process exited\?\)', '', json_data)  # Remove error message
        json_data = re.sub(r'Required memory at 0x[0-9a-fA-F]+ is inaccessible \(swapped\)', '', json_data)  # Remove error message

        cleaned_json_data = re.sub(r'\s+', ' ', json_data).strip()
        print("--START--")
        print(cleaned_json_data)
        print("--ENDE--")
    # Prepare system context (memory structure)
    system_msg = (
        "Analyze the provided JSON memory structure and assist in identifying "
        f"suspicious activity or malicious presence.\n\nData: {cleaned_json_data}"
    )

    # Previous chat history + optional prompt from user
    # (prompt is appended here as “USER” if it exists)
    # We append NOTHING to st.session_state.chat_history, but build our prompt string from what is already there + prompt,
    # what is already there + prompt our prompt string.
    temp_history = st.session_state.chat_history.copy()

    if prompt:
        temp_history.append({"role": "user", "content": prompt})

    # Build a large prompt string
    final_prompt = build_prompt_from_history(temp_history, system_message=system_msg)

    # Send and get reply
    response = await chat.send_message(final_prompt)
    return response.text


async def gemini_thinking(api_llm_key, prompt=None):
    """
    Continues the conversation with the Gemini model using the entire chat history.

    This function handles follow-up queries or prompts from the user. It appends the
    new prompt (if provided) to the chat history, converts the entire chat history
    into a single prompt string, and sends that string to the Gemini model.

    :param api_llm_key: The API key required for accessing the Google GenAI service.
    :param prompt: The user's follow-up question or instruction.
    :return: The text response generated by the Gemini model, reflecting the full conversation context so far.
    """
    client = genai.Client(api_key=api_llm_key, http_options={'api_version': 'v1alpha'})
    chat = client.aio.chats.create(model='gemini-2.0-flash-thinking-exp')

    # Copy of the previous history + new prompt
    temp_history = st.session_state.chat_history.copy()

    if prompt:
        temp_history.append({"role": "user", "content": prompt})

    # Build prompt string
    final_prompt = build_prompt_from_history(temp_history)

    # Send request
    response = await chat.send_message(final_prompt)
    return response.text
