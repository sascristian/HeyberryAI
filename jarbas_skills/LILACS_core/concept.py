from jarbas_utils.jarbas_services import LILACSstorageService
from mycroft.util.log import getLogger

__authors__ = ["jarbas", "heinzschmidt"]


class ConceptNode():
    '''
    Node:
       name:
       type: "informational"   <- all discussed nodes so far are informational
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
    '''

    def __init__(self, name, data=None, parent_concepts=None,
        child_concepts=None, synonims=None, antonims=None, cousins = None,
        spawns = None, spawned_by = None, consumes = None, consumed_by = None,
        parts = None, part_off=None, type="info"):
        self.name = name
        self.type = type
        if data is None:
            data = {}
        self.data = data
        self.connections = {}
        if parent_concepts is not None:
            self.connections.setdefault("parents", parent_concepts)
        else:
            self.connections.setdefault("parents", {})
        if child_concepts is not None:
            self.connections.setdefault("childs", child_concepts)
        else:
            self.connections.setdefault("childs", {})
        if synonims is not None:
            self.connections.setdefault("synonims", synonims)
        else:
            self.connections.setdefault("synonims", {})
        if antonims is not None:
            self.connections.setdefault("antonims", antonims)
        else:
            self.connections.setdefault("antonims", {})
        if cousins is not None:
            self.connections.setdefault("cousins", cousins)
        else:
            self.connections.setdefault("cousins", {})
        if spawns is not None:
            self.connections.setdefault("spawns", spawns)
        else:
            self.connections.setdefault("spawns", {})
        if spawned_by is not None:
            self.connections.setdefault("spawned_by", spawned_by)
        else:
            self.connections.setdefault("spawned_by", {})
        if consumes is not None:
            self.connections.setdefault("consumes", consumes)
        else:
            self.connections.setdefault("consumes", {})
        if consumed_by is not None:
            self.connections.setdefault("consumed_by", consumed_by)
        else:
            self.connections.setdefault("consumed_by", {})
        if parts is not None:
            self.connections.setdefault("parts", parts)
        else:
            self.connections.setdefault("parts", {})
        if part_off is not None:
            self.connections.setdefault("part_off", part_off)
        else:
            self.connections.setdefault("part_off", {})

    def get_dict(self):
        node_dict = {"name": self.name, "type": self.type, "connections":
            self.connections, "data": self.data}
        return node_dict

    def load_from_dict(self, node_dict):
        self.connections.update(node_dict["connections"])
        self.data.update(node_dict.get("data", {}))

    def get_parents(self):
        return self.connections["parents"]

    def get_childs(self):
        return self.connections["childs"]

    def get_cousins(self):
        return self.connections["cousins"]

    def get_consumes(self):
        return self.connections["consumes"]

    def get_consumed_by(self):
        return self.connections["consumed_by"]

    def get_spawn(self):
        return self.connections["spawns"]

    def get_spawned_by(self):
        return self.connections["spawned_by"]

    def get_parts(self):
        return self.connections["parts"]

    def get_part_off(self):
        return self.connections["part_off"]

    def get_synonims(self):
        return self.connections["synonims"]

    def get_antonims(self):
        return self.connections["antonims"]

    def get_data(self):
        return self.data

    def add_synonim(self, synonim, strenght=5):
        if synonim not in self.connections["synonims"]:
            self.connections["synonims"][synonim] = strenght

    def add_antonim(self, antonim, strenght=5):
        if antonim not in self.connections["antonims"]:
            self.connections["antonims"][antonim] = strenght

    def add_data(self, key, data=None):
        if data is None:
            data = {}
        if key in self.data:
            self.data[key] = data
        else:
            self.data.setdefault(key, data)

    def add_parent(self, parent_name, gen = 1, update = True):

        # a node cannot be a parent  of itself
        if parent_name == self.name:
            return

        # a node cannot be a parent and a child (would it make sense in some corner case?)
        if parent_name in self.connections["childs"]:
            return

        if parent_name not in self.connections["parents"]:
            self.connections["parents"].setdefault(parent_name, gen)
        elif parent_name in self.connections["parents"] and update:
            self.connections["parents"][parent_name] = gen

    def add_child(self, child_name, gen=1, update = True):
        # a node cannot be a child of itself
        if child_name == self.name:
            return

        if child_name in self.connections["parents"]:
            return

        if child_name not in self.connections["childs"]:
            self.connections["childs"].setdefault(child_name, gen)
        elif child_name in self.connections["childs"] and update:
            self.connections["childs"][child_name] = gen

    def add_cousin(self, cousin, strenght=5):

        # dont add self or plural forms to related
        cousin_p = cousin+"s" #add an s
        cousin_s = cousin[0:len(cousin)] #remove last letter
        if cousin == self.name or cousin_p in self.name or cousin_s in self.name:
            return

        # dont add synonims
        for s in self.connections["synonims"].keys():

            if cousin == s or cousin_p in s+"s" or cousin_s in s+"s":
                return

        if cousin not in self.connections["cousins"]:
            self.connections["cousins"][cousin] = strenght

    def add_spawn(self, spawn, strenght=5):
        if spawn not in self.connections["spawns"]:
            self.connections["spawns"][spawn]= strenght

    def add_spawned_by(self, spawned_by, strenght=5):
        if spawned_by not in self.connections["spawned_by"]:
            self.connections["spawned_by"][spawned_by]= strenght

    def add_consumes(self, consumes, strenght=5):
        if consumes not in self.connections["consumes"]:
            self.connections["consumes"][consumes]= strenght

    def add_consumed_by(self, consumed_by, strenght=5):
        if consumed_by not in self.connections["consumed_by"]:
            self.connections["consumed_by"][consumed_by]= strenght

    def add_part(self, part, strenght=5):
        if part not in self.connections["parts"]:
            self.connections["parts"][part]= strenght

    def add_part_off(self, part_off, strenght=5):
        if part_off not in self.connections["part_off"]:
            self.connections["part_off"][part_off]= strenght

    def remove_synonim(self, synonim):
        if synonim is self.connections["synonims"]:
            self.connections["synonims"].pop(synonim)

    def remove_antonim(self, antonim):
        if antonim in self.connections["antonims"]:
            self.connections["antonims"].pop(antonim)

    def remove_cousin(self, cousin):
        if cousin in self.connections["cousins"]:
            self.connections["cousins"].pop(cousin)

    def remove_part(self, part):
        if part in self.connections["parts"]:
            self.connections["parts"].pop(part)

    def remove_part_off(self, part_off):
        if part_off in self.connections["part_off"]:
            self.connections["part_off"].pop(part_off)

    def remove_consumes(self, consumes):
        if consumes in self.connections["consumes"]:
           self.connections["consumes"].pop(consumes)

    def remove_consumed_by(self, consumed_by):
        if consumed_by in self.connections["consumed_by"]:
            self.connections["consumed_by"].pop(consumed_by)

    def remove_spawns(self, spawn):
        if spawn in self.connections["spawns"]:
            self.connections["spawns"].pop(spawn)

    def remove_spawned_by(self, spawned_by):
        if spawned_by in self.connections["spawned_by"]:
            self.connections["spawned_by"].pop(spawned_by)

    def remove_data(self, key):
        if key in self.data:
            self.data.pop(key)

    def remove_parent(self, parent_name):
        if parent_name in self.connections["parents"]:
            self.connections["parents"].pop(parent_name)

    def remove_child(self, child_name):
        if child_name in self.connections["childs"]:
            self.connections["childs"].pop(child_name)


