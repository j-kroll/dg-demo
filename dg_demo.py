import asyncio
from io import BytesIO
import json
import requests
import os

from deepgram import Deepgram
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from pydub import AudioSegment
from pydub.playback import play

from secrets import DEEPGRAM_API_KEY
from keywords import KEYWORDS
from sources import SOURCES


deepgram = Deepgram(DEEPGRAM_API_KEY)
ps = PorterStemmer()

BOLD = '\033[1m'
UNDERLINE = '\033[4m'
END = '\033[0m'

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

async def transcribe(url, audio):
  file_path = "./transcripts/" + url.split(".")[-2].split("/")[-1] + ".json"
  if os.path.exists("./transcripts/") and os.path.exists(file_path):
    f = open(file_path, "r")
    return json.loads(f.read())
  elif not os.path.exists("./transcripts/"):
    os.makedirs("./transcripts/")
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
  with open(file_path, "w") as f:
    f.write(json.dumps(response, indent=4))
    print(f"Saved transcription: {file_path}")
  return response

def get_keywords_in_transcript(transcript, audio_segment):
  paragraphs = transcript["results"]["channels"][0]["alternatives"][0]["paragraphs"]["paragraphs"]
  for p in paragraphs:
    sentences = [s for s in p["sentences"]]
    for s in sentences:
      text = s["text"]
      stemmed_words = {ps.stem(w).lower(): w for w in word_tokenize(text)}
      stemmed_keywords = {ps.stem(k.lower()): k for k in KEYWORDS}
      keyword_matches = [s_kw if s_kw in stemmed_words.keys() else None for s_kw in stemmed_keywords.keys()]
      if any(keyword_matches):
        print_sentence(stemmed_words, keyword_matches, text)
        start_ms = s["start"] * 1000
        end_ms = s["end"] * 1000
        play(audio_segment[start_ms:end_ms])

def print_sentence(stemmed_words, keyword_matches, text):
  for match in keyword_matches:
    if match:
      text = text.replace(stemmed_words[match], UNDERLINE + stemmed_words[match] + END)
  print(f"---> {text}")

def main():
  print(f"Finding keywords: {KEYWORDS}")
  for url in SOURCES:
    print()
    file_type = url.split(".")[-1]
    audio_segment = AudioSegment.from_file(BytesIO(requests.get(url).content), format=file_type)
    source = get_source(url, file_type=file_type)
    transcript = asyncio.run(transcribe(url, source))
    get_keywords_in_transcript(transcript, audio_segment)

if __name__ == "__main__":
  main()
