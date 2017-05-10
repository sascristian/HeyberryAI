# LILACS chatbot skill

this skill tags entitys in all utterances, then uses concept net backend to get possible sentences using those entitys and says one at random

this ensures you get a reply related to subject

takes advantage of converse method to not let lilacs-core answer questions

it is possible to activate this mode vocally, it starts of by default

# usage

to activate this skill

        start chatbot

to de-activate

        stop chatbot
        talk seriously

# output

            do you want to play nuclear warfare
            2017-04-23 21:50:33,533 - CLIClient - INFO - Speak: being bored would make you want to play

            what do you think about war
            2017-04-23 21:50:47,355 - CLIClient - INFO - Speak: i dont understand the question

            who is satan
            2017-04-23 21:51:07,811 - CLIClient - INFO - Speak: Satan is a fallen angel

            do you eat
            2017-04-23 21:51:16,257 - CLIClient - INFO - Speak: i dont understand the question

            what is your favorite food
            2017-04-23 21:51:25,672 - CLIClient - INFO - Speak: favorite is a type of choice

            what is your favorite food
            2017-04-23 21:51:35,725 - CLIClient - INFO - Speak: preferit is a translation of favorite

            do you like meat
            2017-04-23 21:51:46,755 - CLIClient - INFO - Speak: steak is related to meat

            do you like cheese
            2017-04-23 21:55:04,139 - CLIClient - INFO - Speak: *Something you find at the market is cheese

            do you have a cat
            2017-04-23 21:55:37,026 - CLIClient - INFO - Speak: dog is not cat

            do you have a dog
            2017-04-23 21:58:31,427 - CLIClient - INFO - Speak: a dog is a kind of mammal

            are you alive
            2017-04-23 21:58:37,460 - CLIClient - INFO - Speak: If you want to breathe then you should be alive

            do you love me
            2017-04-23 21:58:49,236 - CLIClient - INFO - Speak: Love is an emotion

            do you have emotions
            2017-04-23 21:58:54,895 - CLIClient - INFO - Speak: Emotions can make a person dangerous to others

            are you a robot
            2017-04-23 21:59:06,424 - CLIClient - INFO - Speak: A robot is an automation


