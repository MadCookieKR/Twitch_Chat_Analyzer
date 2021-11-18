import re
from datetime import datetime as dateparser
import datetime
from chat import Chat
from graph_painter import GraphPainter
import os


def to_time(time):
    return dateparser.strptime(time, '%H:%M:%S')


def parse_time(time):
    p = re.compile(r'(.{2}) ([0-9]{2}:[0-9]{2}:[0-9]{2})')
    m = p.search(time)
    if m is None:
        return
    time = to_time(m.group(2))
    if time.hour != 12 and m.group(1) == '오후':
        time = time + datetime.timedelta(hours=12)
    return time


def createChatSegList(chatList: list[Chat]) -> list[list[Chat]]:
    chatSegList = []
    chatSeg = []
    timestamp = chatList[0].time
    # 10초 단위로 끊는다.
    interval = 10
    for chat in chatList:
        if chat.time > (timestamp + datetime.timedelta(seconds=interval)):
            chatSegList.append(chatSeg.copy())
            chatSeg.clear()
            timestamp = chat.time
        chatSeg.append(chat)
    return chatSegList


def analyze(fileName):
    chatList = []
    with open(fileName, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            p = re.compile(r'(\[.*\]) (\<.*\>) (.*)')
            m = p.search(line)
            if m is None:
                continue
            chatList.append(Chat(parse_time(m.group(1)), m.group(3)))

    first_chat_hour = chatList[0].time.hour
    first_chat_minute = chatList[0].time.minute
    first_chat_second = chatList[0].time.second

    for chat in chatList:
        chat.time -= datetime.timedelta(hours=first_chat_hour, minutes=first_chat_minute, seconds=first_chat_second)

    GraphPainter(createChatSegList(chatList)).draw_chat_graph()


if __name__ == '__main__':
    video_id: str = input("트위치 비디오 아이디를 입력해주세요. ")
    print('Getting twitch chat log...')
    os.system(f'cd {os.getcwd()}')
    os.system(f'twitch-chatlog -l 0 {video_id} > {video_id}.txt')
    print(f'chat log saved as {video_id}')
    print('start analyze!')
    analyze(f'{video_id}.txt')
    print('finished!!')
