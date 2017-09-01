# LILACS

LILACS is a learning and comprehension subsystem

![LILACSS](https://github.com/ElliotTheRobot/LILACS-mycroft-core/raw/dev/lilacs-core.jpg)

The idea is that Jarbas gathers knowledge about anything it hears, searches info
 on several possible knowledge backends, and learns from user input

This knowledge comes both in the form of connections/properties of subjects and text info, this allows mycroft:

    to be vocally programmed about relationships of things (music tastes, family relationships)
    to gather all the info from the internet, more backends can be added any time
    to deduce answers from node relationships and answer several kinds of questions
    to be more personal
        "individual" knowledge between units
        a "personality" depending on usage history
        can "talk/rant" about subjects
    store gathered knowledge in several fashions
        collective database
        personal database

The job of lilacs is to understand concepts and answer questions about them

[![LILACS learning demo](https://img.youtube.com/vi/BPYOC1Dass4/0.jpg)](http://www.youtube.com/watch?v=BPYOC1Dass4)

# Step 1: Understanding what is being asked

The first job of LILACS is to understand what any kind of text is talking about,
Is it a question? What kind of question? What is the the question about?

The first thing LILACS does is run the text trough the LILACS Question Parser

### LILACS Question Parser ###

LILACSQuestionParser can be imported and used by any skill

    from jarbas_utils.question_parser import LILACSQuestionParser, RegexQuestionParser

The question parser starts by using some regex rules to try to understand the
question, it gives the following info

- 'QuestionWord': the word that defines the kind of question being asked
- 'QuestionVerb': the verb that connects the question subjects
- 'QuestionTargetWord': word that change meaning of question (of)
- 'QuestionTargetWord2': other word that change meaning of question (of)
- 'Query1': main subject of question
- 'Query2': second subject of question
- 'QuestionPerson': about wich person is the question about
- 'Query': subject of the question

Some examples:

        Question: what is the speed of light
        {'Query2': 'light', 'Query1': ' is the speed', 'QuestionTargetWord': 'of', 'QuestionWord': 'what', 'Query': ' is the speed light'}

        Question: who are you
        {'QuestionWord': 'who', 'Query': 'you', 'QuestionVerb': 'are'}

        Question: what is war
        {'QuestionWord': 'what', 'Query': 'war', 'QuestionVerb': 'is'}


After this LILACS uses dbpedia spotlight to extract concepts from the sentence

          Question: how to kill animals ( a cow ) and make meat
          center_node: kill
          target_node: animals
          parents: {u'animals': [u'Species', u'Eukaryote', u'Animal'], u'cow': [u'Species', u'Eukaryote', u'Animal', u'Mammal']}
          relevant_nodes: [u'meat', u'cow']
          synonims: {u'kill': u'murder', u'cow': u'cattle'}

If no concept is tagged from dbpedia lilacs will use the query from regex
instead with some extra processing to handle "noise"


The last step is to normalize the text, for this the question parser lenmmatize
words and remove plurals, some extra processing is done for
changing concepts like "me" and "your" to "current_user" and "self"

Some examples of final question parser output:

            Question: think about the meaning of life
            question_type: think
            center_node: meaning
            target_node: life
            parents: {}
            relevant_nodes: []
            synonims: {}
            parse: {'Query2': 'life', 'Query1': 'the meaning', 'QuestionTargetWord': 'about ', 'QuestionWord': 'think', 'QuestionVerb': None, 'Query': 'the meaning life', 'QuestionTargetWord2': 'of '}

            Question: what is the speed of light
            question_type: what
            center_node: speed
            target_node: light
            parents: {}
            relevant_nodes: []
            synonims: {}
            parse: {'QuestionWord': 'what', 'Query': 'speed of light', 'QuestionVerb': 'is'}

            Question: who are you
            question_type: who
            center_node: self
            target_node:
            parents: {}
            relevant_nodes: []
            synonims: {}
            parse: {'QuestionWord': 'who', 'Query': 'you', 'QuestionVerb': 'are'}

            Question: who am i
            question_type: who
            center_node: current_user
            target_node:
            parents: {}
            relevant_nodes: []
            synonims: {}
            parse: {'QuestionWord': 'who', 'Query': 'i', 'QuestionVerb': 'am'}

            Question: what is my favorite song
            question_type: what
            center_node: favorite song
            target_node: current user
            parents: {}
            relevant_nodes: []
            synonims: {u'favorite song': u"people's choice award for favorite song of the year"}
            parse: {'QuestionWord': 'what', 'Query': 'my favorite song', 'QuestionVerb': 'is'}

            Question: what is your favorite book
            question_type: what
            center_node: self
            target_node: favorite book
            parents: {}
            relevant_nodes: [u'favorite']
            synonims: {u'favorite': u'favourite'}
            parse: {'QuestionWord': 'what', 'Query': 'your favorite book', 'QuestionVerb': 'is'}

            Question: who is my cousin
            question_type: who
            center_node: cousin
            target_node: current user
            parents: {}
            relevant_nodes: []
            synonims: {}
            parse: {'QuestionWord': 'who', 'Query': 'my cousin', 'QuestionVerb': 'is'}

            Question: what is war
            question_type: what
            center_node: war
            target_node:
            parents: {}
            relevant_nodes: []
            synonims: {}
            parse: {'QuestionWord': 'what', 'Query': 'war', 'QuestionVerb': 'is'}

            Question: how to kill animals ( a cow ) and make meat
            question_type: how
            center_node: kill
            target_node: animal
            parents: {u'cow': [u'specie', u'eukaryote', u'animal', u'mammal'], u'animal': [u'specie', u'eukaryote', u'animal']}
            relevant_nodes: [u'cow', u'meat']
            synonims: {u'kill': u'murder', u'cow': u'cattle'}
            parse: {'QuestionWord': 'how', 'Query': 'kill animals ( cow ) and make meat', 'QuestionVerb': 'to'}

            Question: what is a living being
            question_type: what
            center_node: living being
            target_node:
            parents: {}
            relevant_nodes: [u'living']
            synonims: {u'living': u'life'}
            parse: {'QuestionWord': 'what', 'Query': 'living being', 'QuestionVerb': 'is'}

            Question: why are humans living beings
            question_type: why
            center_node: human
            target_node: living being
            parents: {}
            relevant_nodes: [u'living being']
            synonims: {u'living beings': u'life'}
            parse: {'QuestionWord': 'why', 'Query': 'humans living beings', 'QuestionVerb': 'are'}

            Question: give examples of animals
            question_type: examples
            center_node: animal
            target_node:
            parents: {u'animal': [u'specie', u'eukaryote', u'animal']}
            relevant_nodes: []
            synonims: {}
            parse: {'QuestionWord': 'examples', 'Query': 'animals', 'QuestionVerb': 'of'}

            Question: how do i make money with bitcoin
            question_type: how
            center_node: current user
            target_node: money
            parents: {u'bitcoin': [u'currency']}
            relevant_nodes: [u'bitcoin']
            synonims: {}
            parse: {'QuestionWord': 'how', 'Query': 'i make money with bitcoin', 'QuestionVerb': 'do'}

            Question: how can i win bitcoin
            question_type: how
            center_node: current user
            target_node: win
            parents: {u'bitcoin': [u'currency']}
            relevant_nodes: [u'bitcoin']
            synonims: {u'win': u'win\u2013loss record (pitching)'}
            parse: {'QuestionWord': 'how', 'Query': 'i win bitcoin', 'QuestionVerb': 'can'}

            Question: are the prophets with me
            question_type: are
            center_node: prophet
            target_node: current user
            parents: {}
            relevant_nodes: []
            synonims: {}
            parse: {'Query2': ' me', 'Query1': 'the prophets', 'QuestionTargetWord': 'with', 'QuestionWord': 'are', 'QuestionVerb': None, 'Query': 'the prophets  me', 'QuestionTargetWord2': None}

            Question: is your god evil
            question_type: is
            center_node: god
            target_node: evil
            parents: {}
            relevant_nodes: []
            synonims: {}
            parse: {'QuestionWord': 'is', 'Query': 'god evil', 'QuestionPerson': 'your'}

# step 2 - Process tagged concepts and question type

LILACS-core, the fallback skill that handles the questions, will then
disambiguate between some question types

disambiguation between question types using 'QuestionTargetWord':

"how to X" and "how tall is X"

"what is X" and "what is X of Y"

'QuestionTargetWord2' is useful for correctly understand the subjects of
sentences with more modifier words like

    Question: think about the meaning of life
    'QuestionTargetWord': 'about '
    'QuestionTargetWord2': 'of '

Instead of seeking concepts related to "meaning", lilacs will now seek
concepts that relate "meaning" and "life"

# step 3 - Retrieval of information

The KnowledgeQuery class can be imported and used from other skills as follows

    from jarbas_utils.skill_tools import KnowledgeQuery

    self.service = KnowledgeQuery()

    self.service.adquire("subject", "optionally desired knowledge backend here")

Depending on the kind of question LILACS will now try to retrieve information,
for this LILACS uses a number of different sources:

        - Wikipedia
        - Wikidata
        - Dbpedia
        - ConceptNet
        - Wordnik
        - Wikihow
        - Wolfram Alpha

Depending on the question type these are called with different priorities

If the question was not understood or the question type not yet accounted for
LILACS attempts to use wolfram alpha, in the future maybe even ask the user, or
one of many trusted users

Each of these sources is also a skill that can be triggered with

"test SOURCE with X", "what does SOURCE say about X"

# Step 4 - Node relationships

Each concept in LILACS is stored as a "concept node"

Each connection also has a weight determining how strong the connection is

Under data any arbitrary field can be added


    Node:
       name: <- the concept this node is about
       type: "informational"   <- general info, or about a person
       Connections:
           synonims: []  <- is the same as
           antonims: [] <- can never be related to
           parents: {name : weight }  <- is an instance of
           childs: {name : weight } <- can have the following instances
           cousins: {name : weight } <- somewhat related subjects
           spawns: {name : weight }  <- what comes from this?
           spawned_by: {name : weight } <- where does this come from?
           consumes: {name : weight } <- what does this need/spend ?
           consumed_by: {name : weight }  <- what consumes this?
           parts : {name : weight } <- what smaller nodes can this be divided into?
           part_off: {name : weight } <- what can be made out of this?
       Data:
            description: wikidata description_field
            abstract: dbpedia abstract
            summary: wikipedia_summary
            pics: [ wikipedia pic, dbpedia pic ]
            infobox: {wikipedia infobox}
            wikidata: {wikidata_dict}
            props: [wikidata_properties] <- if we can parse this appropriatly we can make connections
            links: [ wikipedia link, dbpedia link  ]
            external_links[ suggested links from dbpedia]

Currently the following relationships are "crawled" in order to answer questions


# step 5 - Node storage

Currently all nodes are stored as .json object, this is temporary and eventually
 several backends should be available to use

 The LILACS storage skill will handle this and is responsible to listen for save
  and load node messages, a good analogy would be retrieving long term memory
  and passing it to short term memory

# step 6 - Filling nodes

Nodes are auto populated with some info from the knowledge sources, one way to
trigger this is with questions of the kind "think about" or "talk about"


        Input: think about evil
        2017-04-21 23:30:15,548 - CLIClient - INFO - Speak: Evil, in a general context, is the absence or opposite of that which is described as being good. Often, evil is used to denote profound immorality. In certain religious contexts, evil has been described as a supernatural force. Definitions of evil vary, as does the analysis of its motives. However, elements that are commonly associated with evil involve unbalanced behavior involving expediency, selfishness, ignorance, or neglect. In cultures with an Abrahamic religious influence, evil is usually perceived as the dualistic antagonistic opposite of good, in which good should prevail and evil should be defeated. In cultures with Buddhist spiritual influence, both good and evil are perceived as part of an antagonistic duality that itself must be overcome through achieving Śūnyatā meaning emptiness in the sense of recognition of good and evil being two opposing principles but not a reality, emptying the duality of them, and achieving a oneness. The philosophical question of whether morality is absolute, relative, or illusory leads to questions about the nature of evil, with views falling into one of four opposed camps: moral absolutism, amoralism, moral relativism, and moral universalism. While the term is applied to events and conditions without agency, the forms of evil addressed in this article presume an evildoer or doers.
        2017-04-21 23:30:15,554 - CLIClient - INFO - Speak: Satan (Hebrew: שָּׂטָן satan, meaning "adversary"; Arabic: شيطان shaitan, meaning; "astray", "distant", or sometimes "devil") is a figure appearing in the texts of the Abrahamic religions who brings evil and temptation, and is known as the deceiver who leads humanity astray. Some religious groups teach that he originated as an angel who fell out of favor with God, seducing humanity into the ways of sin, and who has power in the fallen world. In the Hebrew Bible and the New Testament, Satan is primarily an accuser and adversary, a decidedly malevolent entity, also called the devil, who possesses demonic qualities. In Theistic Satanism, Satan is considered a positive force and deity who is either worshipped or revered. In LaVeyan Satanism, Satan is regarded as holding virtuous characteristics.
        2017-04-21 23:30:16,092 - CLIClient - INFO - Speak: Deities depicted with horns or antlers are found in many different religions across the world.
        2017-04-21 23:30:16,616 - CLIClient - INFO - Speak: Azazel [ə-ˈzā-zəl], also spelled Azazael (Hebrew: עֲזָאזֵל, Azazel; Arabic: عزازيل , Azāzīl) appears in the Bible in association with the scapegoat rite. In some traditions of Judaism and Christianity, it is the name for a fallen angel. In Rabbinic Judaism it is not a name of an entity but rather means literally "for the complete removal", i.e., designating the goat to be cast out into the wilderness as opposed to the goat sacrificed "for YHWH".

if active LILACS curiosity skill leverages converse method to process all
utterances before any intent is triggered and learn about nodes

the ultimate way to learn about subjects is the LILACS teach skill, not yet
available, this will fill the node relationships at first much like a vocal
programming language, in the future for trusted users this can be made "passive"
 with machine learning on curiosity skill

# step 7 - Navigating Node Connections

the ConceptCrawler helper class will implement several strategies to navigate
node connections, the crawler will need a search depth (there could be infinite
nodes) and to choose what nodes to load/unload in memory as it crawls

Currently not much was done in this regard, the following POC crawlers navigate
childs and parents connections

- Drunk Crawler - choose next connection semi-randomly going to the strongest ones most of the times
- Explorer Crawler - check all connections and choose the best one

more crawlers will be added for all kinds of questions, strategies, connections and other functions

    - maintenance crawler will improve node connections, remove duplicate nodes,add shortcuts etc.
    - learning crawler will start at a subject and search everything it can about it and related nodes and save the populated info
    - anti-crawler could choose always the least likely connections
    - discoverer crawler could seek nodes with the least number of connections and populate those, because they represent a void in knowledge

A crawl-log would be a great representation for the thinking process , a "thought stream" of sorts


# Extra skills that leverage LILACS

LILACS rhymes skill was made to show usage of KnowledgeQuery from other skill

LILACS personal skill makes updates to the "self" user node "self X is Y"

LILACS users skill processes users "current_user_node Y is X"

this allows for things like

"who is my father"
"i don't know"
"my father is darth vader"
"your father is darth vader"
"what is your name"
"my name is jarbas"
"what is your favorite animal"
"i haven't decided what my favorite animal is"
"your favorite musical style is black metal"
"my favorite musical style is black metal"
"who is my father"
"your father is darth vader"
"what is your favorite musical style"
"my favorite musical style is black metal"

this works per unit, not per user, until user authentication is done expect it
to behave a little dumb, however using server client architecture every client
is considered a different user, same goes for facebook chat