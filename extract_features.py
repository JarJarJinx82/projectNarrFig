#!/usr/bin/python3

import argparse, time
import csv
import os
from inspect import getmembers, isfunction
from catma import Catma
from RFTagParser import RFTagger
import sys
import pickle
import statistics
import re
import nltk


"""Class for all the Blocks to contain the plain Text and
its annotations"""
class Block:
    """principal methods"""

    # constructor (runs every time an instance of this class is created)
    def __init__(self, listOfSegs, sprecher, title):
        self.segments = listOfSegs
        self.sprecher = sprecher
        self.text = self.extractText()
        self.properties = self.extractProps()
        self.tags = []
        self.title = title

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
        types = cat.getType(seg.attrib["ana"])
        isSprecher = False
        for elem in types:
            if elem["type"] == "Sprecherfigur":
                isSprecher = True

        #isSprecher = "Sprecherfigur" == cat.getType(seg.attrib["ana"])[1]["type"]
        if inBlock:
            if isFigurenrede:  # inside of block
                tmp.append(seg)
            else:  # end of Block
                #print(sprecher)
                temp_block = Block(tmp, sprecher, cat.title)
                listOfBlocks.append(temp_block)
                tmp = []
                sprecher = None
                inBlock = False
        else:
            if isFigurenrede:  # start of block
                inBlock = True
                tmp.append(seg)
        if isSprecher:
            sprecher = seg.text.strip().replace(".", "")


    # getting all the tags
    totalText = ""
    for figurenrede in listOfBlocks:
        totalText += figurenrede.text + "\nSTOPHERE\n"

    rf = RFTagger(totalText, ignore_segmentation=False)
    listOfTags = rf.listOfTags

    for block, tags in zip(listOfBlocks, listOfTags):
        block.tags = tags

    return listOfBlocks


"""Special functions, that can't be in other file"""


def li_contains_neper_local(text, tags):
    """True if someone from the Dramatis Personae is mentioned"""
    global anno
    for word, tag in tags:
        if tag["pos"] == "N" :
            if word.lower() in anno.dp:
                return True
    return False


def gb_contains_selfref(block):
    """True if speaker is mentioned."""
    sprechers = block.sprecher.split()
    for word, tag in block.tags:
        if word in sprechers:
            return True
        if tag["pos"] == "PRO" and not tag["attributes"] is None and tag["attributes"]["person"] == "1":
            return True
    else:
        return False


def bp_total_speech_proportion(block):
    """Redeanteil dieser Person generell"""
    varName = "speech_prp_" + block.sprecher
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


def bp_variance_from_mean_speech_proportion(block):
    """Redeanteil dieser Person - Mittelwert aller Redeanteile"""
    varName = "speech_prp_" + block.sprecher
    global ListOfPersonenreden
    total = len(ListOfPersonenreden)

    if varName not in globals():
        this = 0
        for rede in ListOfPersonenreden:
            if rede.sprecher == block.sprecher:
                this += 1
        prop = globals()[varName] = this / total
    else:
        prop = globals()[varName]

    varNameMean = "mean_speech_prop_" + block.title
    if varNameMean not in globals():
        sprecherCount = len(set([b.sprecher for b in ListOfPersonenreden]))
        mean = globals()[varNameMean] = (total / sprecherCount) / total
    else:
        mean = globals()[varNameMean]

    return prop - mean


def bp_first_appearance(block):
    """Der erste Auftritt der Figur (0=am Anfang, 1=am Ende)"""
    if block.sprecher == None:
        return None
    varName = "first_appearance_" + block.sprecher
    if varName not in globals():
        global ListOfPersonenreden
        total = len(ListOfPersonenreden) -1
        for i, rede in enumerate(ListOfPersonenreden):
            if rede.sprecher == block.sprecher:
                res = globals()[varName] = i/total
                return res
    else:
        return globals()[varName]


def bp_last_appearance(block):
    """Der letzte Auftritt der Figur (0=am Anfang, 1=am Ende)"""
    if block.sprecher == None:
        return None
    varName = "last_appearance_" + block.sprecher
    if varName not in globals():
        global ListOfPersonenreden
        total = len(ListOfPersonenreden) -1
        for i, rede in enumerate(reversed(ListOfPersonenreden)):
            if rede.sprecher == block.sprecher:
                res = globals()[varName] = (total-i) /total
                return res
    else:
        return globals()[varName]


