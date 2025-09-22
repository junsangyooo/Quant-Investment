import copy
import yaml
import requests
import json

import os

from collections import namedtuple
from datetime import datetime

clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')

key_bytes = 32

config_root = 'd:\\KIS\\config\\'  # Folder path where token file is saved, set the path so that it is hard for others to find.
token_tmp = config_root + 'KIS' + datetime.today().strftime("%Y%m%d")  # Token local save filename with year-month-day

# Check if the file managing the access token exists, if not create one
if os.path.exists(token_tmp) == False:
    f = open(token_tmp, "w+")

# App key, App secret, token, account number etc. managed here. Set your own path and filename.
# pip install PyYAML (package installation required)
with open('config.yaml', encoding='UTF-8') as f:
    _cfg = yaml.load(f, Loader=yaml.FullLoader)

_TRENV = tuple()
_last_auth_time = datetime.now()
_DEBUG = True

# Base header values
_base_headers = {
    "Content-Type": "application/json",
    "Accept": "text/plain",
    "charset": "UTF-8",
    'User-Agent': _cfg['my_agent']
}


# Save issued token (token value, expiration time, 1 day, if requested within 6 hours returns same token, notification sent when issued)
def save_token(my_token, my_expired):
    valid_date = datetime.strptime(my_expired, '%Y-%m-%d %H:%M:%S')
    with open(token_tmp, 'w', encoding='utf-8') as f:
        f.write(f'token: {my_token}\n')
        f.write(f'valid-date: {valid_date}\n')


# Read token (returns token value if valid, otherwise None)
def read_token():
    try:
        # Read saved token file
        with open(token_tmp, encoding='UTF-8') as f:
            tkg_tmp = yaml.load(f, Loader=yaml.FullLoader)

        # Token expiration datetime
        exp_dt = datetime.strftime(tkg_tmp['valid-date'], '%Y-%m-%d %H:%M:%S')
        # Current datetime
        now_dt = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

        # Check if token is still valid
        if exp_dt > now_dt:
            return tkg_tmp['token']
        else:
            return None
    except Exception as e:
        print('read token error: ', e)
        return None

# Return base header (deep copy)
def _getBaseHeader():
    return copy.deepcopy(_base_headers)

def _setTRENV(cfg):
    nt1 = namedtuple('KISEnv', ['my_app', 'my_sec', 'my_acct', 'my_prod', 'my_token', 'my_url'])
    d = {
        'my_app': cfg['my_app'],  # App key
        'my_sec': cfg['my_sec'],  # App secret
        'my_acct': cfg['my_acct'],  # Account number (8 digits)
        'my_prod': cfg['my_prod'],  # Account product code (2 digits)
        'my_token': cfg['my_token'],  # Token
        'my_url': cfg['my_url']  # Real trading domain (https://openapi.koreainvestment.com:9443)
    }  # Simulation domain (https://openapivts.koreainvestment.com:29443)

    global _TRENV
    _TRENV = nt1(**d)


def changeTREnv(token_key):
    cfg = dict()

    cfg['my_app'] = _cfg['my_app'] # App Key
    cfg['my_sec'] = _cfg['my_sec'] # App Secret
    cfg['my_acct'] = _cfg['my_acct'] # Account number (8 digits)
    cfg['my_prod'] = _cfg['my_prod'] # Product code (e.g., 01)
    cfg['my_token'] = token_key
    cfg['my_url'] = _cfg['prod']

    _setTRENV(cfg)

# Convert json_data to namedtuple for easier access
def _getResultObject(json_data):
    _tc_ = namedtuple('res', json_data.keys())
    return _tc_(**json_data)


# Issue token, valid for 1 day, same token if requested within 6 hours, notification is always sent when issued
def auth():
    p = {
        "grant_type": "client_credentials"
    }
    p["appkey"] = _cfg['my_app']
    p["appsecret"] = _cfg['my_sec']

    # Check if saved token exists
    saved_token = read_token()  
    if saved_token is None:  # If no saved token, request a new one
        url = f'{_cfg["prod"]}/oauth2/tokenP'
        res = requests.post(url, headers=_getBaseHeader(), data=json.dumps(p))  
        rescode = res.status_code
        if rescode == 200:  # Token successfully issued
            my_token = _getResultObject(res.json()).access_token  
            my_expired= _getResultObject(res.json()).access_token_token_expired  
            save_token(my_token, my_expired)  # Save new token
        else:
            print('Get Authentication token fail!\nYou have to restart your app!!!')
            return
    else:
        my_token = saved_token  # Use existing valid token

    # Save issued token into headers for API calls
    changeTREnv(f"Bearer {my_token}")

    _base_headers["authorization"] = _TRENV.my_token
    _base_headers["appkey"] = _TRENV.my_app
    _base_headers["appsecret"] = _TRENV.my_sec

    global _last_auth_time
    _last_auth_time = datetime.now()

    if (_DEBUG):
        print(f'[{_last_auth_time}] => get AUTH Key completed!')

