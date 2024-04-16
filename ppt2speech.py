from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from playsound import playsound
import os
import sys
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

load_dotenv()

client = OpenAI()

file_path = "./sampleppt/" +  sys.argv[1]
my_file = client.files.create(
  file=open(file_path, "rb"),
  purpose="assistants"
)
#print(my_file)

my_assistant = client.beta.assistants.create(
    instructions="You are a lecture speaker",
    name="LecturePresenter",
    tools=[{"type": "retrieval"}],
    model="gpt-3.5-turbo",
)
#print(my_assistant)

thread = client.beta.threads.create()

message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="give a presentation speech on first 3 slides of this file in natural language.",
    file_ids=[my_file.id],
)

run = client.beta.threads.runs.create_and_poll(
  thread_id=thread.id,
  assistant_id=my_assistant.id
)

#print(run)
def uniquify(path):
    filename, extension = os.path.splitext(path)
    counter = 1

    while os.path.exists(path):
        path = filename + " (" + str(counter) + ")" + extension
        counter += 1

    return path

if run.status == 'completed': 
  messages = client.beta.threads.messages.list(
    thread_id=thread.id
  )

  speech = messages.data[0].content[0].text.value
  print(speech)

  speech_file_path = uniquify("./output/speech.mp3")
  response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input=speech
  )

  response.stream_to_file(speech_file_path)

  playsound(speech_file_path)
else:
  print(run.status)

delete_response = client.beta.assistants.delete(my_assistant.id)
#print(delete_response)