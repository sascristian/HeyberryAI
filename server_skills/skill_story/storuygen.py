from mycroft.util.markov import MarkovChain
import random

limit = 25000
train = False

style = "lusiadas"
try:
    chain = MarkovChain(5, pad=False).load(style + ".json")
except:
    chain = MarkovChain(5, pad=False)


if train:

    print "reading corpus"
    with open("styles/" + style + ".txt", "r") as file:

      #  lines = file.readlines()
      #  if len(lines) < 2:
        lines = file.read()
        lines = lines.split("\n")

    print "training on: " + str(len(lines)) + " lines"
    c = 0
    for i in range(0, len(lines)):
        if i > limit:
            break
        line = random.choice(lines)
        lines.remove(line)
        if line.isdigit():
            continue
        line += "."
        line = line.decode("latin-1")
        words = line.split(" ")
        size = len(words)
        if size > 250:
            words = words[size - 100:]
        chain.add_tokens(words)
        if i%100 == 0:
            print "iter: " + str(i), "word_count: " + str(c)
            chain.save(style + ".json")
        c += len(words)

    print "iter: " + str(i), "word_count: " + str(c)
    chain.save(style + ".json")
    # remove trained lines from corpus
    with open("styles/" + style + ".txt", "w") as file:
        for line in lines:
            file.write(line+".\n")

print "generating\n\n\n"
generated = chain.generate_sequence(200)
text = ""
for word in generated:
    try:
        text += word
        if "." in word:
            text += "\n"
        elif "\n" not in word:
            text += " "
    except:
        pass
print text+"."

