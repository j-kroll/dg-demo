from deepgram import Deepgram
import asyncio, json
from secrets import DEEPGRAM_API_KEY

# Based on https://developers.deepgram.com/documentation/getting-started/prerecorded/

FILE = 'life-moves-pretty-fast.wav'
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
        'punctuate': True,
        'model': 'nova',
      }
    )
  )

  print(json.dumps(response, indent=4))

  # Write only the transcript to the console
  #print(response["results"]["channels"][0]["alternatives"][0]["transcript"])

try:
  asyncio.run(main())
except Exception as e:
  exception_type, exception_object, exception_traceback = sys.exc_info()
  line_number = exception_traceback.tb_lineno
  print(f'line {line_number}: {exception_type} - {e}')
