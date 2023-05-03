import asyncio
from io import BytesIO
import json
import requests
import os

from deepgram import Deepgram
from langdetect import detect
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize
from pydub import AudioSegment
from pydub.playback import play
import streamlit as st

from key import DEEPGRAM_API_KEY
from keywords import KEYWORDS
from sources import SOURCES


deepgram = Deepgram(DEEPGRAM_API_KEY)

BOLD = '\033[1m'
UNDERLINE = '\033[4m'
END = '\033[0m'

# ('arabic', 'danish', 'dutch', 'english', 'finnish', 'french', 'german', 'hungarian', 'italian', 'norwegian', 'porter', 'portuguese', 'romanian', 'russian', 'spanish', 'swedish')
LANGUAGE_CODES = {
  "en": "english",
  "it": "italian",
  "pt": "portuguese",
  "fr": "french",
  "es": "spanish",
}

def initialize_stemmers(keyword_langs):
  stemmers_by_lang = {}
  keyword_langs = keyword_langs.values()
  for lang in keyword_langs:
    stemmer = SnowballStemmer(LANGUAGE_CODES[lang])
    stemmers_by_lang[lang] = stemmer
    print(f"Initialized stemmers for langs: {stemmers_by_lang.keys()}")
    return stemmers_by_lang

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
        "detect_language": True,
        "model": "nova",
      }
    )
  )
  with open(file_path, "w") as f:
    f.write(json.dumps(response, indent=4))
    print(f"Saved transcription: {file_path}")
  return response

def get_keyword_in_transcript(transcript, audio_segment, keyword, stemmer):
  paragraphs = transcript["results"]["channels"][0]["alternatives"][0]["paragraphs"]["paragraphs"]
  for p in paragraphs:
    sentences = [s for s in p["sentences"]]
    for s in sentences:
      text = s["text"]
      stemmed_words = {stemmer.stem(w).lower(): w for w in word_tokenize(text)}
      stemmed_keywords = {stemmer.stem(k.lower()): k for k in [keyword]}
      keyword_matches = [s_kw if s_kw in stemmed_words.keys() else None for s_kw in stemmed_keywords.keys()]
      if any(keyword_matches):
        text = print_sentence(stemmed_words, keyword_matches, text)
        start_ms = s["start"] * 1000
        end_ms = s["end"] * 1000
        play(audio_segment[start_ms:end_ms])
        return text

def print_sentence(stemmed_words, keyword_matches, text):
  for match in keyword_matches:
    if match:
      text = text.replace(stemmed_words[match], UNDERLINE + stemmed_words[match] + END)
  print(f"---> {text}")
  return text

def label_keyword_langs():
  keyword_langs = {}
  for keyword in KEYWORDS:
    lang = detect(keyword)
    keyword_langs[keyword] = lang
  return keyword_langs

def main():
  results = []
  print(f"Finding keywords: {KEYWORDS}")
  keyword_langs = label_keyword_langs()
  stemmers_by_lang = initialize_stemmers(keyword_langs)
  print(keyword_langs) # {"divina": "it"}
  for url in SOURCES:
    print()
    file_type = url.split(".")[-1]
    if url.startswith("http"):
      audio_segment = AudioSegment.from_file(BytesIO(requests.get(url).content), format=file_type)
    else:
      audio_segment = AudioSegment.from_file(url, format=file_type)
    source = get_source(url, file_type=file_type)
    transcript = asyncio.run(transcribe(url, source))
    transcript_language = transcript["results"]["channels"][0]["detected_language"]
    print(f"Detected language {transcript_language}")
    for keyword in KEYWORDS:
      if keyword_langs[keyword] == transcript_language: # "en", "en-US"
        print(f"Looking for keyword {keyword} in source {url}")
        print(f"Using stemmer in language {transcript_language}")
        sentence = get_keyword_in_transcript(transcript, audio_segment, keyword, stemmers_by_lang[transcript_language])
        results.append([url, keyword, transcript_language, sentence])
  st.table(results)

if __name__ == "__main__":
  main()