# Re-authenticate if token has expired (valid for 1 day)
def reAuth(svr='prod', product=_cfg['my_prod']):
    n2 = datetime.now()
    if (n2 - _last_auth_time).seconds >= 86400:  
        auth(svr, product)

def getEnv():
    return _cfg

def getTREnv():
    return _TRENV

# Generate hash key for order API (optional, for preventing tampering)
# Input: HTTP Header, HTTP post param
# Output: None
def set_order_hash_key(h, p):
    url = f"{getTREnv().my_url}/uapi/hashkey"  # hashkey API URL

    res = requests.post(url, data=json.dumps(p), headers=h)
    rescode = res.status_code
    if rescode == 200:
        h['hashkey'] = _getResultObject(res.json()).HASH
    else:
        print("Error:", rescode)


# Wrapper for API responses
# Converts API responses into APIResp class for consistent handling
class APIResp:
    def __init__(self, resp):
        self._rescode = resp.status_code
        self._resp = resp
        self._header = self._setHeader()
        self._body = self._setBody()
        self._err_code = self._body.msg_cd
        self._err_message = self._body.msg1

    def getResCode(self):
        return self._rescode

    def _setHeader(self):
        fld = dict()
        for x in self._resp.headers.keys():
            if x.islower():
                fld[x] = self._resp.headers.get(x)
        _th_ = namedtuple('header', fld.keys())

        return _th_(**fld)

    def _setBody(self):
        _tb_ = namedtuple('body', self._resp.json().keys())

        return _tb_(**self._resp.json())

    def getHeader(self):
        return self._header

    def getBody(self):
        return self._body

    def getResponse(self):
        return self._resp

    def isOK(self):
        try:
            if (self.getBody().rt_cd == '0'):
                return True
            else:
                return False
        except:
            return False

    def getErrorCode(self):
        return self._err_code

    def getErrorMessage(self):
        return self._err_message

    def printAll(self):
        print("<Header>")
        for x in self.getHeader()._fields:
            print(f'\t-{x}: {getattr(self.getHeader(), x)}')
        print("<Body>")
        for x in self.getBody()._fields:
            print(f'\t-{x}: {getattr(self.getBody(), x)}')

    def printError(self, url):
        print('-------------------------------\nError in response: ', self.getResCode(), ' url=', url)
        print('rt_cd : ', self.getBody().rt_cd, '/ msg_cd : ',self.getErrorCode(), '/ msg1 : ',self.getErrorMessage())
        print('-------------------------------')

    # end of class APIResp

########### API call wrapping : Common API call handler

def _url_fetch(api_url, ptr_id, tr_cont, params, appendHeaders=None, postFlag=False, hashFlag=True):
    url = f"{getTREnv().my_url}{api_url}"

    headers = _getBaseHeader()  # Base headers

    # Set additional headers
    tr_id = ptr_id

    headers["tr_id"] = tr_id  # Transaction TR id
    headers["custtype"] = "P"  # Customer type: "P" = personal/company, "B" = partner
    headers["tr_cont"] = tr_cont  # Transaction continuation id

    if appendHeaders is not None:
        if len(appendHeaders) > 0:
            for x in appendHeaders.keys():
                headers[x] = appendHeaders.get(x)

    if (_DEBUG):
        print("< Sending Info >")
        print(f"URL: {url}, TR: {tr_id}")
        print(f"<header>\n{headers}")
        print(f"<body>\n{params}")

    if (postFlag):
        # if (hashFlag): set_order_hash_key(headers, params)
        res = requests.post(url, headers=headers, data=json.dumps(params))
    else:
        res = requests.get(url, headers=headers, params=params)

    if res.status_code == 200:
        ar = APIResp(res)
        if (_DEBUG): ar.printAll()
        return ar
    else:
        print("Error Code : " + str(res.status_code) + " | " + res.text)
        return None
