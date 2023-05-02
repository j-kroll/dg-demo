import asyncio
from io import BytesIO
import json
import requests

from deepgram import Deepgram
from pydub import AudioSegment
from pydub.playback import play

from secrets import DEEPGRAM_API_KEY


file_path = "https://play.podtrac.com/npr-510289/edge1.pod.npr.org/anon.npr-mp3/npr/pmoney/2023/04/20230426_pmoney_e58d4524-d165-42f8-9fbd-10472ce664a0.mp3"
file_type = file_path.split(".")[-1]
mimetype = f"audio/{file_type}"
audio_segment = AudioSegment.from_file(BytesIO(requests.get(file_path).content), format=file_type)

async def main():

  deepgram = Deepgram(DEEPGRAM_API_KEY)

  if file_path.startswith("http"):
    source = {
      "url": file_path
    }
  else:
    audio = open(file_path, "rb")
    source = {
      "buffer": audio,
      "mimetype": mimetype
    }

  response = await asyncio.create_task(
    deepgram.transcription.prerecorded(
      source,
      {
        "smart_format": True,
        "utterances": True,
        "model": "nova",
      }
    )
  )

  # f = open("zoo_transcript.json")
  # response = json.loads(f.read())

  keyword = "lemurs".lower()
  # TODO stem/lemmatize for not exact matches, "lemur" vs "lemurs"

  print(f"Finding keyword: '{keyword}'")

  paragraphs = response["results"]["channels"][0]["alternatives"][0]["paragraphs"]["paragraphs"]
  for p in paragraphs:
    sentences = [s for s in p["sentences"]]
    for s in sentences:
      text = s["text"]
      if keyword in text.lower():
        print(f"---> {text}")
        start_ms = s["start"] * 1000
        end_ms = s["end"] * 1000
        print(f"Playing segment from {start_ms} to {end_ms} milliseconds.")
        play(audio_segment[start_ms:end_ms])

asyncio.run(main())
