import time
import threading
import wave  # wavファイルを扱うためのライブラリ

import pyaudio  # 録音機能を使うためのライブラリ

RECORD_SECONDS = 60  # 録音する時間の長さ（秒）
WAVE_OUTPUT_FILENAME = "sample.wav"  # 音声を保存するファイル名
iDeviceIndex = 0  # 録音デバイスのインデックス番号

# 基本情報の設定
FORMAT = pyaudio.paInt16  # 音声のフォーマット
CHANNELS = 1  # モノラル
RATE = 44100  # サンプルレート
CHUNK = 2 ** 11  # データ点数
audio = pyaudio.PyAudio()  # pyaudio.PyAudio()

stream = audio.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    input_device_index=iDeviceIndex,  # 録音デバイスのインデックス番号
    frames_per_buffer=CHUNK,
)

waveFile = wave.open(WAVE_OUTPUT_FILENAME, "wb")
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
waveFile.setframerate(RATE)

frameslist = []
lockframeslist = threading.Lock()
stopflag = False

def save_2_wav():
    global frameslist
    global lockframeslist
    global stopflag
    global wavefile

    while True:
        time.sleep(1)
        sz = len(frameslist)
        if sz <= 0:
            if stopflag == True:
                return
            else:
                continue
        lockframeslist.acquire()
        frames = frameslist.pop(0)
        lockframeslist.release()
        waveFile.writeframes(b"".join(frames))

def record_stream():
    global frameslist
    global lockframeslist
    global stopflag
    global stream

    for sec in range(0, 2):
        frames = []
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        lockframeslist.acquire()
        frameslist.append(frames)
        lockframeslist.release()

    stopflag = True

# --------------録音開始---------------
print("recording...")

thread1 = threading.Thread(target=record_stream)
thread2 = threading.Thread(target=save_2_wav)
thread1.start()
thread2.start()
thread1.join()
thread2.join()
print("finished recording")
# --------------録音終了---------------
stream.stop_stream()
stream.close()
audio.terminate()
