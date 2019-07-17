import threading
import time
import wave  # wavファイルを扱うためのライブラリ

import pyaudio  # 録音機能を使うためのライブラリ

RECORD_MIN = 180
RECORD_SECONDS = 10  # 録音する時間の長さ（秒）
WAVE_OUTPUT_FILENAME = "sample.wav"  # 音声を保存するファイル名
iDeviceName = "MacBook Proのマイク"

iDeviceIndex = 0  # 録音デバイスのインデックス番号

# 基本情報の設定
FORMAT = pyaudio.paInt16  # 音声のフォーマット
CHANNELS = 1  # モノラル
RATE = 44100  # サンプルレート
CHUNK = 2 ** 11  # データ点数

frameslist = []
lockframeslist = threading.Lock()
stopflag = False


def get_audio_index(iAudio, name):
    for x in range(0, iAudio.get_device_count()):
        str = iAudio.get_device_info_by_index(x)
        if str["name"] == name:
            return str["index"]
    return -1

def thread_save_2_wav(**kwargs):
    global frameslist
    global lockframeslist
    global stopflag

    waveFile = kwargs["waveFile"]

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


def thread_record_stream(**kwargs):
    global frameslist
    global lockframeslist
    global stopflag
    stream = kwargs["stream"]

    for sec in range(0, RECORD_MIN):
        frames = []
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        lockframeslist.acquire()
        frameslist.append(frames)
        lockframeslist.release()

    stopflag = True


def main():
    audio = pyaudio.PyAudio()  # pyaudio.PyAudio()

    iDeviceIndex = get_audio_index(audio, iDeviceName)
    if iDeviceIndex < 0:
        print("デバイスが見つかりませんでした")
        return -1

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

    # --------------録音開始---------------
    print("recording...")

    thread1 = threading.Thread(target=thread_record_stream, kwargs={"stream": stream})
    thread2 = threading.Thread(target=thread_save_2_wav, kwargs={"waveFile": waveFile})
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
    print("finished recording")
    # --------------録音終了---------------
    stream.stop_stream()
    stream.close()
    audio.terminate()

main()

