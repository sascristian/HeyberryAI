# LILACS

LILACS is a learning and comprehension subsystem

The job of lilacs is to understand concepts and answer questions about them

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

        Question: think about the meaning of life
        {'Query2': 'life', 'Query1': 'the meaning', 'QuestionTargetWord': 'about ', 'QuestionWord': 'think', 'Query': 'the meaning life', 'QuestionTargetWord2': 'of '}

        Question: what is the speed of light
        {'Query2': 'light', 'Query1': ' is the speed', 'QuestionTargetWord': 'of', 'QuestionWord': 'what', 'Query': ' is the speed light'}

        Question: who are you
        {'QuestionWord': 'who', 'Query': 'you', 'QuestionVerb': 'are'}

        Question: who am i
        {'QuestionWord': 'who', 'Query': 'i', 'QuestionVerb': 'am'}

        Question: what is my favorite song
        {'QuestionWord': 'what', 'Query': 'my favorite song', 'QuestionVerb': 'is'}

        Question: what is your favorite book
        {'QuestionWord': 'what', 'Query': 'your favorite book', 'QuestionVerb': 'is'}

        Question: who is my cousin
        {'QuestionWord': 'who', 'Query': 'my cousin', 'QuestionVerb': 'is'}

        Question: what is war
        {'QuestionWord': 'what', 'Query': 'war', 'QuestionVerb': 'is'}

        Question: how to kill animals ( a cow ) and make meat
        {'QuestionWord': 'how', 'Query': 'kill animals ( cow ) and make meat', 'QuestionVerb': 'to'}

        Question: what is a living being
        {'QuestionWord': 'what', 'Query': 'living being', 'QuestionVerb': 'is'}

        Question: why are humans living beings
        {'QuestionWord': 'why', 'Query': 'humans living beings', 'QuestionVerb': 'are'}

        Question: give examples of animals
        {'QuestionWord': 'examples', 'Query': 'animals', 'QuestionVerb': 'of'}

        Question: how do i make money with bitcoin
        {'QuestionWord': 'how', 'Query': 'i make money with bitcoin', 'QuestionVerb': 'do'}

        Question: how can i win bitcoin
        {'QuestionWord': 'how', 'Query': 'i win bitcoin', 'QuestionVerb': 'can'}

        Question: are the prophets with me
        {'Query2': ' me', 'Query1': 'the prophets', 'QuestionTargetWord': 'with', 'QuestionWord': 'are', 'Query': 'the prophets  me'}

        Question: is your god evil
        {'QuestionWord': 'is', 'Query': 'god evil', 'QuestionPerson': 'your'}


After this LILACS uses dbpedia spotlight to extract concepts from the sentence

If no concept is tagged from dbpedia lilacs will use the query from regex
instead with some extra processing to handle "noise"

The last step is to normalize the text, for this the question parser lenmmatize
words and remove plurals, some extra processing is done for
changing concepts like "me" and "your" to "current_user" and "self"

Some examples of final question parser output:

### TODO ###

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

Each concept in LILACS is stored as a "concept node" with the following anatomy

    Node:
       name: <- the concept this node is about
       type: "informational"   <- general info, or about a person
       Connections:
           synonims: []  <- is the same as
           antonims: [] <- can never be related to
           parents: {name : distance }  <- is an instance of
           childs: {name : distance } <- can have the following instances
           cousins: [] <- somewhat related subjects
           spawns: []  <- what comes from this?
           spawned_by: [] <- where does this come from?
           consumes: [] <- what does this need/spend ?
           consumed_by: []  <- what consumes this?
           parts : [ ] <- what smaller nodes can this be divided into?
           part_off: [ ] <- what can be made out of this?
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

### TODO examples

# step 5 - Node storage

Currently all nodes are stored as .json object, this is temporary and eventually
 several backends should be available to use

 The LILACS storage skill will handle this and is responsible to listen for save
  and load node messages, a good analogy would be retrieving long term memory
  and passing it to short term memory

# step 6 - Filling nodes

Nodes are auto populated with some info from the knowledge sources, one way to
trigger this is with questions of the kind "think about" or "talk about"

if active LILACS curiosity skill leverages converse method to process all
utterances before any intent is triggered and learn about nodes

the ultimate way to learn about subjects is the LILACS teach skill, not yet
available, this will fill the node relationships at first much like a vocal
programming language, in the future for trusted users this can be made "passive"
 with machine learning on curiosity skill

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

### TODO add picture ###