import re
from datetime import datetime as dateparser
import datetime
from chat import Chat
from graph_painter import GraphPainter
import os


def to_time(time) -> datetime:
    return dateparser.strptime(time, '%Y-%m-%d %H:%M:%S')


def parse_time(time) -> datetime:
    p = re.compile(r'([0-9]{2}). ([0-9]{2}). ([0-9]{2}). (.{2}) ([0-9]{2}):([0-9]{2}):([0-9]{2})')
    m = p.search(time)
    if m is None:
        return
    year = m.group(1)
    month = m.group(2)
    day = m.group(3)
    ampm = m.group(4)
    hour = m.group(5)
    minute = m.group(6)
    second = m.group(7)
    if ampm == '오후':
        hour = int(hour) + 12
    elif ampm == '오전' and hour == '12':
        hour = int(hour) - 12
    time = to_time(f'20{year}-{month}-{day} {hour}:{minute}:{second}')
    return time


# for analyzing, Group chat by 10sec.
# ex) group1 : 00:00~00:10, group2 : 00:10~00:20
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
    # last case
    chatSegList.append(chatSeg.copy())
    return chatSegList


def analyze(fileName, keywords: list[str]):
    chatList = []
    with open(fileName, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            p = re.compile(r'(\[.*\]) (\<.*\>) (.*)')
            m = p.search(line)
            if m is None:
                continue
            chatList.append(Chat(parse_time(m.group(1)), m.group(3)))

    if not chatList:
        print("Failed to get chat log")
        print("채팅을 받아오는데 실패했습니다.")
        return

    first_chat_hour = chatList[0].time.hour
    first_chat_minute = chatList[0].time.minute
    first_chat_second = chatList[0].time.second

    for chat in chatList:
        chat.time -= datetime.timedelta(hours=first_chat_hour, minutes=first_chat_minute, seconds=first_chat_second)

    GraphPainter(createChatSegList(chatList), keywords).draw_chat_graph()


if __name__ == '__main__':
    # print("getting required library...")
    # print("필요한 라이브러리를 가져오고 있습니다...")
    # os.system(f'cd {os.getcwd()}')
    # os.system('twitch_chatlog_installer.exe')

    video_id: str = input("Please type twitch video id.\n트위치 비디오 아이디를 입력해주세요.\n")
    keywords = list(input(
        "\nType keywords that you want to match.\nSeparate each keyword into spaces.\nIt doesn't matter whether it's lowercase or uppercase.\nex) lol yabe lmao\n* Type enter to keep the default setting(lmao lol lewd yabe)\n" +
        "매칭시킬 키워드를 입력해주세요.\n각 키워드를 띄어쓰기로 구분해서 입력해주세요.\n대소문자는 구분하지 않습니다.\n예) lol yabe lmao\n* 기본 설정(lmao lol lewd yabe) 유지하려면 엔터를 치세요.\n").split())
    print('Getting twitch chat log...')
    fileName = f'{video_id}.txt'
    if not os.path.isfile(fileName):
        os.system(f'cd {os.getcwd()}')
        os.system(f'twitch-chatlog -l 0 {video_id} > {video_id}.txt')
        print(f'chat log saved as {video_id}')
    print('start analyze!')
    analyze(fileName, keywords)
