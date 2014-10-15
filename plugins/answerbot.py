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

    def shutdown(self):
        pass

    def get_answer(self, q):
        strippedQ = remove_punc(q)
        if strippedQ in self.answers:
            return self.answers[strippedQ][0]

        return None

    def on_chatmsg(self, ev):
        if ev.source.nick != "triviabot":
            return

        message = ev.arguments[0]

        if re.match("Question \d+: ", message) is not None:
            message = re.sub("Question \d+: ", "", message)
        else:
            return

        answer = self.get_answer(message)
        if answer is not None:
            print(answer)
            self.bot.say(answer.strip())
        
