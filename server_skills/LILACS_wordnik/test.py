from wordnik import *

apiUrl = 'http://api.wordnik.com/v4'
apiKey = "api key"
client = swagger.ApiClient(apiKey, apiUrl)
wordApi = WordApi.WordApi(client)


def get_definitions(subject):
    definitions = wordApi.getDefinitions(subject,
                                              partOfSpeech='noun',
                                              sourceDictionaries='all',
                                              limit=5)
    defs = []
    try:
        for defi in definitions:
            defs.append(defi.text)
    except:
        pass
    return defs


def get_related_words(subject):
    res = wordApi.getRelatedWords(subject)
    words = {}
    try:
        for r in res:
            words.setdefault(r.relationshipType, r.words)
    except:
        pass
    return words

subject = "evil"
node_data = {}
node_data["relations"] = get_related_words(subject)
node_data["definitions"] = get_definitions(subject)

print node_data