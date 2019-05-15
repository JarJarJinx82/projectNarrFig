#!/usr/bin/python3

import argparse, time
import csv
import xml.etree.ElementTree as ET
import sys, os
import subprocess
from inspect import getmembers, isfunction

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

	# function to make types easily lookupable
	def create_typeDict(self):
		typeDict = {}
		# iterate over Declarations
		for fsDecl in self.root.findall(f".//{self.tei}encodingDesc/*/{self.tei}fsDecl"):
			# create a subdict with the type and the baseType
			tempDict = {}
			tempDict["type"] =fsDecl.find(f"{self.tei}fsDescr").text
			if "baseTypes" in fsDecl.attrib:
				tmp = fsDecl.attrib["baseTypes"]
			else:
				tmp = None
			tempDict["baseType"] = tmp
			typeDict[fsDecl.attrib["type"]] = tempDict
		return typeDict

	#function to make ids easily lookupable
	def create_idDict(self):
		idDict = {}
		#iterate over all id -> typeID nodes
		for fs in self.root.findall(f".//{self.tei}text/{self.tei}fs"):
			#creating dict entry that connects id(ana) and typeID
			#creating dict entry that connects id(ana) and typeID
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

class RFTagger:
	def __init__(self, text):
		self.text = text
		self.tags = {}
		# use RFTagger to pos-tag the text
		os.chdir("RFTagger")
		with open("tmp.txt", "w") as tmp:
			tmp.write(text)
		self.rftags = subprocess.check_output("bash cmd/rftagger-german tmp.txt", shell=True)
		os.remove("tmp.txt")
		os.chdir("..")
		# read the results and parse them into a dict
		rows = self.rftags.decode().split("\n")
		for row in csv.reader(rows, delimiter="\t"):
			if len(row) == 0:
				continue
			# creating the dictionary and adding the easy ones
			tmpDict = {}
			tmpDict["lemma"] = row[2]
			tmpTags = row[1].split(".")
			tmpDict["pos"] = pos = tmpTags[0]
			# getting the more complicated ones with the helper functinos
			helperfunc = eval("self.pos_" + pos)  # dirty trick to call function
			try:
				attribs = helperfunc(tmpTags[1:])
			except IndexError:
				print("Warning: POS-tag incomplete: " + row[0], file=sys.stderr)
				if len(tmpTags[1:]) == 0:
					attribs = None
				else:
					attribs = {}
					for i, elem in enumerate(tmpTags[1:]):
						attribs[i] = elem
			tmpDict["attributes"] = attribs
			self.tags[row[0]] = tmpDict

	# helper methods for pos-tag-parsing
	def pos_kng(self, tags):
		if len(tags) == 0:
			print("Warning: POS-tag incomplete.", file=sys.stderr)
			retDict = None
		elif len(tags) < 3:
			print("Warning: POS-tag incomplete.", file=sys.stderr)
			retDict = {}
			for i, elem in enumerate(tags):
				retDict[i] = elem
		else:
			retDict = {"case": tags[0],
					   "number": tags[1],
					   "gender": tags[2]}
		return retDict

	def pos_ADJA(self, tags):
		retDict = {"degree": tags[0]}
		retDict.update(self.pos_kng(tags[1:]))
		return retDict

	def pos_ADJD(self, tags):
		return {"degree": tags[0]}

	def pos_ADV(self, _):
		return None

	def pos_APPO(self, tags):
		return {"case": tags[0]}

	def pos_APPR(self, tags):
		return {"case": tags[0]}

	def pos_APPRART(self, tags):
		return self.pos_kng(tags)

	def pos_APZR(self, _):
		return None

	def pos_ART(self, tags):
		retDict = {"type": tags[0]}
		retDict.update(self.pos_kng(tags[1:]))
		return retDict

	def pos_CARD(self, _):
		return None

	def pos_CONJ(self, tags):
		return {"type": tags[0]}

	def pos_FM(self, _):
		return None

	def pos_ITJ(self, _):
		return None

	def pos_N(self, tags):
		retDict = {"type": tags[1]}
		retDict.update(self.pos_kng(tags[1:]))
		return retDict

	def pos_PART(self, tags):
		return {"type": tags[0]}

	def pos_PRO(self, tags):
		retDict = {"type": tags[0],
				   "usage": tags[1],
				   "person": tags[2]}
		retDict.update(self.pos_kng(tags[3:]))
		return retDict

	def pos_PROADV(self, tags):
		return {"type": tags[0]}

	def pos_SYM(self, tags):
		retDict = {"type": tags[0], "subtype": tags[1]}
		return retDict

	def pos_TRUNC(self, tags):
		return {"pos": tags[0]}

	def pos_VFIN(self, tags):
		retDict = {"type": tags[0],
				   "person": tags[1],
				   "number": tags[2],
				   "tense": tags[3],
				   "mood": tags[4]}
		return retDict

	def pos_VIMP(self, tags):
		retDict = {"type": tags[0],
				   "person": tags[1],
				   "number": tags[2]}
		return retDict

	def pos_VINF(self, tags):
		retDict = {"type": tags[0],
				   "subtype": tags[1]}
		return retDict

	def pos_VPP(self, tags):
		retDict = {"type": tags[0],
				   "subtype": tags[1]}
		return retDict


