#!/usr/bin/python3

import argparse, time
import csv
from inspect import getmembers, isfunction
from catma import Catma
from RFTagParser import RFTagger


"""Class for all the Blocks to contain the plain Text and
its annotations"""
class Block:

	"""principal methods"""
	# constructor (runs every time an instance of this class is created)
	def __init__(self, listOfSegs, sprecher):
		self.segments = listOfSegs
		self.sprecher = sprecher
		self.text = self.extractText()
		self.properties = self.extractProps()
		self.tags = []

		"""postagging here
		rf = RFTagger(self.text)
		self.tags = rf.tags"""


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
	sprecher = None
	# iterating over all catma-segments
	segments = cat.root.findall(f".//{cat.tei}seg")
	for i, seg in enumerate(segments):
		#print(f"\nSegment #{i+1} of {len(segments)}", file=sys.stderr)
		baseType = cat.getBaseType(seg.attrib["ana"])
		isFigurenrede = baseType == "Figurenrede"
		isSprecher = "Sprecherfigur" in cat.getType(seg.attrib["ana"])
		if inBlock:
			if isFigurenrede:  # inside of block
				tmp.append(seg)
			else:  # end of Block
				temp_block = Block(tmp, sprecher)
				listOfBlocks.append(temp_block)
				tmp = []
				sprecher = None
				inBlock = False
		else:
			if isFigurenrede:  # start of block
				inBlock = True
				tmp.append(seg)
			else:  # outside of block
				if isSprecher:
					sprecher = seg.text
				continue

	totalText = ""
	for figurenrede in listOfBlocks:
		totalText += figurenrede.text + "\nSTOPHERE\n"

	rf = RFTagger(totalText, ignore_segmentation=False)
	listOfTags = rf.listOfTags

	for block, tags in zip(listOfBlocks, listOfTags):
		block.tags = tags

	return listOfBlocks


"""Special functions, that can't be in other file"""
def contains_neper_local(text, tags):
	"""True if someone from the Dramatis Personae is mentioned"""
	global anno
	for word, tag in tags:
		if tag["pos"] == "N":
			if tag["attributes"]["type"] == "Name" and word.lower() in anno.dp:
				return True
	return False

def contains_selfref(block):
	"""True if speaker is mentioned."""
	global anno
	if block.sprecher in anno.dp:
		return True
	else:
		return False


if __name__ == "__main__":
	"""Preparation"""
	# imports all the extraction functions from named modules
	my_imports = ["features_m", "features_j", "features_p"]
	func_list = [contains_neper_local]
	for imp in my_imports:
		mod = __import__(imp)
		func_list += [o[1] for o in getmembers(mod) if isfunction(o[1])]

	# command line ui, including parsing of wished features
	parser = argparse.ArgumentParser(description="Extract features from Catma annotated Files")
	parser.add_argument("files", type=str, nargs="+", help="Filenames of the annotations.")
	parser.add_argument("-n", "--notablehead", action="store_const", const=True, default=False, help="Exclude table head from csv.")
	# create a cl argument entry for every feature
	group = parser.add_argument_group("features")
	group.add_argument("-a", "--all_features", action="store_const", const=True, default=False, help="Extract all avaliable features.")
	for f in func_list:
		group.add_argument("--"+f.__name__, action="store_const", const=True, default=False, help=f.__doc__)
	group.add_argument("--contains_selfref", action="store_const", const=True, default=False, help=contains_selfref.__doc__)
	args = parser.parse_args()

	"""extracting all the features"""
	outData = []
	if not args.notablehead:
		outData.append(["Personenrede", *[f.__name__ for f in func_list if (eval("args."+f.__name__) or args.all_features)]])
		if args.contains_selfref or args.all_features:
			outData[0].append("contains_selfref")
		outData[0] += ["Narrativer_Anteil", "falsifiziert"]

	# iterate over the different files
	for inf in args.files:
		# get the annotation
		anno = Catma(inf)
		# get the Blocks from the annotation
		ListOfPersonenreden = extract_blocks(anno)
		# iterate over the annotated Blocks
		for personenrede in ListOfPersonenreden:
			retVal = ['"'+personenrede.text+'"']
			# extract all the wished features
			for func in func_list:
				if eval("args." + func.__name__) or args.all_features:
					retVal.append(func(personenrede.text, personenrede.tags))
			if args.contains_selfref or args.all_features:
				retVal.append(contains_selfref(personenrede))
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
