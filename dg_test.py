import asyncio
from io import BytesIO
import json
import requests

from deepgram import Deepgram
from pydub import AudioSegment
from pydub.playback import play

from secrets import DEEPGRAM_API_KEY


file_path = "https://play.podtrac.com/npr-510325/edge1.pod.npr.org/anon.npr-mp3/npr/indicator/2023/04/20230427_indicator_d90de0fd-411e-4022-9987-d8653ea58561.mp3"
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

  keyword = "tiktok".lower() # "lemurs".lower()

  full_transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]

  if keyword in full_transcript.lower(): # TODO stem/lemmatize for not exact matches, "lemur" vs "lemurs"
    print(f"Keyword {keyword} found in transcript!")

  sliced_words = [w["word"].lower() for w in response["results"]["channels"][0]["alternatives"][0]["words"]]

  if keyword in sliced_words:
    print(f"Keyword {keyword} found in words!")

  paragraphs = response["results"]["channels"][0]["alternatives"][0]["paragraphs"]["paragraphs"]
  for p in paragraphs:
    sentences = [s for s in p["sentences"]]
    for s in sentences:
      text = s["text"]
      if keyword in text.lower():
        print(f"Found keyword {keyword} in sentence: {text}")
        start_ms = s["start"] * 1000
        end_ms = s["end"] * 1000
        print(f"Playing segment from {start_ms} to {end_ms} milliseconds.")
        play(audio_segment[start_ms:end_ms])

asyncio.run(main())