class ConceptConnector():

    def __init__(self, concepts = None, emitter=None, user_concepts=None):
        if concepts is None:
            concepts = {}
        if user_concepts is None:
            user_concepts = {}
        self.concepts = concepts
        self.user_concepts = user_concepts
        self.logger = getLogger("ConceptConnector")
        self.emitter = emitter
        self.emitter.on("new_node", self.new_node)
        self.storage = LILACSstorageService(self.emitter)
        self.saved = []
        self.curiosity_save = False
        self.curiosity_load = False

    def new_node(self, message):
        node_name = message.data["name"]
        node_dict = message.data
        save = message.data.get("save", self.curiosity_save)
        load = message.data.get("load", self.curiosity_load)
        # create node signaled from outside
        if load:
            self.logger.info("Loading into memory externally signaled node from " + message.context.get("source", "unknown source"))
            self.create_concept(new_concept_name=node_name)
            if node_dict.get("type", "info") == "info":
                self.concepts[node_name].load_from_dict(node_dict)
            elif node_dict.get("type", "info") == "user":
                self.user_concepts[node_name].load_from_dict(node_dict)
            else:
                # TODO handle this
                return
            self.logger.info("Node loaded: " + node_name)
            if save:
                self.logger.info("Updating storage")
                self.save_concept(node_name)

    def get_concept_names(self, type="info"):
        concepts = []
        if type == "info":
            for name in self.concepts:
                concepts.append(name)
        elif type == "user":
            for name in self.user_concepts:
                concepts.append(name)
        return concepts

    def get_concepts(self):
        return self.concepts

    def add_concept(self, concept_name, concept, type="info"):
        if type == "info":
            if concept_name in self.concepts:
                self.logger.info("concept exists, merging fields")
                #  merge fields
                concept_dict = self.concepts[concept_name].get_dict()
                new_dict = concept.get_dict()
                for key in new_dict:
                    if key == "connections":
                        cons = new_dict[key]
                        for con in cons:
                            # check if there is any data for this connection
                            if cons[con] != {}:
                                # update each node individually
                                for node in cons[con]:
                                    concept_dict["connections"][con][node] = cons[con][node]
                    else:
                        concept_dict[key] = new_dict[key]
                self.concepts[concept_name].load_from_dict(concept_dict)
            else:
                self.logger.info("adding concept to connector")
                self.concepts.setdefault(concept_name, concept)
        elif type == "user":
            if concept_name in self.user_concepts:
                self.logger.info("concept exists, merging fields")
                #  merge fields
                concept_dict = self.user_concepts[concept_name].get_dict()
                new_dict = concept.get_dict()
                for key in new_dict:
                    if key == "connections":
                        cons = new_dict[key]
                        for con in cons:
                            # check if there is any data for this connection
                            if cons[con] != {}:
                                # update each node individually
                                for node in cons[con]:
                                    concept_dict["connections"][con][node] = cons[con][node]
                    else:
                        concept_dict[key] = new_dict[key]
                self.user_concepts[concept_name].load_from_dict(concept_dict)
            else:
                self.logger.info("adding concept to connector")
                self.user_concepts.setdefault(concept_name, concept)

    def remove_concept(self, concept_name):
        if concept_name in self.concepts:
            self.concepts.pop(concept_name)
        if concept_name in self.user_concepts:
            self.user_concepts.pop(concept_name)

    def get_data(self, concept_name):
        if concept_name in self.concepts:
            return self.concepts[concept_name].get_data()
        if concept_name in self.user_concepts:
            return self.user_concepts[concept_name].get_data()

    def add_data(self, concept_name, key, data=None):
        if concept_name in self.concepts:
            self.concepts[concept_name].add_data(key, data)
        if concept_name in self.user_concepts:
            self.user_concepts[concept_name].add_data(key, data)

    def get_childs(self, concept_name):
        if concept_name in self.concepts:
            c = self.concepts[concept_name].get_childs()
        else:
            c = {}
        return c

    def add_child(self, concept_name, child):
        if concept_name in self.concepts:
            self.concepts[concept_name].add_child(child)

    def get_parents(self, concept_name):
        if concept_name in self.concepts:
            p = self.concepts[concept_name].get_parents()
        else:
            p = {}
        return p

    def add_parent(self, concept_name, parent):
        if concept_name in self.concepts:
            self.concepts[concept_name].add_parent(parent)

    def get_antonims(self, concept_name):
        if concept_name in self.concepts:
            return self.concepts[concept_name].get_antonims()

    def add_antonim(self, concept_name, antonim):
        if concept_name in self.concepts:
            self.concepts[concept_name].add_antonim(antonim)

    def get_synonims(self, concept_name):
        if concept_name in self.concepts:
            return self.concepts[concept_name].get_synonims()

    def add_synonim(self, concept_name, synonim):
        if concept_name in self.concepts:
            self.concepts[concept_name].add_synonim(synonim)

    def get_cousins(self, concept_name):
        if concept_name in self.concepts:
            return self.concepts[concept_name].get_cousins()

    def add_cousin(self, concept_name, cousin):
        self.logger.info("adding cousin: " + cousin + " to concept: " + concept_name)
        if concept_name in self.concepts:
            self.concepts[concept_name].add_cousin(cousin)

    def get_parts(self, concept_name):
        if concept_name in self.concepts:
            return self.concepts[concept_name].get_parts()

    def add_part(self, concept_name, part):
        if concept_name in self.concepts:
            self.concepts[concept_name].add_part(part)

    def get_part_off(self, concept_name):
        if concept_name in self.concepts:
            return self.concepts[concept_name].get_part_off()

    def add_part_off(self, concept_name, part_off):
        if concept_name in self.concepts:
            self.concepts[concept_name].add_part_off(part_off)

    def get_spawn(self, concept_name):
        if concept_name in self.concepts:
          return self.concepts[concept_name].get_spawn()

    def add_spawn(self, concept_name, spawn):
        if concept_name in self.concepts:
            self.concepts[concept_name].add_spawn(spawn)

    def get_spawned_by(self, concept_name):
        if concept_name in self.concepts:
            return self.concepts[concept_name].get_spawned_by()

    def add_spawned_by(self, concept_name, spawned_by):
        if concept_name in self.concepts:
            self.concepts[concept_name].add_spawned_by(spawned_by)

    def get_consumes(self, concept_name):
        if concept_name in self.concepts:
            return self.concepts[concept_name].get_consumes()

    def add_consumes(self, concept_name, consumes):
        if concept_name in self.concepts:
            self.concepts[concept_name].add_consumes(consumes)

    def get_consumed_by(self, concept_name):
        if concept_name in self.concepts:
            return self.concepts[concept_name].get_consumed_by()

    def add_consumed_by(self, concept_name, consumed_by):
        if concept_name in self.concepts:
            self.concepts[concept_name].add_consumed_by(consumed_by)

    def create_concept(self, new_concept_name, data=None,
                           child_concepts=None, parent_concepts=None,
                       synonims=None,
                       antonims=None, type="info"):

        if data is None:
            data = {}
        if child_concepts is None:
            child_concepts = {}
        if parent_concepts is None:
            parent_concepts = {}
        if synonims is None:
            synonims = {}
        if antonims is None:
            antonims = {}
        # safe - checking
        self.logger.info("checking for invalid data")
        if new_concept_name in parent_concepts:
            parent_concepts.pop(new_concept_name)
        if new_concept_name in child_concepts:
            child_concepts.pop(new_concept_name)

        self.logger.info("creating concept node")
        # handle new concept
        concept = ConceptNode(name=new_concept_name, data=data, child_concepts=child_concepts, parent_concepts=parent_concepts,
                              synonims=synonims, antonims=antonims, type=type)

        if new_concept_name not in self.concepts:
            self.logger.info("Trying to load concept json " + new_concept_name)
            loaded_concept = self.storage.load(new_concept_name)
            if loaded_concept["sucess"]:
                self.logger.info("loading concept data " + new_concept_name)
                node_dict = loaded_concept["node"]
                concept.load_from_dict(node_dict)
                self.logger.info("loaded concept into memory")
        else:
            self.logger.info("updating concept")
        self.add_concept(new_concept_name, concept, type)
        # handle parent concepts
        for concept_name in parent_concepts:
            self.logger.info("checking if parent node exists: " + concept_name)
            gen = parent_concepts[concept_name]
            # create parent if it doesnt exist
            if concept_name not in self.concepts:
                self.logger.info("creating node: " + concept_name )
                concept = ConceptNode(concept_name)
                self.add_concept(concept_name, concept, type)
            # add child to parent
            self.logger.info("adding child: " + new_concept_name + " to parent: " + concept_name)
            if type == "info":
                self.concepts[concept_name].add_child(new_concept_name, gen=gen)
            elif type == "user":
                self.user_concepts[concept_name].add_child(new_concept_name,
                                                       gen=gen)

        # handle child concepts
        for concept_name in child_concepts:
            self.logger.info("checking if child node exists: " + concept_name)
            gen = child_concepts[concept_name]
            # create child if it doesnt exist
            if concept_name not in self.concepts:
                self.logger.info("creating node: " + concept_name)
                concept = ConceptNode(concept_name)
                self.add_concept(concept_name, concept, type)
                #self.save_concept(name=new_concept_name)
                #self.save_concept(name=newconcept_name)
            #add parent to child
            self.logger.info("adding parent: " + new_concept_name + " to child: " + concept_name)
            if type == "info":
                self.concepts[concept_name].add_parent(new_concept_name, gen=gen)
            elif type == "user":
                self.user_concepts[concept_name].add_parent(new_concept_name,
                                                        gen=gen)

        # handle synonims
        for concept_name in synonims:
            self.logger.info("checking if synonim exists: " + concept_name)
            # create synonim if it doesnt exist
            if concept_name not in self.concepts:
                self.logger.info("creating node: " + concept_name)
                concept = ConceptNode(concept_name)
                self.add_concept(concept_name, concept, type)
                #self.save_concept(name=new_concept_name)
            # add synonim to synonim
            self.logger.info("adding synonim: " + new_concept_name + " to concept: " + concept_name)
            if type == "info":
                self.concepts[concept_name].add_synonim(new_concept_name)
            elif type == "user":
                self.user_concepts[concept_name].add_synonim(new_concept_name)

        # handle antonims
        for concept_name in antonims:
            self.logger.info("checking if antonim exists: " + concept_name)
            # create synonim if it doesnt exist
            if concept_name not in self.concepts:
                self.logger.info("creating node: " + concept_name)
                concept = ConceptNode(concept_name)
                self.add_concept(concept_name, concept, type)
                #self.save_concept(name=new_concept_name)
            # add antonim to antonim
            self.logger.info("adding antonim: " + new_concept_name + " to concept: " + concept_name)
            if type == "info":
                self.concepts[concept_name].add_antonim(new_concept_name)
            elif type == "user":
                self.user_concepts[concept_name].add_antonim(new_concept_name)
        #self.save_concept(concept_name)

    def save_concept(self, name, type="info"):
        if name is None or name == "" or name == " ":
            self.logger.info("no node to save")
            return
        self.logger.info("saving: " + name)
        self.saved.append(name)
        if type == "info":
            if name not in self.concepts.keys():
                self.logger.error("Can not save this node because it doesnt exist in memory yet")
                return
            node_dict = self.concepts[name].get_dict()
        elif type == "user":
            if name not in self.user_concepts.keys():
                self.logger.error("Can not save this node because it doesnt exist in memory yet")
                return
            node_dict = self.user_concepts[name].get_dict()
        else:
            self.logger.error("invalid node type: " + str(type))
            return

        # TODO check hash before loading to see if file chnaged
        self.storage.save(node_dict)
        return

    def load_concept(self, name):

        if name is None or name == "" or name == " ":
            self.logger.info("no node to load " + name)
            return False

        loaded = self.storage.load(name)
        if not loaded.get("sucess", False):
            self.logger.info("no node to load " + name)
            return False
        node_dict = loaded["node"]
        type = node_dict.get("type", "info")
        self.logger.info("creating concept in memory: " + name)
        if type == "info":
            self.create_concept(name)
            self.concepts[name].load_from_dict(node_dict)
            self.logger.info("created info concept in memory: " + name)
        elif type == "user":
            self.create_concept(name, type="user")
            self.logger.info("created user concept in memory: " + name)
            self.user_concepts[name].load_from_dict(node_dict)

        else:
            self.logger.error("invalid node type: " + str(type))
            return False
        self.logger.info("loaded node_data: " + str(node_dict))
        return True

    def reset_connector(self):
        self.concepts = {}
        self.user_concepts = {}
        self.saved = []