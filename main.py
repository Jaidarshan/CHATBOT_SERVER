import pathlib
import textwrap

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown


def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))


def introduce_bot():
    intro_message = """
    Hello! I am your AI-powered chatbot. You can ask me anything, and I will do my best to provide helpful information or assistance.

    Here are a few things you can do:
    * Ask me questions on any topic.
    * Type 'help' to see a list of commands.
    * Type 'quit' to end our session.

    Let's get started! What would you like to know today?
    """
    print(intro_message)


def show_help():
    help_message = """
    Here are some commands you can use:
    * 'help' - Show this help message.
    * 'quit' - End the session.

    You can ask me anything by simply typing your question or request.
    """
    print(help_message)


# Configure the API
GOOGLE_API_KEY = input("Enter your Google API key: ").strip()
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')

# Introduce the chatbot
introduce_bot()

# Start the main loop
quit_ = False
while not quit_:
    input_prompt = input("\nEnter your prompt: ").strip()

    if not input_prompt:
        print("Please enter a valid prompt or type 'help' for assistance.")
    elif input_prompt.lower() == "quit":
        print("Your session has ended. Goodbye!")
        quit_ = True
    elif input_prompt.lower() == "help":
        show_help()
    else:
        response = model.generate_content(input_prompt)
        print(response.text)
