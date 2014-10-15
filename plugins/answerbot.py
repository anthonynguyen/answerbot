import re
import string

from fuzzywuzzy import fuzz

def clean_str(s):
    return re.sub("[\.\?\!\"']", "", s).lower()

class AnswerPlugin:
    def __init__(self, bot):
        self.bot = bot

    def startup(self, config):
        self.bot.registerCommand("dump", self.cmd_dump)
        self.bot.registerEvent("public_message", self.on_chatmsg)

        answers = open(self.bot.basepath + "/trivia.db").readlines()
        answers = map(lambda a: a.strip(), answers)
        self.answers = {}
        for a in answers:
            p = a.split("*")
            self.answers[p[0]] = p[1:]

        self.question = None

    def shutdown(self):
        database = open(self.bot.basepath + "/trivia.db", "w")

        for a in self.answers:
            database.write("{}*{}\n".format(a, "*".join(self.answers[a])))

        database.close()
        self.bot.say("Answers dumped.")

    def cmd_dump(self, issuedBy, data):
        self.shutdown()

    def get_answer(self, q):
        candidates = []
        for pair in self.answers:
            score = fuzz.ratio(clean_str(pair), clean_str(q))
            if score == 100:
                return self.answers[pair][0]
            elif score >= 80: 
                candidates.append([score, self.answers[pair][0]])

        if candidates:
            candidates.sort(key = lambda x: x[0], reverse = True)
            print(candidates)
            return candidates[0][1]

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
            self.answers[self.question] = m[:]
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
        
