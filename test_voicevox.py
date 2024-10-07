# -*- coding: utf-8 -*-
# 必要なライブラリをインポート
import json
import requests
import io
import numpy as np
import soundfile
import sounddevice as sd
from typing import Tuple

# VoiceVox APIと通信するためのクラス
class VoiceVoxAdapter:
    # VoiceVox APIのURLを設定
    URL = 'http://127.0.0.1:50021/'
    
    def __create_audio_query(self, text: str, speaker_id: int) -> dict:
        # テキストを音声に変換するためのクエリを作成
        params = {'text': text, 'speaker': speaker_id}
        response = requests.post(f"{self.URL}audio_query", params=params)
        return response.json()
    
    def __create_request_audio(self, query_data: dict, speaker_id: int) -> bytes:
        # 音声合成のリクエストを送信
        headers = {
            "accept": "audio/wav",
            "content-type": "application/json" 
        }
        response = requests.post(
            f"{self.URL}synthesis",
            params={'speaker': speaker_id},
            data=json.dumps(query_data),
            headers=headers
        )
        print(f"Synthesis status code: {response.status_code}")
        return response.content
    
    def get_voice(self, text: str, speaker_id: int = 3) -> Tuple[np.ndarray, int]:
        """音声データとサンプリングレートを返す

        Args:
            text (str): 音声を作成したいテキスト
            speaker_id (int, optional): 話者ID. デフォルトは3

        Returns:
            Tuple[numpy.ndarray, int]: 音声データとサンプリングレート
        """
        # テキストを音声に変換
        query_data = self.__create_audio_query(text, speaker_id)
        audio_bytes = self.__create_request_audio(query_data, speaker_id)
        
        # バイトデータを音声データに変換
        with io.BytesIO(audio_bytes) as audio_stream:
            return soundfile.read(audio_stream)

# 音声を再生するためのクラス
class PlaySound:
    def __init__(self, output_device_name: str = "CABLE Input") -> None:
        # 出力デバイスを設定
        self.output_device_id = self._search_output_device_id(output_device_name)
        sd.default.device = [0, self.output_device_id]  # 入力デバイスIDは0（未使用）
    
    def _search_output_device_id(self, output_device_name: str, output_device_host_api: int = 0) -> int:
        # 指定された名前の出力デバイスを検索
        devices = sd.query_devices()
        for device in devices:
            if (output_device_name in device["name"] and 
                device["hostapi"] == output_device_host_api):
                return device["index"]
        
        # デバイスが見つからない場合はエラーを発生
        raise ValueError(f"Output device '{output_device_name}' not found!")
    
    def play_sound(self, data: np.ndarray, rate: int) -> None:
        # 音声データを再生
        sd.play(data, rate)
        sd.wait()  # 再生が終わるまで待機

# メインの実行部分
if __name__ == '__main__':
    # ユーザーからテキスト入力を受け取る
    input_str = input("話す内容：")
    
    # VoiceVoxAdapterのインスタンスを作成
    voicevox_adapter = VoiceVoxAdapter()
    
    # PlaySoundのインスタンスを作成（出力デバイスを指定）
    play_sound = PlaySound("スピーカー")
    
    # テキストを音声データに変換
    data, rate = voicevox_adapter.get_voice(input_str, speaker_id=1)
    
    # 音声を再生
    play_sound.play_sound(data, rate)