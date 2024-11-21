import wave
import os
from pydub import AudioSegment
import numpy as np

# Step 1: 轉換音檔為目標格式 (16kHz, mono, 16 bits per sample)
def convert_audio(input_path, output_path):
    # 使用 pydub 進行轉換
    audio = AudioSegment.from_file(input_path)
    converted_audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
    converted_audio.export(output_path, format="wav")
    print(f"Audio converted to {output_path} with 16kHz, mono, 16 bits per sample.")

# Step 2: 分割音檔為每個 2000 bytes 的 chunk
def split_audio_into_chunks(input_path, output_folder, chunk_size_bytes=2000):
    # 確保輸出資料夾存在
    os.makedirs(output_folder, exist_ok=True)

    with wave.open(input_path, "rb") as wav_file:
        # 獲取音檔參數
        sample_rate = wav_file.getframerate()
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        frame_size = channels * sample_width  # 每幀的 byte 大小
        frames_per_chunk = chunk_size_bytes // frame_size

        # 讀取音檔並分割
        total_frames = wav_file.getnframes()
        for i in range(0, total_frames, frames_per_chunk):
            wav_file.setpos(i)
            chunk_data = wav_file.readframes(frames_per_chunk)

            # 儲存 chunk 到新的檔案
            chunk_path = os.path.join(output_folder, f"chunk_{i // frames_per_chunk}.wav")
            with wave.open(chunk_path, "wb") as chunk_file:
                chunk_file.setnchannels(channels)
                chunk_file.setsampwidth(sample_width)
                chunk_file.setframerate(sample_rate)
                chunk_file.writeframes(chunk_data)
            print(f"Chunk saved: {chunk_path}")

# Step 3: 驗證每個 chunk 的大小
def verify_chunks(output_folder, chunk_size_bytes):
    for file_name in os.listdir(output_folder):
        if file_name.endswith(".wav"):
            file_path = os.path.join(output_folder, file_name)
            with wave.open(file_path, "rb") as wav_file:
                num_frames = wav_file.getnframes()
                sample_width = wav_file.getsampwidth()
                channels = wav_file.getnchannels()
                actual_chunk_size = num_frames * sample_width * channels
                assert actual_chunk_size <= chunk_size_bytes, f"Chunk size mismatch in {file_name}"
            print(f"{file_name} verified with size {actual_chunk_size} bytes.")

# 主程式
if __name__ == "__main__":
    # 設定路徑
    input_audio = "test.m4a"  # 輸入音檔
    converted_audio = "output.wav"  # 轉換後的音檔
    chunks_folder = "chunks"  # 分割後的音檔資料夾

    # 1. 將音檔轉換為符合格式
    convert_audio(input_audio, converted_audio)

    # 2. 將轉換後的音檔分割為 chunk
    split_audio_into_chunks(converted_audio, chunks_folder)

    # 3. 驗證每個 chunk 的大小
    verify_chunks(chunks_folder, chunk_size_bytes=2000)
