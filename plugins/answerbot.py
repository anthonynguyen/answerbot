import re
import string

def remove_punc(s):
    return re.sub("[\.\?\!]", "", s)

class AnswerPlugin:
    def __init__(self, bot):
        self.bot = bot

    def startup(self, config):
        self.bot.registerEvent("public_message", self.on_chatmsg)

        answers = open(self.bot.basepath + "/trivia.db").readlines()
        answers = map(lambda s: remove_punc(s), answers)
        self.answers = {}
        for a in answers:
            p = a.split("*")
            self.answers[p[0]] = p[1:]

        self.question = None

    def shutdown(self):
        pass

    def get_answer(self, q):
        strippedQ = remove_punc(q)
        if strippedQ in self.answers:
            return self.answers[strippedQ][0]

        return None

    _QUESTIONRE = re.compile("Question \d+( \(.+?\))?: ")
    _ANSWERRE = re.compile("Time's up! The answer was: (.+)")
    def on_chatmsg(self, ev):
        if ev.source.nick != "triviabot":
            return

        message = ev.arguments[0]

        if message == "Say !trivia ?library? to play again.":
            self.bot.say("!trivia")
            return

        m = self._ANSWERRE.findall(message)
        if m and self.question is not None:
            self.bot.say("Learned: {}".format(m[0].strip()))
            self.answers[remove_punc(self.question)] = m[:]
            self.question = None
            return

        if self._QUESTIONRE.match(message) is not None:
            message = self._QUESTIONRE.sub("", message)
            print("Question seen: {}".format(message))
            self.question = message.strip()

        answer = self.get_answer(message)
        if answer is not None:
            self.question = None
            self.bot.say(answer.strip())
        
