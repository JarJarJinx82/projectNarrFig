import xml.etree.ElementTree as ET
from nltk import word_tokenize
import re



"""Class for parsing and handling Catma"""
class Catma:
    # makes namespacing easier
    tei = "{http://www.tei-c.org/ns/1.0}"
    xml = "{http://www.w3.org/XML/1998/namespace}"

    # constructor getting all kinds of useful stuff from catma data
    def __init__(self, input_file):
        self.tree = ET.parse(input_file)
        self.root = self.tree.getroot()
        self.typeDict = self.create_typeDict()
        self.idDict = self.create_idDict()
        self.dp = self.getDP()

        """ postagging here
        self.text = self.extract_text()
        rf = RFTagger(self.text)
        self.total_tags = rf.tags

    def extract_text(self):
        pass"""

    # parse Dramatis Personae
    def getDP(self):
        text = self.root.find(f".//{self.tei}body/{self.tei}ab").text
        personen = re.search("Personen Personen. (.*) 1.", text)
        personen = word_tokenize(personen.group(1))
        return personen

    # function to make types easily lookupable
    def create_typeDict(self):
        typeDict = {}
        # iterate over Declarations
        for fsDecl in self.root.findall(f".//{self.tei}encodingDesc/*/{self.tei}fsDecl"):
            # create a subdict with the type and the baseType
            tempDict = {}
            tempDict["type"] = fsDecl.find(f"{self.tei}fsDescr").text
            if "baseTypes" in fsDecl.attrib:
                tmp = fsDecl.attrib["baseTypes"]
            else:
                tmp = None
            tempDict["baseType"] = tmp
            typeDict[fsDecl.attrib["type"]] = tempDict
        return typeDict

    # function to make ids easily lookupable
    def create_idDict(self):
        idDict = {}
        # iterate over all id -> typeID nodes
        for fs in self.root.findall(f".//{self.tei}text/{self.tei}fs"):
            # creating dict entry that connects id(ana) and typeID
            idDict[fs.attrib[f"{self.xml}id"]] = fs.attrib["type"]
        return idDict

    # function to tell the type of a segment based on its id
    def getType(self, ana, includeID=False):
        anas = ana.split(" ")
        anas = [elem[1:] for elem in anas]
        types = []
        for a in anas:
            typeID = self.idDict[a]
            if includeID:
                types.append((self.typeDict[typeID], typeID))
            else:
                types.append(self.typeDict[typeID])
        return types

    # get the base type (Figurenrede or not)
    def getBaseType(self, ana, all=False):
        types = self.getType(ana, includeID=True)
        if all:
            baseType = []
            for ty in types:
                baseType.append(ty[0])
                baseType += self.getBaseTypeHelper(ty[1], all)
        else:
            baseType = self.getBaseTypeHelper(types[0][1])
        return baseType

    # recursive method to crawl to basic baseType
    def getBaseTypeHelper(self, typeID, all=False):
        cond = self.typeDict[typeID]["baseType"] is None
        if cond:
            return self.typeDict[typeID]["type"]
        else:
            if all:
                return [self.typeDict[typeID]["type"], *self.getBaseTypeHelper(self.typeDict[typeID]["baseType"], all)]
            else:
                return self.getBaseTypeHelper(self.typeDict[typeID]["baseType"])