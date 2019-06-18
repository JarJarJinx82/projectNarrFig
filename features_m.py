#!/usr/bin/python3
import re
import xml.etree.ElementTree as ET


chrono_list = ["also", "anfangs", "anno", "bald", "beizeiten", "bekanntlich", "bereits", "bisher", "bislang", "dadrauf",
               "dadurch", "daher", "damals", "danach", "damit", "dann", "darauf", "daraufhin", "davor", "dazwischen",
               "demnach", "demnächst",
               "dereinst", "derweil", "doch", "drauf", "eben", "ehemals", "einmal", "einst", "einstmals", "einstweilen",
               "erwartungsgemäß", "ferner", "folglich", "früher", "gerade", "gleich", "grad", "gleichwohl",
               "infolgedessen", "indes", "jedoch",
               "jüngst", "just", "künftig", "kürzlich", "längst", "letztens", "letztlich", "letzthin", "letztmals",
               "neulich", "schließlich", "seitdem", "seither", "sodann", "somit", "später", "späterhin", "vordem",
               "vorgestern", "gestern", "vorher",
               "vorhin", "vormals", "weiter", "weiters", "wodurch", "wogegen", "womit", "wonach", "zeither", "zuerst",
               "zugleich", "zuletzt", "überdies"]

narration_list = [r", (sagten?|meinten?) (er|sie)"]


# features

# unfertig, muss um die liste und deren inhalt ergänzt werden. was genau soll in dieser liste zu finden sein und WIE? > sagte er als 1 String oder anders?
def narration_keyphrases(text, tags):
    """compares each word with a wordlist of narration keyphrases, returns BOOL"""
    for exp in narration_list:
        if re.search(exp, text):
            return True
    return False


def chronologically_structured(text, tags):
    """compares each word with a wordlist of chronologically structuring terms, returns BOOL"""
    for word in tags:
        if word[0].lower() in chrono_list:
            return True
    return False


def past_proportion(text, tags):
    """"counts all verbs that are conjugated in past tense and divides them with all verbs, returns FLOAT"""
    allverbcount = 0
    pastverbcount = 0
    for word, tag in tags:
        if tag["pos"][0] == "V":
            allverbcount += 1
            if "tense" in tag["attributes"] and tag["attributes"]["tense"] == "Past":
                pastverbcount += 1

    return pastverbcount / allverbcount if allverbcount != 0 else -1


def contains_past(text, tags):
    """is searching for verbs conjugated in past tense, returns true if at least 1 verb stands in past tense (BOOL)"""
    for word, tag in tags:
        if tag["pos"][0] == "V" and "tense" in tag["attributes"] and tag["attributes"]["tense"] == "Past":
            return True
    return False


# futur2 wird momentan noch nicht gefunden, muss implementiert werden + durch was soll nun geteilt werden?
def future_proportion(text, tags):
    """counts all futur1+futur2 constructions and divides them with all verbs, returns FLOAT"""
    hilfsv_toggle = False
    allverbs = 0
    future_constructions = 0
    for word, tag in tags:
        if tag["pos"][0] == "V":
            if tag["pos"] == "VFIN":
                allverbs += 1
            elif hilfsv_toggle == True and tag["pos"] == "VINF":
                future_constructions += 1
                hilfsv_toggle = False
            elif hilfsv_toggle == True:
                hilfsv_toggle = False

            iswerden = "type" in tag["attributes"] and tag["attributes"]["type"] == "Aux" and word[0].lower() == "w"
            ispast = "tense" in tag["attributes"] and tag["attributes"]["tense"] == "Past"
            if iswerden and not ispast:
                hilfsv_toggle = True

    return future_constructions / allverbs if allverbs != 0 else -1


def contains_future(text, tags):
    """is searching for future constellations, returns True if at least 1 constellation was found (BOOL)"""
    hilfsv_toggle = False
    partizip2_toggle = False

    for word, tag in tags:
        try:  # give some output to help debugging
            tag["attributes"]
        except KeyError:
            print(word, tag)
        if hilfsv_toggle and not partizip2_toggle and tag["pos"] == "VINF":  # erfüllt: futur 1
            return True
        elif hilfsv_toggle and partizip2_toggle and tag["pos"] == "VINF" and "type" in tag[
            "attributes"] and tag["attributes"]["type"] == "Aux":  # erfüllt: futur 2
            return True
        elif hilfsv_toggle and not partizip2_toggle and tag["pos"] == "VPP" and "subtype" in tag[
            "attributes"] and tag["attributes"]["subtype"] == "Psp":
            partizip_toggle = True
        elif not tag["attributes"] is None and "type" in tag["attributes"] and tag["attributes"]["type"] == "Aux" and word[0].lower() == "w":
            hilfsv_toggle = True
        elif word == ".":
            hilfsv_toggle = False
            partizip2_toggle = False
    return False


def contains_non_present(text, tags):
    """combines contains_futur/past, returns BOOL"""
    return contains_future(text, tags) or contains_past(text, tags)


# umbenannt nach korr. engl. Bezeichnung
def subj_proportion(text, tags):
    """counts all verbs in subjunctive and divides them with all verbs, returns FLOAT"""
    allverbcount = 0
    subjverbcount = 0
    for word, tag in tags:
        if tag["pos"][0] == "V":
            allverbcount += 1
            if "mood" in tag["attributes"] and tag["attributes"]["mood"] == "Subj":
                subjverbcount += 1
    return subjverbcount / allverbcount if allverbcount != 0 else -1


