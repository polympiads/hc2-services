
import hashlib
import random
import time
from typing import Dict

import requests


class CodeforcesAPI:
    def __init__(self, key: str, sec: str):
        self.__key = key
        self.__sec = sec

    def make_sig_hash (self, method: str, kwargs: Dict[str, str]):
        rand = random.randint(0, 100000)
        rand = str(rand).zfill(6)
        current_time = str(int(time.time()))
        kwargs["time"] = current_time
        kwargs["apiKey"] = self.__key

        vals = []
        for key in kwargs.keys():
            vals.append((key, kwargs[key]))
        vals.sort()

        strs = []
        for a, b in vals:
            strs.append(f"{a}={b}")
        params = "&".join(strs)
        api_sig = f"{rand}/{method}?{params}#{self.__sec}"
        kwargs["apiSig"] = rand + hashlib.sha512(api_sig.encode()).hexdigest()
    
    def get (self, method: str, params: Dict[str, str]):
        self.make_sig_hash(method, params)

        return requests.get( f"https://codeforces.com/api/{method}", params = params )
    def contest_status (self, contestId: str, groupCode: str = None):
        params = { "contestId": contestId }

        if groupCode is not None:
            params["groupCode"] = groupCode

        data = self.get( "contest.status", params ).json()
        if data['status'] != 'OK':
            raise Exception(data['comment'])
        
        status = []
        for submission in data['result']:
            status.append( (submission['id'], submission['verdict'], submission['author']['members'][0]['handle'], submission['problem']['index']) )
        
        return status
