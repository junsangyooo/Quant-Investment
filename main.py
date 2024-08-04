# 웹 소켓 모듈을 선언한다.
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode

import auth as au
import domestic as dm

import pandas as pd
import sys

# Basic instruction(blog): https://wikidocs.net/profile/info/book/13688
# Basic instruction(api): https://apiportal.koreainvestment.com/apiservice/oauth2#L_5c87ba63-740a-4166-93ac-803510bb9c02
# KoreaInvest Github: https://github.com/koreainvestment/open-trading-api
# Jocoding Github: https://github.com/youtube-jocoding/koreainvestment-autotrade

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
