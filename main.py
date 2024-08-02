# 웹 소켓 모듈을 선언한다.
import websockets
import json
import requests
import os
import asyncio
import time

from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode

clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')

key_bytes = 32

# Basic instruction(blog): https://wikidocs.net/profile/info/book/13688
# Basic instruction(api): https://apiportal.koreainvestment.com/apiservice/oauth2#L_5c87ba63-740a-4166-93ac-803510bb9c02
# KoreaInvest Github: https://github.com/koreainvestment/open-trading-api
# Jocoding Github: https://github.com/youtube-jocoding/koreainvestment-autotrade
# postman.com/
# 계좌번호: 64428904
APP_KEY = "PS87iiWlksmzSU8JilwwZyO6I6pH4k4qKXeR"
APP_SECRET = "E9mgaarv+ndZ93+LU2+bKjYWAXHanH8+g0vtDLCYVN6sAKX81YQNJAO3SajR74nzboVgPu1NA2jQkGJai9pCAe/8gTEGTM1L58udnrRQUpAZTP9Jes3d3X06a3iBsO6RF0EA2qyQZtmvWuesHnO7Gl653+wcFZAIw+mydJTFQAp1pI3Vgbw="

headers = {"content-type":"application/json"}
body = {"grant_type":"client_credentials",
        "appkey":APP_KEY, 
        "appsecret":APP_SECRET}

URL_BASE = "https://openapivts.koreainvestment.com:29443" #모의투자서비스
PATH = "oauth2/tokenP"
URL = f"{URL_BASE}/{PATH}"

res = requests.post(URL, headers=headers, data=json.dumps(body))
ACCESS_TOKEN = res.json()["access_token"]
print(URL)
print(ACCESS_TOKEN)

# # AES256 DECODE
# def aes_cbc_base64_dec(key, iv, cipher_text):
#     """
#     :param key:  str type AES256 secret key value
#     :param iv: str type AES256 Initialize Vector
#     :param cipher_text: Base64 encoded AES256 str
#     :return: Base64-AES256 decodec str
#     """
#     cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv.encode('utf-8'))
#     return bytes.decode(unpad(cipher.decrypt(b64decode(cipher_text)), AES.block_size))
