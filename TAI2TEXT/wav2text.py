from ailabs_asr.streaming import StreamingClient

def on_processing_sentence(message):
  print(f'word: {message["asr_sentence"]}')

def on_final_sentence(message):
  print(f'sentence: {message["asr_sentence"]}')
  with open('transcription.txt', 'a', encoding='utf-8') as f:
    f.write(message["asr_sentence"] + '\n')

 # initial Stream client with the key applied from Dev Console
asr_client = StreamingClient(
  key='')
# key 在 LINE裡 阿不要上傳太多音檔測試 我會被收錢 ( ͡° ͜ʖ ͡°)

# start Streaming with a wav file
asr_client.start_streaming_wav(
  pipeline='asr-zh-tw-std',
  # verbose=True,
  file='output.wav', #remove 'file' to switch to streaming mode. 
  on_processing_sentence=on_processing_sentence,
  on_final_sentence=on_final_sentence)
