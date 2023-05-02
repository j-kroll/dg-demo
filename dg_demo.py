import asyncio
from io import BytesIO
import json
import requests

from deepgram import Deepgram
from pydub import AudioSegment
from pydub.playback import play

from secrets import DEEPGRAM_API_KEY
from keywords import KEYWORDS
from sources import SOURCES


deepgram = Deepgram(DEEPGRAM_API_KEY)

def get_source(url, file_type):
  mimetype = f"audio/{file_type}"
  if url.startswith("http"):
    source = {
      "url": url
    }
  else:
    audio = open(url, "rb")
    source = {
      "buffer": audio,
      "mimetype": mimetype
    }
  return source

async def transcribe(audio):
  # TODO cache transcript per url to avoid re-transcribing
  # f = open("zoo_transcript.json")
  # response = json.loads(f.read())
  response = await asyncio.create_task(
    deepgram.transcription.prerecorded(
      audio,
      {
        "smart_format": True,
        "utterances": True,
        "model": "nova",
      }
    )
  )
  return response

def main():
  for url in SOURCES:
    file_type = url.split(".")[-1]
    audio_segment = AudioSegment.from_file(BytesIO(requests.get(url).content), format=file_type)
    source = get_source(url, file_type=file_type)
    transcript = asyncio.run(transcribe(source))
    print(f"Finding keywords: '{KEYWORDS}'")
    # TODO stem/lemmatize for not exact matches, "lemur" vs "lemurs"
    paragraphs = transcript["results"]["channels"][0]["alternatives"][0]["paragraphs"]["paragraphs"]
    for p in paragraphs:
      sentences = [s for s in p["sentences"]]
      for s in sentences:
        text = s["text"]
        if any([keyword.lower() in text.lower() for keyword in KEYWORDS]):
          print(f"---> {text}")
          start_ms = s["start"] * 1000
          end_ms = s["end"] * 1000
          print(f"Playing segment from {start_ms} to {end_ms} milliseconds.")
          play(audio_segment[start_ms:end_ms])

if __name__ == "__main__":
  main()