def bp_variance_from_median_length_total(text, tags):
    """Varianz vom Median aller Längen, normalisiert an der Gesamtlänge"""
    global ListOfPersonenreden
    length = len(tags)
    all_lengths_var = "all_lengths_" + ListOfPersonenreden[0].title
    if all_lengths_var in globals():
        all_lengths = globals()[all_lengths_var]
    else:
        all_lengths = globals()[all_lengths_var] = [len(block.tags) for block in ListOfPersonenreden]

    total_length = sum(all_lengths)
    median_length = statistics.median(all_lengths)
    return (length-median_length)/total_length


def bp_variance_from_median_length_sd(text, tags):
    """Varianz vom Median aller Längen, normalisiert an der Standarddeviation"""
    global ListOfPersonenreden
    length = len(tags)
    all_lengths_var = "all_lengths_" + ListOfPersonenreden[0].title
    if all_lengths_var in globals():
        all_lengths = globals()[all_lengths_var]
    else:
        all_lengths = globals() [all_lengths_var] = [len(block.tags) for block in ListOfPersonenreden]

    sd = statistics.stdev(all_lengths)
    median_length = statistics.median(all_lengths)

    return (length-median_length)/sd


def bp_mean_speech_length_of_speaker(block):
    """Mittelwert der Längen aller Reden dieser Figur."""
    sp = block.sprecher
    varName = "mean_speech_length_"+sp
    if varName in globals():
        return globals()[varName]
    else:
        global ListOfPersonenreden
        all_lengths = [len(b.tags) for b in ListOfPersonenreden if b.sprecher == sp]
        return statistics.mean(all_lengths)



