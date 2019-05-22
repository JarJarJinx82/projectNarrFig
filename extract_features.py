#!/usr/bin/python3

import argparse, time
import csv
from inspect import getmembers, isfunction
from catma import Catma
from RFTagParser import RFTagger
import sys

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
            out += f"{k:15}{v}\n"
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
        # print(f"\nSegment #{i+1} of {len(segments)}", file=sys.stderr)
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
            if word.lower() in anno.dp:
                return True
    return False


def contains_selfref(block):
    """True if speaker is mentioned."""
    global anno
    if block.sprecher in anno.dp:
        return True
    else:
        return False


def total_speech_proportion(block):
    """Redeanteil dieser Person generell"""
    varName = "speech_prp-" + block.sprecher
    if varName not in globals():
        global ListOfPersonenreden
        total = len(ListOfPersonenreden)
        this = 0
        for rede in ListOfPersonenreden:
            if rede.sprecher == block.sprecher:
                this += 1
        res = this/total
        globals()[varName] = res
        return res

    else:
        return globals()[varName]


def variance_from_mean_speech_proportion(block):
    """Redeanteil dieser Person - Mittelwert aller Redeanteile"""
    varName = "speech_prp-" + block.sprecher
    global ListOfPersonenreden
    total = len(ListOfPersonenreden)

    if varName not in globals():
        this = 0
        for rede in ListOfPersonenreden:
            if rede.sprecher == block.sprecher:
                this += 1
        prop = globals()[varName] = this / total
    else:
        prop =  globals()[varName]

    varNameMean = "mean_speech_prop"
    if varNameMean not in globals():
        sprecherCount = sum(set([b.sprecher for b in ListOfPersonenreden]))
        mean = globals()[varNameMean] = total / sprecherCount
    else:
        mean = globals()[varNameMean]

    return prop - mean


def first_appearance(block):
    """Der erste Auftritt der Figur (0=als erstes, 1=als letztes)"""
    varName = "first_appearance-" + block.sprecher
    if varName not in globals():
        global ListOfPersonenreden
        total = len(ListOfPersonenreden) -1
        for i, rede in ListOfPersonenreden:
            if rede.sprecher == block.sprecher:
                res = globals()[varName] = i/total
                return res
    else:
        return globals()[varName]


def last_appearance(block):
    """Der letzte Auftritt der Figur (0=als erstes, 1=als letztes)"""
    varName = "last_appearance-" + block.sprecher
    if varName not in globals():
        global ListOfPersonenreden
        total = len(ListOfPersonenreden) -1
        for i, rede in reversed(ListOfPersonenreden):
            if rede.sprecher == block.sprecher:
                res = globals()[varName] = (total-i) /total
                return res
    else:
        return globals()[varName]


if __name__ == "__main__":
    """Preparation"""
    # imports all the extraction functions from named modules
    my_imports = ["features_m", "features_j", "features_p"]
    func_list = [(last_appearance, "block"), (first_appearance, "block"), (variance_from_mean_speech_proportion, "block"), (total_speech_proportion, "block"), (contains_neper_local, None), (contains_selfref, "block")]
    for imp in my_imports:
        mod = __import__(imp)
        func_list += [(o[1], None) for o in getmembers(mod) if isfunction(o[1])]
    func_list.sort(key=lambda x: x[0].__name__)

    # command line ui, including parsing of wished features
    from operator import attrgetter

    parser = argparse.ArgumentParser(description="Extract features from Catma annotated Files")
    parser.add_argument("files", type=str, nargs="+", help="Filenames of the annotations.")
    parser.add_argument("-n", "--notablehead", action="store_const", const=True, default=False,
                        help="Exclude table head from csv.")
    # create a cl argument entry for every feature
    group = parser.add_argument_group("features")
    group.add_argument("-a", "--all_features", action="store_const", const=True, default=False,
                       help="Extract all avaliable features.")
    for f in func_list:
        group.add_argument("--" + f[0].__name__, action="store_const", const=True, default=False, help=f[0].__doc__)
    args = parser.parse_args()

    """extracting all the features"""
    outData = []
    if not args.notablehead:
        outData.append(["Personenrede",
                        *[f[0].__name__ for f in func_list if (eval("args." + f[0].__name__) or args.all_features)]])
        if args.contains_selfref or args.all_features:
            outData[0].append("contains_selfref")
        outData[0] += ["Narrativer_Anteil", "falsifiziert"]

    # iterate over the different files
    for i, inf in enumerate(args.files):
        print(f"\nWorking on file #{i + 1}/{len(args.files)}\n{inf}\n", file=sys.stderr)
        # get the annotation
        anno = Catma(inf)
        # get the Blocks from the annotation
        print("RFTagger working, this may need a moment.")
        ListOfPersonenreden = extract_blocks(anno)

        # iterate over the annotated Blocks
        for j, personenrede in enumerate(ListOfPersonenreden):
            sys.stderr.write(f"\rProcessing personenrede #{j + 1}/{len(ListOfPersonenreden)}")
            retVal = ['"' + personenrede.text + '"']
            # extract all the wished features
            for func in func_list:
                if eval("args." + func[0].__name__) or args.all_features:
                    if func[1] == "block":
                        retVal.append(func[0](personenrede))
                    else:
                        retVal.append(func[0](personenrede.text, personenrede.tags))

            # complete the data and append it to the data collection
            retVal.append(personenrede.properties["narrative"])
            retVal.append(personenrede.properties["falsified"])
            outData.append(retVal)
        sys.stderr.flush()
        print("\n", file=sys.stderr)

    """outputting results to file"""
    print("Writing Results to file.", file=sys.stderr)
    # creating a timestamp
    ts = time.strftime("%Y%m%d-%H%M")
    ofName = f"features_{ts}.csv"
    # write the list of lists as a csv
    with open(ofName, "w") as of:
        writer = csv.writer(of)
        writer.writerows(outData)
    print("Done.", file=sys.stderr)
