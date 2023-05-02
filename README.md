# dg-demo

## About

Search for keywords in a corpus of audio files. Inspect both the text and audio of the sentences containing the keyword.

## Setup

1. Install the requirements:
```
pip3 install -r requirements.txt
```

1. Add your API key in `secrets.py`

## Run the code:

```
python3 dg_demo.py
```

## Example output

Given a keyword "lemurs" and the podcast [Why zoos can't buy or sell animals](https://play.podtrac.com/npr-510289/edge1.pod.npr.org/anon.npr-mp3/npr/pmoney/2023/04/20230426_pmoney_e58d4524-d165-42f8-9fbd-10472ce664a0.mp3?d=1003&size=16050095&e=1172161875&t=podcast&p=510289&awEpisodeId=1172161875&awCollectionId=510289&sc=siteplayer&aw_0_1st.playerid=siteplayer):

```
% python3 dg_demo.py
Finding keyword: 'lemurs'
---> Still on the list, lemurs.
Playing segment from 967105.04 to 969125.0 milliseconds.
Input #0, wav, from '/var/folders/1j/t0lwqrz93gj0np_r1sdf505w0000gn/T/tmp2juu3a0g.wav':
  Duration: 00:00:02.02, bitrate: 1411 kb/s
  Stream #0:0: Audio: pcm_s16le ([1][0][0][0] / 0x0001), 44100 Hz, 2 channels, s16, 1411 kb/s
   1.94 M-A:  0.000 fd=   0 aq=    0KB vq=    0KB sq=    0B f=0/0   
---> Calgary wants black and white lemurs.
Playing segment from 969905.0 to 971765.0 milliseconds.
Input #0, wav, from '/var/folders/1j/t0lwqrz93gj0np_r1sdf505w0000gn/T/tmpgxxz3t0q.wav':
  Duration: 00:00:01.86, bitrate: 1411 kb/s
  Stream #0:0: Audio: pcm_s16le ([1][0][0][0] / 0x0001), 44100 Hz, 2 channels, s16, 1411 kb/s
   1.79 M-A:  0.000 fd=   0 aq=    0KB vq=    0KB sq=    0B f=0/0     
```
