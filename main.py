import pathlib
import textwrap

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown

def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

GOOGLE_API_KEY=input("Enter your google api key: ").strip()
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

quit_=0

while quit_==0:
  input_prompt=input("Enter your prompt: ")

  if input_prompt=="":
    print("Enter a valid prompt.")

  elif input_prompt.lower()=="quit":
    print("Your session has been ended")
    quit_=1

  else:
    response = model.generate_content(input_prompt)
    print(response.text)
