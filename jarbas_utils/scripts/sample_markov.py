from mycroft import MYCROFT_ROOT_PATH

path = MYCROFT_ROOT_PATH + "/jarbas_utils"

import sys
sys.path.append(path)

from MarkovChains import MarkovChain

START_OF_SEQ = "~"
END_OF_SEQ = "[END]"

chain_name = "metal_5_w"
chain = MarkovChain()
chain_path = MYCROFT_ROOT_PATH + \
             "/jarbas_models/Markov_Chains/poetry_styles/"+chain_name+".json"
chain.load(chain_path)

print chain.generate_sequence()
