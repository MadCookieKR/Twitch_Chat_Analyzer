import datetime


class Chat:
    def __init__(self, time: datetime, msg: str):
        self.time = time
        self.msg = msg

    def print(self):
        print(f'time : {self.time} msg : {self.msg}')
