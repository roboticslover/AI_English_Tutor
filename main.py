# Importing the Libraries
import streamlit as st
import openai
from openai import OpenAI
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Verify OpenAI Library Version
st.write(f"OpenAI Library Version: {openai.__version__}")

# Design the Application Structure
class Tutor:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def ask_question(self, prompt):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful English tutor."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

# Create the Streamlit Interface
st.sidebar.title("AI English Tutor")
selection = st.sidebar.radio("Go to", ["Vocabulary Practice", "Grammar Practice", "Conversation Practice"])

st.title(selection)

# Integrate OpenAI API
def load_api_key():
    try:
        api_key = os.getenv("OPENAI_API_KEY")  # Get API key from environment variable
        if not api_key:
            raise ValueError("API key not found")
        return api_key
    except Exception as e:
        st.error(f"API key not found. Please set the OPENAI_API_KEY environment variable. Details: {e}")
        return None

api_key = load_api_key()
if api_key:
    tutor = Tutor(api_key)
else:
    st.stop()

# Implement File Handling for User Progress
def save_progress(module, content):
    try:
        progress = {}
        if os.path.exists('progress.json'):
            with open('progress.json', 'r') as f:
                progress = json.load(f)
        if module not in progress:
            progress[module] = []
        progress[module].append(content)
        with open('progress.json', 'w') as f:
            json.dump(progress, f)
    except Exception as e:
        st.error(f'An error occurred while saving your progress: {e}')

# Develop Vocabulary Practice Module
if selection == "Vocabulary Practice":
    st.subheader("Learn New Words")
    word = st.text_input('Enter a word that you want to learn:')
    if st.button('Get Definition'):
        if word:
            try:
                prompt = f"Define the word '{word}' and use it in a sentence."
                definition = tutor.ask_question(prompt)
                st.write(definition)
                save_progress('Vocabulary', {'word': word, 'definition': definition})
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a word.")

# Develop Grammar Practice Module
if selection == "Grammar Practice":
    st.subheader('Improve Your Sentences')
    sentence = st.text_area('Enter a sentence you want to check:')
    if st.button('Check Grammar'):
        if sentence:
            try:
                prompt = f"Correct the grammar of the following sentence and explain the changes:\n\n{sentence}"
                correction = tutor.ask_question(prompt)
                st.write(correction)
                save_progress('Grammar', {'sentence': sentence, 'correction': correction})
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a sentence.")

# Implement Conversation Practice Module
if selection == "Conversation Practice":
    st.subheader('Practice Conversing in English')
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    user_input = st.text_input("You:", key="conversation_input")
    if st.button('Send'):
        if user_input:
            try:
                # Append user's input to conversation history
                st.session_state.conversation_history.append({"role": "user", "content": user_input})
                # Create a prompt with the conversation history
                conversation = "\n".join([f"{turn['role'].capitalize()}: {turn['content']}" for turn in st.session_state.conversation_history])
                prompt = conversation + "\nAI:"
                # Get the AI's response
                ai_response = tutor.ask_question(prompt)
                # Append AI's response to conversation history
                st.session_state.conversation_history.append({"role": "ai", "content": ai_response})
                # Display the conversation
                for turn in st.session_state.conversation_history[-4:]:  # Display last 4 turns
                    st.write(f"**{turn['role'].capitalize()}:** {turn['content']}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("Please enter a message to continue the conversation.")