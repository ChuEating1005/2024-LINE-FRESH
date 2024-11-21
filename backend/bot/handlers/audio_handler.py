from linebot import LineBotApi
from linebot.models import AudioSendMessage, TextSendMessage
from django.conf import settings
import tempfile
from ailabs_asr.streaming import StreamingClient
from pydub import AudioSegment
from .utils import *

line_bot_api = LineBotApi(settings.LINE_ACCESS_TOKEN)

asr_sentences = []

def on_processing_sentence(message):
  print(f'word: {message["asr_sentence"]}')

def on_final_sentence(message):
  global asr_sentences
  final_sentence = message["asr_sentence"]
  asr_sentences.append(final_sentence)  # 將句子添加到緩存中
#   with open('transcription.txt', 'a', encoding='utf-8') as f:
#     f.write(message["asr_sentence"] + '\n')

 # initial Stream client with the key applied from Dev Console
asr_client = StreamingClient(
  key=settings.AUDIO_KEY)

def convert_audio(input_path, output_path):
    # 使用 pydub 進行轉換
    audio = AudioSegment.from_file(input_path)
    converted_audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
    converted_audio.export(output_path, format="wav")
    print(f"Audio converted to {output_path} with 16kHz, mono, 16 bits per sample.")

def process_audio_message(event):
    """
    Handle incoming audio messages
    """
    global asr_sentences
    asr_sentences = []
    try:
        # Get the audio content
        message_content = line_bot_api.get_message_content(event.message.id)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as temp_audio_file:
            for chunk in message_content.iter_content():
                temp_audio_file.write(chunk)
            temp_audio_file_path = temp_audio_file.name
        converted_audio_path = temp_audio_file_path.replace(".m4a", ".wav")
        convert_audio(temp_audio_file_path, converted_audio_path)
        asr_client.start_streaming_wav(
            pipeline='asr-zh-tw-std',
            file=converted_audio_path,
            on_processing_sentence=on_processing_sentence,
            on_final_sentence=on_final_sentence
        )
        # TODO: Add your audio processing logic here
        # You might want to:
        # 1. Save the audio file
        # 2. Process it (speech-to-text, analysis, etc.)
        # 3. Send appropriate response
        final_result = " ".join(asr_sentences)  # 合併所有句子
        print(f"Final result to user: {final_result}")

        generate_article(event, final_result)
    except Exception as e:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"Sorry, I couldn't process your audio message.")
        ) 