def contains_thirdpers(text, tags):
    """is searching for verbs and pronouns in 3rd pers.sg., returns BOOL"""
    for word, tag in tags:
        if tag["pos"][0] == "V" and "person" in tag["attributes"] and tag["attributes"]["person"] == "3":
            return True
        elif tag["pos"] == "PRO" and "person" in tag["attributes"] and tag["attributes"][
            "person"] == "3":
            return True
    return False


def thirdpers_proportion(text, tags):
    """counts all verbs and pronouns in 3rd pers.sg. and divides them with all verbs and pronouns, returns FLOAT"""
    allverbpron = 0
    thirdpers = 0
    for word, tag in tags:
        if tag["pos"] == "PRO" or tag["pos"][0] == "V":
            allverbpron += 1

        verbisthird = tag["pos"][0] == "V" and "Person" in tag["attributes"] and tag["attributes"]["person"] == "3"
        proisthird = tag["pos"] == "PRO" and "person" in tag["attributes"] and tag["attributes"]["person"] == "3"
        if verbisthird or proisthird:
            thirdpers += 1
    return thirdpers / allverbpron if allverbpron != 0 else -1


def exclamation_proportion(text, tags):
    """counts all "!" and "?", divides them with all tokens, returns FLOAT"""
    allTokens = len(tags)
    punct = 0
    for word, tag in tags:
        if word == "!" or word == "?":
            punct += 1
    return punct / allTokens if allTokens != 0 else -1


def sym_proportion(text, tags):
    """is searching for all special characters and divides them with all tokens, returns FLOAT"""
    # spec_list = re.findall(r"[^a-zA-Z0-9]", text)
    symcount = 0
    for word, tag in tags:
        if tag["pos"] == "SYM":
            symcount += 1

    return symcount / len(tags) if len(tags) != 0 else -1


def adj_proportion(text, tags):
    """counts all adjectives and divides them with all tokens, returns FLOAT"""
    adj_counter = 0
    for word, tag in tags:
        if tag["pos"] == "ADJA" or tag["pos"] == "ADJD":
            adj_counter += 1
    return adj_counter / len(tags) if len(tags) != 0 else -1


def noun_proportion(text, tags):
    """counts all nouns (excluding proper names) and divides them with all tokens, returns FLOAT"""
    noun_counter = 0
    for word, tag in tags:
        if tag["pos"] == "N":
            noun_counter += 1
    return noun_counter / len(tags) if len(tags) != 0 else -1


def ne_proportion(text, tags):
    """counts all proper names and divides them with all tokens (all nouns could be worth a try), returns FLOAT"""
    ne_counter = 0
    for word, tag in tags:
        if tag["pos"] == "N":
            if "type" in tag["attributes"] and tag["attributes"]["type"] == "Name":
                ne_counter += 1
    return ne_counter / len(tags) if len(tags) != 0 else -1


def pron_proportion(text, tags):
    """counts all pronouns (maybe restrict them if it does not work properly) and divides them with all tokens, returns FLOAT"""
    pron_counter = 0
    for word, tag in tags:
        if tag["pos"] == "PRO":
            pron_counter += 1
    return pron_counter / len(tags) if len(tags) != 0 else -1


def contains_verbs_location(text, tags):
    """checks if location-related verb is contained, returns BOOL"""
    liste = _getlist("verbs_location", "./data/verben.Lokation.xml")
    for word, tag in tags:
        if word in liste:
            return True
    return False
    
def contains_adj_time(text, tags):
    """checks if time-related adjective is contained, returns BOOL"""
    liste = _getlist("adj_time", "./data/adj.Zeit.xml")
    for word, tag in tags:
        if word in liste:
            return True
    return False
    
def contains_noun_event(text, tags):
    """checks if event-related noun is contained, returns BOOL"""
    liste = _getlist("noun_event", "./data/nomen.Geschehen.xml")
    for word, tag in tags:
        if word in liste:
            return True
    return False
    
def contains_noun_group(text, tags):
    """checks if group-related noun is contained, returns BOOL"""
    liste = _getlist("noun_group", "./data/nomen.Gruppe.xml")
    for word, tag in tags:
        if word in liste:
            return True
    return False
    
def contains_noun_communication(text, tags):
    """checks if communication-related noun is contained, returns BOOL"""
    liste = _getlist("noun_communicaion", "./data/nomen.Kommunikation.xml")
    for word, tag in tags:
        if word in liste:
            return True
    return False
    
    

def contains_nouns_time(text, tags):
    """checks if time-related noun is contained, returns BOOL"""
    liste = _getlist("nouns_time", "./data/nomen.Zeit.xml")
    for word, tag in tags:
        if word in liste:
            return True
    return False

def contains_nouns_location(text, tags):
    """checks if location-related noun is contained, returns BOOL"""
    liste = _getlist("nouns_location", "./data/nomen.Ort.xml")
    for word, tag in tags:
        if word in liste:
            return True
    return False



def _getlist(varName, fileName):
    if varName in globals():
        foolist = globals()[varName]
    else:
        et = ET.parse(fileName)
        root = et.getroot()
        elist = root.findall(".//orthForm")
        foolist = [e.text for e in elist]
        globals()[varName] = foolist
    return foolist




if __name__ == "__main__":
    import pickle
    import inspect
    import sys

    with open("test.test", "rb") as testfile:
        tags = pickle.load(testfile)
        text = pickle.load(testfile)
    res = []
    functions = [obj for name, obj in inspect.getmembers(sys.modules[__name__]) if inspect.isfunction(obj)]
    for f in functions:
        res.append((f.__name__, f(text, tags)))
    for elem in res:
        print(elem[0], elem[1])