if __name__ == "__main__":
    """Preparation"""
    # imports all the extraction functions from named modules
    my_imports = ["features_m", "features_p"]
    func_list = [(bp_mean_speech_length_of_speaker, "block"), (bp_variance_from_median_length_total, None), (bp_variance_from_median_length_sd, None), (bp_last_appearance, "block"), (bp_first_appearance, "block"), (bp_variance_from_mean_speech_proportion, "block"), (bp_total_speech_proportion, "block"), (li_contains_neper_local, None), (gb_contains_selfref, "block")]
    for imp in my_imports:
        mod = __import__(imp)
        func_list += [(o[1], None) for o in getmembers(mod) if isfunction(o[1]) and o[0][0] != "_"]
    func_list.sort(key=lambda x: x[0].__name__)

    # different topic model settings
    topic_models = [("tm" + str(n), f"values for topics of topic model with {n} topics") for n in [5,10,15,20]]


    # command line ui, including parsing of wished features
    from operator import attrgetter
    parser = argparse.ArgumentParser(description="Extract features from Catma annotated Files")
    parser.add_argument("files", type=str, nargs="+", help="Filenames of the annotations.")
    parser.add_argument("-n", "--notablehead", action="store_const", const=True, default=False,
                        help="Exclude table head from csv.")
    parser.add_argument("-N", "--notext", action="store_const", const=True, default=False,
                        help="Exclude Text of Personenrede from csv.")
    megroup = parser.add_mutually_exclusive_group()
    megroup.add_argument("-j", "--just_prepare", action="store_const", const=True, default=False, help="Dont extract any feature, just take the text, devide it and get POS-Tags.")
    megroup.add_argument("-i", "--input_prepared", action="store_const", const=True, default=False, help="Dont use XML as input, but pre-prepared binary.")
    # create a cl argument entry for every feature
    group = parser.add_argument_group("features")
    group.add_argument("-a", "--all_features", action="store_const", const=True, default=False,
                       help="Extract all avaliable features.")
    for f in func_list:
        group.add_argument("--" + f[0].__name__, action="store_const", const=True, default=False, help=f[0].__doc__)

    for tm in topic_models:
        group.add_argument("--" + tm[0], action="store_const", const=True, default=False, help=tm[1])

    args = parser.parse_args()

    """extracting all the features"""

    if not args.just_prepare:  # preparing Tablehead if output of results is wished
        outData = []
        if not args.notablehead:
            tablehead = ["ID"]
            if not args.notext:
                tablehead.append("Personenrede")
            tablehead += [f[0].__name__ for f in func_list if (eval("args." + f[0].__name__) or args.all_features)]
            for tm in topic_models:
                    if eval("args." + tm[0]) or args.all_features:
                        tablehead += [tm[0] + "_" + str(i) for i in range(1, int(tm[0][2:]) + 1)]

            tablehead += ["Narrativer_Anteil", "falsifiziert"]
            outData.append(tablehead)
    else:  # prepare pickle output of prepared files
        ts = time.strftime("%Y%m%d-%H%M")
        pickle_file = f"d{len(args.files)}_{ts}.prep"

    if args.input_prepared:  # take the prepared tuples from the pickle as input
        with open(args.files[0], "rb") as inf:
            dramen = pickle.load(inf)

    else:  # take the named files as input
        dramen = args.files

    list_to_pickle = []
    # iterate over the different files
    for i, inf in enumerate(dramen):  # iterate over one of the to lists with all the dramen
        name = inf if not args.input_prepared else inf[0].title
        print(f"\nWorking on file #{i + 1}/{len(dramen)}\n{name}\n", file=sys.stderr)
        id = (i+1)*10000

        if not args.input_prepared:  # if iterating over files
            # get the annotation
            anno = Catma(inf)
            # get the Blocks from the annotation
            print("RFTagger working, this may need a moment.")
            ListOfPersonenreden = extract_blocks(anno)

        else:  # if iterating over prepared pickle stuff
            anno, ListOfPersonenreden = inf


        if args.just_prepare:  # save tagged and prepared blocks and annotation to pickle file
            list_to_pickle.append((anno, ListOfPersonenreden))
            #with open(pickle_file, "wb") as ouf:
            #    pickle.dump((anno, ListOfPersonenreden), ouf)


        else:  # extracing features, if not in just-prepare-mode
            # prepare data for topic modelling
            tm_path = "tm_" + anno.title
            if not os.path.exists(tm_path):
                os.makedirs(tm_path)

            raw_file = tm_path + "/utts_raw.txt"
            voca_file = tm_path + "/voca.txt"
            ind_file = tm_path + "/utts_ind.txt"


            with open(raw_file, "w") as of:
                for pr in ListOfPersonenreden:
                    # preprocess text for topic modelling (filter stopwords and symbols)
                    toks = nltk.word_tokenize(pr.text, language="german")
                    sw = nltk.corpus.stopwords.words("german")
                    no_symbols = r"\w+[-']?\w*"
                    filtered = [t.lower() for t in toks if t.lower() not in sw and re.match(no_symbols, t)]
                    of.write(" ".join(filtered) + "\n")

            # prepare the data with btm script
            os.system(f"python3 BTM/script/indexDocs.py {raw_file} {ind_file} {voca_file}")

            tm_results = {}
            for tm in topic_models:
                if eval("args." + tm[0]) or args.all_features:
                    output_path = tm_path + "/output_" + tm[0] + "/"
                    if not os.path.exists(output_path):
                        os.makedirs(output_path)

                    w = sum(1 for line in open(voca_file))
                    k = int(tm[0][2:])
                    # train topic model
                    os.system(f"BTM/src/btm est {k} {w} {50/k:.3f} 0.005 5 501 {ind_file} {output_path}")
                    # infer p(z|d) for each line
                    os.system(f"BTM/src/btm inf sum_b {k} {ind_file} {output_path}")

                    with open(f"{output_path}k{k}.pz_d") as res_inf:
                        tm_results[tm[0]] = [[float(e) for e in line[:k]] for line in csv.reader(res_inf, delimiter=" ")]


            # iterate over the annotated Blocks
            for j, personenrede in enumerate(ListOfPersonenreden):
                sys.stderr.write(f"\rProcessing personenrede #{j + 1}/{len(ListOfPersonenreden)}")

                retVal = [id+j]
                if not args.notext:
                    retVal.append('"' + personenrede.text.strip() + '"')
                # extract all the wished features
                for func in func_list:
                    if eval("args." + func[0].__name__) or args.all_features:
                        if func[1] == "block":
                            retVal.append(func[0](personenrede))
                        else:
                            retVal.append(func[0](personenrede.text, personenrede.tags))

                for tm in topic_models:
                    if eval("args." + tm[0]) or args.all_features:
                        retVal += tm_results[tm[0]][j]



                # complete the data and append it to the data collection
                retVal.append(personenrede.properties["narrative"])
                retVal.append(personenrede.properties["falsified"])
                outData.append(retVal)
            sys.stderr.flush()
            print("\n", file=sys.stderr)

    if not args.just_prepare:
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
    else:
        with open(pickle_file, "wb") as ouf:
            pickle.dump(list_to_pickle, ouf)
