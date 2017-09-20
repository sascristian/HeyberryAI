import wolframalpha
import re

api = ""

client = wolframalpha.Client(api)

PIDS = ['Value', 'NotableFacts:PeopleData', 'BasicInformation:PeopleData',
        'Definition', 'DecimalApproximation']


def get_result(res):
    try:
        return next(res.results).text
    except:
        result = None
        try:
            for pid in PIDS:
                result = __find_pod_id(res.pods, pid)
                if result:
                    result = result[:5]
                    break
            if not result:
                result = __find_num(res.pods, '200')
            return result
        except:
            return result


def __find_pod_id(pods, pod_id):
    for pod in pods:
        if pod_id in pod.id:
            return pod.text
    return None


def __find_num(pods, pod_num):
    for pod in pods:
        if pod.node.attrib['position'] == pod_num:
            return pod.text
    return None


def _find_did_you_mean(res):
    value = []
    root = res.tree.find('didyoumeans')
    if root is not None:
        for result in root:
            value.append(result.text)
    return value


def process_wolfram_string(text):
    # Remove extra whitespace
    text = re.sub(r" \s+", r" ", text)

    # Convert | symbols to commas
    text = re.sub(r" \| ", r", ", text)

    # Convert newlines to commas
    text = re.sub(r"\n", r", ", text)

    # Convert !s to factorial
    text = re.sub(r"!", r",factorial", text)

    regex = "(1,|1\.) (?P<Definition>.*) (2,|2\.) (.*)"
    list_regex = re.compile(regex)

    match = list_regex.match(text)
    if match:
        text = match.group('Definition')

    return text


def ask_wolfram(query, res=None):
    response = ["no answer"]
    others = []
    if res is None:
        res = client.query(query)
    result = get_result(res)
    if result is None:
        others = _find_did_you_mean(res)
    if result:
        input_interpretation = __find_pod_id(res.pods, 'Input')
        verb = "is"

        if "|" in result:  # Assuming "|" indicates a list of items
            verb = ":"

        result = process_wolfram_string(result)
        input_interpretation = \
            process_wolfram_string(input_interpretation)
        response = "%s %s %s" % (input_interpretation, verb, result)
        i = response.find("?")
        if i != -1:
            response = response[i + 1:].replace("is ", "").replace("(",
                                                                   "\n").replace(
                ")", " ")
        response = [response]

    else:
        if len(others) > 0:
            response.remove("no answer")
            for other in others:
                response.append(ask_wolfram(other))
    return response


def get_connections(res):
    synonims = {}
    parents = {}
    for unit in res:
        if "assumption" in unit.keys():
            # gets parents from wolfram disambiguation
            assumption = unit["assumption"]
            type = assumption["@type"]
            if type == "Clash":
                node = assumption["@word"]
                if "value" in assumption:
                    if node not in parents:
                        parents[node] = {}
                    for ass in assumption["value"]:
                        parents[node][ass["@name"]] = 5
        if "infos" in unit.keys():
            info = unit["infos"]["info"]
            if "unit" in info:
                # gets units and constants "km" : "kilometers"
                units = info["units"]["unit"]
                for unit in units:
                    synonims[unit["@short"]] = unit["@long"]
            elif "link" in info:
                url = info["link"]["@url"]
            else:
                print info
    return synonims, parents


def get_node(res, center_node="", target_node=None):
    node_dict = {}
    node_data = {}
    atr = None
    for unit in res:
        try:
            categorie = unit["@title"]
            if categorie not in node_data.keys():
                node_data[categorie] = []
            data = unit["subpod"]
            if isinstance(data, dict):
                info = data["plaintext"]
                if categorie == "Input interpretation":
                    name, atr = info.split("|")
                    if "\n" in name:
                        center_node, target_node = name.split("\n")

                if categorie == "Interpretation":
                    atr = info
                elif info:
                    if "\n" in info:
                        fields = []
                        for field in [field for field in info.split("\n")
                                      if "(script capital r)" not in field]:
                            if "|" in field:
                                key, value = field.split("|")[:2]
                                info = {key: value}
                                fields.append(info)
                            else:
                                fields.append(field)
                        node_data[categorie].extend(fields)
                    elif "|" in info:
                        values = info.split("|")
                        node_data[categorie].extend(values)
                    else:
                        node_data[categorie].append(info)

            elif isinstance(data, list):
                for field in data:
                    if isinstance(field, dict):
                        info = field["plaintext"].replace("|", "").replace(
                            ":", "")
                        if "\n" in info:
                            key, value = info.split("\n")
                            if "|" in value:
                                value = value.split("|")
                            info = {key: value}
                        elif "|" in info:
                            info = info.split("|")
                        node_data[categorie].append(info)

            if node_data[categorie] == []:
                node_data.pop(categorie)
        except:
            if "infos" in unit.keys():
                info = unit["infos"]["info"]
                if "link" in info:
                    url = info["link"]["@url"]
                    node_data["url"] = url
        if atr is None and target_node is not None:
            atr = target_node
            target_node = None
        if atr is not None:
            if target_node is not None:
                node_dict["data"] = {atr: {target_node: node_data}}
            else:
                node_dict["data"] = {atr: node_data}
        else:
            node_dict["data"] = node_data
    node_dict["name"] = center_node
    return node_dict


query = "how much wood can a woodchuck chuck"
res = client.query(query)

node = get_node(res, "light", "speed")
syns, parents = get_connections(res)
print ask_wolfram(query, res)
print "syns", syns
print "parents", parents
print "node", node