"""Class for all the Blocks to contain the plain Text and
its annotations"""
class Block:

	"""principal methods"""
	# constructor (runs every time an instance of this class is created)
	def __init__(self, listOfSegs):
		self.segments = listOfSegs
		self.text = self.extractText()
		self.properties = self.extractProps()
		rf = RFTagger(self.text)
		self.tags = rf.tags


	# get the plain Text content of the part
	def extractText(self) -> str:
		retstr = ""
		for seg in self.segments:
			retstr += seg.text
		return retstr
	
	# extract properties of the text -> narration, falsification, ...
	def extractProps(self) -> dict:
		global anno
		containsNarr = False
		isFalsified = False
		for seg in self.segments:
			types = anno.getBaseType(seg.attrib["ana"], all=True)

			if "Narrative_Figurenrede" in types:
				containsNarr = True
			if "Falsifizierte_Figurenrede" in types:
				isFalsified = True
		props = {"narrative": containsNarr, "falsified": isFalsified}
		return props
	
	
	"""helper methods and deluxe stuff"""

	# functions to make the object printable
	def __repr__(self):
		out = self.text + "\n"
		for k, v in self.properties.items():
			k += ":"
			out+= f"{k:15}{v}\n"
		return out

	def __str__(self):
		return self.__repr__()




"""Eats catma annotations as ElementTree and spits out a list
of Block Objects containing the Text and its annotations"""
def extract_blocks(cat) -> list:
	listOfBlocks = []
	inBlock = False  # remembers if right now in Block while iterating
	tmp = []  # list of Segments that belong to same Block
	# iterating over all catma-segments
	segments = cat.root.findall(f".//{cat.tei}seg")
	for i, seg in enumerate(segments):
		print(f"\nSegment #{i+1} of {len(segments)}", file=sys.stderr)
		baseType = cat.getBaseType(seg.attrib["ana"])
		isFigurenrede = baseType == "Figurenrede"
		if inBlock:
			if isFigurenrede:  # inside of block
				tmp.append(seg)
			else:  # end of Block
				temp_block = Block(tmp)
				listOfBlocks.append(temp_block)
				tmp = []
		else:
			if isFigurenrede:  # start of block
				inBlock = True
				tmp.append(seg)
			else:  # outside of block
				continue

	return listOfBlocks


if __name__ == "__main__":
	"""Preparation"""
	# imports all the extraction functions from named modules
	my_imports = ["features_m", "features_j", "features_p"]
	func_list = []
	for imp in my_imports:
		mod = __import__(imp)
		func_list += [o[1] for o in getmembers(mod) if isfunction(o[1])]

	# command line ui, including parsing of wished features
	parser = argparse.ArgumentParser(description="Extract features from Catma annotated Files")
	parser.add_argument("files", type=str, nargs="+", help="Filenames of the annotations.")
	parser.add_argument("--notablehead", action="store_const", const=True, default=False, help="Exclude table head from csv.")
	# create a cl argument entry for every feature
	for f in func_list:
		parser.add_argument("--"+f.__name__, action="store_const", const=True, default=False, help=f.__doc__)
	args = parser.parse_args()

	"""extracting all the features"""
	outData = []
	if not args.notablehead:
		outData.append(["Personenrede", *list(features.keys()), "Narrativer_Anteil", "falsifiziert"])

	# iterate over the different files
	for inf in args.files:
		# get the annotation
		anno = Catma(inf)
		# get the Blocks from the annotation
		ListOfPersonenreden = extract_blocks(anno)
		# iterate over the annotated Blocks
		for personenrede in ListOfPersonenreden:
			retVal = ["'"+personenrede.text+"'"]
			# extract all the wished features
			for func in func_list:
				if eval("args." + func.__name__):
					retVal.append(func(personenrede.text, personenrede.tags))
			# complete the data and append it to the data collection
			retVal.append(personenrede.properties["narrative"])
			retVal.append(personenrede.properties["falsified"])
			outData.append(retVal)


	"""outputting results to file"""
	# creating a timestamp
	ts = time.strftime("%Y%m%d-%H%M")
	ofName = f"features_{ts}.csv"
	# write the list of lists as a csv
	with open(ofName, "w") as of:
		writer = csv.writer(of)
		writer.writerows(outData)