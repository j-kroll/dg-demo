from deepgram import Deepgram
import asyncio, json
from secrets import DEEPGRAM_API_KEY

# Based on https://developers.deepgram.com/documentation/getting-started/prerecorded/

FILE = '/users/julia/Downloads/PM_why_zoos_cant_buy_sell_animals.mp3'
MIMETYPE = 'audio/wav'

async def main():

  deepgram = Deepgram(DEEPGRAM_API_KEY)

  if FILE.startswith('http'):
    source = {
      'url': FILE
    }
  else:
    audio = open(FILE, 'rb')

    source = {
      'buffer': audio,
      'mimetype': MIMETYPE
    }

  response = await asyncio.create_task(
    deepgram.transcription.prerecorded(
      source,
      {
        'smart_format': True,
        'utterances': True,
        'model': 'nova',
      }
    )
  )

  # print(json.dumps(response, indent=4))

  # Write only the transcript to the console
  #print(response["results"]["channels"][0]["alternatives"][0]["transcript"])

  keyword = "lemurs"

  full_transcript = response["results"]["channels"][0]["alternatives"][0]["transcript"]

  if keyword in full_transcript: # TODO stem/lemmatize for not exact matches, "lemur" vs "lemurs"
    print(f"Keyword {keyword} found in transcript!")

  sliced_words = [w["word"] for w in response["results"]["channels"][0]["alternatives"][0]["words"]]

  if keyword in sliced_words:
    print(f"Keyword {keyword} found in words!")

  paragraphs = response["results"]["channels"][0]["alternatives"][0]["paragraphs"]["paragraphs"]
  for p in paragraphs:
    sentences = [s["text"] for s in p["sentences"]]
    for s in sentences:
      if keyword in s:
        print(f"Found keyword {keyword} in sentence: {s}")

try:
  asyncio.run(main())
except Exception as e:
  exception_type, exception_object, exception_traceback = sys.exc_info()
  line_number = exception_traceback.tb_lineno
  print(f'line {line_number}: {exception_type} - {e}')
