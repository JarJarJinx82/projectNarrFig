import sys, os
import subprocess
import csv

class RFTagger:
	def __init__(self, text, ignore_segmentation=True):
		self.text = text
		self.tags = []
		self.listOfTags = []
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
			if not ignore_segmentation and row[0] == "STOPHERE":
				self.listOfTags.append(self.tags)
				self.tags = []
				continue

			# creating the dictionary and adding the easy ones
			tmpDict = {}
			if len(row) == 0:
				continue
			elif len(row) == 1:
				self.tags.append((row[0], {}))
			else:
				tmpDict["rftag"] = row[1]
				tmpDict["lemma"] = row[2]
				tmpTags = row[1].split(".")
				tmpDict["pos"] = pos = tmpTags[0]
				# getting the more complicated ones with the helper functinos
				helperfunc = eval("self.pos_" + pos)  # dirty trick to call function
				try:
					attribs = helperfunc(tmpTags[1:])
				except IndexError:
					if len(tmpTags[1:]) == 0:
						attribs = None
					else:
						attribs = {}
						for i, elem in enumerate(tmpTags[1:]):
							attribs[i] = elem
					print("Warning: POS-tag incomplete: " + row[0] + "\n\t-> " + tmpDict["rftag"] + "\n\t->", attribs, file=sys.stderr)
				tmpDict["attributes"] = attribs
				self.tags.append((row[0], tmpDict))

	# helper methods for pos-tag-parsing
	def pos_kng(self, tags):
		if len(tags) == 2:
			retDict = {"case" : "*",
					   "number" : tags[0],
					   "gender" : tags[1]}
		elif len(tags) == 0:
			print("Warning: POS-tag incomplete." + "\n\t->", tags, file=sys.stderr)
			retDict = None
		elif len(tags) == 1:
			print("Warning: POS-tag incomplete." + "\n\t->", tags, file=sys.stderr)
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
		if len(tags) == 0:
			return {"case": "*"}
		else:
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
		retDict = {"type": tags[0]}
		if len(tags) == 2:
			retDict["subtype"] = tags[1]
		return retDict

	def pos_VPP(self, tags):
		retDict = {"type": tags[0],
				   "subtype": tags[1]}
		return retDict
