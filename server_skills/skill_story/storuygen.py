import random
import re
from os.path import dirname


class MarkovGen():
    def __init__(self, minsize=8, maxsize=20, names=False, new_names=None, banned=None, replaces=None):
        self.names = names
        if new_names is None:
            new_names = []
            for i in range(0, 3):
                new_names.append("person_" + str(i))
        self.pnames = new_names
        self.mode = 1
        self.minsize = minsize
        self.maxsize = maxsize
        self.freqDict = {}
        if banned is None:
            banned = [[]]
        if replaces is None:
            replaces = [[]]
        self.banned = banned
        self.replaces = replaces

    def replace_bads(self, text):
        lines = text
        for stuff in text:
            i = 0
            for cat in self.banned:
                for word in cat:
                    lines = lines.replace(word, random.choice(self.replaces[i]))
                i += 1
        return lines

    def add_to_dict(self, fileName):
        f = open(fileName, 'r')
        # phrases
        if self.mode == 1:
            lines = re.sub("\n", " \n", f.read()).lower().replace(".", "\n").replace('"', "\n").split('\n')
        else:
            lines = re.sub("\n", " \n", f.read()).lower().split(' ')
        # count frequencies curr -> succ
        for curr, succ in zip(lines[1:], lines[:-1]):
            # check if curr is already in the dict of dicts
            if curr not in self.freqDict:
                self.freqDict[curr] = {succ: 1}
            else:
                # check if the dict associated with curr already has succ
                if succ not in self.freqDict[curr]:
                    self.freqDict[curr][succ] = 1;
                else:
                    self.freqDict[curr][succ] += 1;

        # compute percentages
        probDict = {}
        for curr, currDict in self.freqDict.items():
            probDict[curr] = {}
            currTotal = sum(currDict.values())
            for succ in currDict:
                probDict[curr][succ] = currDict[succ] / currTotal
        self.freqDict = probDict

    def markov_next(self, curr):
        probDict = self.freqDict
        if curr not in probDict:
            next = random.choice(list(probDict.keys()))
            if self.names:
                next = random.choice(self.pnames) + ": " + next
            return next
        else:
            succProbs = probDict[curr]
            randProb = random.random()
            currProb = 0.0
            for succ in succProbs:
                currProb += succProbs[succ]
                if randProb <= currProb:
                    if self.names:
                        succ = random.choice(self.pnames) + ": " + succ
                    return succ
            next = random.choice(list(probDict.keys()))
            if self.names:
                next = random.choice(self.pnames) + ": " + next
            return next

    def generate(self, curr):
        if self.mode == 1:
            T = random.choice(range(self.minsize, self.maxsize))
        else:
            T = random.choice(range(self.minsize * 20, self.maxsize * 5))
        generated = [curr]
        for t in range(T):
            next = self.markov_next(generated[-1])
            if len(next) > 10:
                generated.append(next)
                if self.mode == 1:
                    generated.append("\n")
        generated = " ".join(generated)
        return self.replace_bads(generated)


starts = open(dirname(__file__) + "/start/sci_fi.txt").readlines()

# names in corpus to replace
names = ["SPOCK", "ONE", "ANDROMEDA", "HUNT", "RHADE", "HARPER", "TYR", "BEM", "COMPUTER", "BEKA",
         "TYLER", "PIKE", "GARISON", "BOYCE", "COLT", "KIRK", "UHURA", "BALOK", "BAILEY", "MCCOY",
         "SCOTT", "SULU", "k irk", "CHEKOV", "doctor", "captain", "jim", "enterprise", "surak", "klingon", "vulcan",
         " b ", " s ", " r ", " m "]

# characters
new_names = ["BOB"]

# banned words
banned = []
replaces = []
drugs = ["ayahuasca", "psilo", "marijuana", "music", "dxm", "tricorder", "tab", "drug", "chemical", "dope", "kush",
         "acid",
         "peyote", "hallucinogen", " m ", "smoked", "tabitha", "mescaline", "harmala", "cevs", "peak", "substance",
         "smoke",
         " trip ", "psychedelic", "mdma", "phenethylamine", "visual", "cannabis", "weed", "drug", "lsd", "dmt",
         "mushroom",
         "maoi", "jurema", "heroin",
         "stash", "2-cb", "2c-b", "2cb", " mg ", " ug ", " g ", "shroom", "crack"]
banned.append(drugs)
drug_replaces = ["artificial memorie", "engine", "positronic stuff", "computing power", "super-computer",
                 "galactic council", "pod bay",
                 "alien goo", "engine", "anti-matter", "flux capacitator", "artificial mind", "space ship", "computer",
                 "bot", "escape pod",
                 "AI", "synthetic", "alien", "data", "metadata", "time-machine", "medkit", "terminator",
                 "radioactive poop", "waste", "eletronic flux"]
replaces.append(drug_replaces)

story = random.choice(starts)
Adventure = MarkovGen(minsize=1, maxsize=4, names=False, new_names=new_names, banned=banned, replaces=replaces)
Adventure.add_to_dict(dirname(__file__) + "/styles/drugs.txt")
Dialog = MarkovGen(minsize=1, maxsize=3, names=True, new_names=new_names)
Dialog.add_to_dict(dirname(__file__) + "/dialog/sci_fi.txt")

for i in range(0, 10):
    story = Adventure.generate(story)
    story = Dialog.generate(story)

for name in names:
    story = story.replace(name.lower(), random.choice(new_names))

print story
