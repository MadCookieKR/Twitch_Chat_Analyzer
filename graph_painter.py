import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.dates as mdates
from chat import Chat


class GraphPainter:
    keywords = ['lmao', 'lol', 'lewd', 'yabe']

    def __init__(self, chatSegList: list[list[Chat]], keywords : list[str]):
        self.chatSegList = chatSegList
        self.isPaused = False
        self.acc = len(chatSegList[0])
        self.count = 1
        self.x = []
        self.y_highlight_score = []
        self.y_avg = []
        self.y_avg_15 = []  # 1.15배
        self.y_avg_2 = []  # 1.2배
        self.ani = FuncAnimation(plt.gcf(), self.animate, interval=100)
        if keywords:
            self.keywords = keywords
        print("Applied keywords : " + str(self.keywords))
        print("적용된 키워드 : " + str(self.keywords))

    def draw_chat_graph(self):
        plt.show()

    def switchPause(self):
        self.isPaused = not self.isPaused
        if self.isPaused:
            self.ani.pause()
        else:
            self.ani.resume()

    def animate(self, i):
        # 모든 챗을 분석했을 경우
        if self.count >= len(self.chatSegList):
            self.ani.pause()
            print("it's done !!!!!")
            return
        # 10초간 챗이 없는 구간일 경우 다음으로 넘어간다.
        if len(self.chatSegList[self.count]) == 0:
            self.count += 1
            return

        score = self.getHighlightScore(self.chatSegList[self.count])
        # 하이라이트 스코어는 (채팅 수 + 키워드가 일치한 수) 만큼으로 한다.
        self.x.append(self.chatSegList[self.count][0].time)
        self.y_highlight_score.append(score)
        avg = self.acc // self.count
        self.y_avg.append(avg)
        self.y_avg_15.append(avg * 1.15)
        self.y_avg_2.append(avg * 1.2)
        self.acc += score
        self.count += 1
        plt.cla()
        plt.xlabel('timeline')
        plt.ylabel('highlight score')  # chat count per 2 ~ 10 second

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.plot(self.x, self.y_highlight_score, label='realtime')
        plt.plot(self.x, self.y_avg, label='avg')
        plt.plot(self.x, self.y_avg_15, label='avg * 1.15')
        plt.plot(self.x, self.y_avg_2, label='avg * 1.2')

        plt.gcf().autofmt_xdate()
        plt.legend()

    def getHighlightScore(self, chat: list[Chat]):
        return len(chat) + self.getKeywordHitCount(chat)

    def getKeywordHitCount(self, chat: list[Chat]):
        return len([x for x in chat if self.isMsgContainsKeyword(x.msg)])

    def isMsgContainsKeyword(self, msg: str):
        target = msg.lower()
        return any(keyword in target for keyword in self.keywords)
