#!/usr/bin/python3
import re

chrono_list = ["also","anfangs","anno","bald","beizeiten","bekanntlich","bereits","bisher","bislang","dadrauf","dadurch","daher","damals","danach","damit","dann","darauf","daraufhin","davor","dazwischen","demnach","demnächst",
               "dereinst","derweil","doch","drauf","eben","ehemals","einmal","einst","einstmals","einstweilen","erwartungsgemäß","ferner","folglich","früher","gerade","gleich","grad","gleichwohl","infolgedessen","indes","jedoch",
               "jüngst","just","künftig","kürzlich","längst","letztens","letztlich","letzthin","letztmals","neulich","schließlich","seitdem","seither","sodann","somit","später","späterhin","vordem","vorgestern","gestern","vorher",
               "vorhin","vormals","weiter","weiters","wodurch","wogegen","womit","wonach","zeither","zuerst","zugleich","zuletzt","überdies"]

narration_list = ["sagte"]


#features


#unfertig, muss um die liste und deren inhalt ergänzt werden. was genau soll in dieser liste zu finden sein und WIE? > sagte er als 1 String oder anders?
def narration_keyphrases(text, tags):
        """compares each word with a wordlist of narration keyphrases, returns BOOL"""
        for word in tags:
                if word[0].lower() in chrono_list: 
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
    allverbcount=0
    pastverbcount=0
    for word, tag in tags:
                if tag["pos"][0] == "V":
                        allverbcount += 1
                        if "tense" in tag["attributes"] and tag["attributes"]["tense"] == "Past":
                                pastverbcount += 1
                        
    return pastverbcount/allverbcount

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
    futur_constructions=0
    for word, tag in tags:
                if tag["pos"][0] == "V":
                        allverbs += 1
                        if hilfsv_toggle == True and tag["pos"] == "VINF": 
                                future_constructions += 1
                                hilfsv_toggle = False
                        elif hilfsv_toggle == True: 
                                hilfsv_toggle = False
                        if "type" in tag["attributes"] and tag["attributes"]["type"] == "Aux" and word[0].lower() == "w":
                                hilfsv_toggle = True
                            
    return futur_constructions/allverbs                        

def contains_future(text, tags):
    """is searching for future constellations, returns True if at least 1 constellation was found (BOOL)"""
    hilfsv_toggle = False
    partizip2_toggle = False

    for word, tag in tags:
                if hilfsv_toggle == True and  partizip2_toggle == False and tag["pos"] == "VINF": #erfüllt: futur 1
                        return True
                elif hilfsv_toggle == True and partizip2_toggle == True and tag["pos"] == "VINF" and "type" in tag["attributes"] and tag["attributes"]["type"] == "Aux": #erfüllt: futur 2
                        return True
                elif hilfsv_toggle == True and partizip2_toggle == False and tag["pos"] == "VPP" and "subtype" in tag["attributes"] and tag["attributes"]["subtype"] == "Psp":
                        partizip_toggle = True
                elif "type" in tag["attributes"] and tag["attributes"]["type"] == "Aux" and word[0].lower() == "w":
                        hilfsv_toggle = True
                else:
                        hilfsv_toggle = False
                        partizip2_toggle = False
    return False
def contains_non_present(text, tags):
    """combines contains_futur/past, returns BOOL"""
    hilfsv_toggle = False
    partizip2_toggle = False

    for word, tag in tags:
                if hilfsv_toggle == True and  partizip2_toggle == False and tag["pos"] == "VINF": #erfüllt: futur 1
                        return True
                elif hilfsv_toggle == True and partizip2_toggle == True and tag["pos"] == "VINF" and "type" in tag["attributes"] and tag["attributes"]["type"] == "Aux": #erfüllt: futur 2
                        return True
                elif hilfsv_toggle == True and partizip2_toggle == False and tag["pos"] == "VPP" and "subtype" in tag["attributes"] and tag["attributes"]["subtype"] == "Psp":
                        partizip_toggle = True
                elif "type" in tag["attributes"] and tag["attributes"]["type"] == "Aux" and word[0].lower() == "w":
                        hilfsv_toggle = True
                else:
                        hilfsv_toggle = False
                        partizip2_toggle = False
                if tag["pos"][0] == "V" and "tense" in tag["attributes"] and tag["attributes"]["tense"] == "Past":
                        return True
    return False         

#umbenannt nach korr. engl. Bezeichnung
def subj_proportion(text, tags):
    """counts all verbs in subjunctive and divides them with all verbs, returns FLOAT"""
    allverbcount=0
    subjverbcount=0
    for word, tag in tags:
                if tag["pos"][0] == "V":
                        allverbcount += 1
                        if "mood" in tag["attributes"] and tag["attributes"]["mood"] == "Subj":
                                subjverbcount += 1        
    return subjverbcount/allverbcount

def contains_thirdpers(text, tags):
    """is searching for verbs and pronouns in 3rd pers.sg., returns BOOL"""
    for word, tag in tags:
                if tag["pos"][0] == "V" and "person" in tag["attributes"] and tag["attributes"]["person"] == "3" and "number" in tag["attributes"] and tag["attributes"]["number"] == "Sg":
                        return True
                elif tag["pos"] == "PRO" and "person" in tag["attributes"] and tag["attributes"]["person"] == "3" and "number" in tag["attributes"] and tag["attributes"]["number"] == "Sg":
                        return True
    return False

def thirdpers_proportion(text, tags):
	"""counts all verbs and pronouns in 3rd pers.sg. and divides them with all verbs and pronouns, returns FLOAT""" 
	allverbpron = 0
	thirdpers = 0
	for word, tag in tags:
		if tag["pos"] == "PRO" or tag["pos"][0] == "V":
			allverbpron += 1
		if (tag["pos"][0] == "V" and "person" in tag["attributes"] and tag["attributes"]["person"] == "3" and "number" in tag["attributes"] and tag["attributes"]["number"] == "Sg") or (tag["pos"] == "PRO" and "person" in tag["attributes"] and tag["attributes"]["person"] == "3" and "number" in tag["attributes"] and tag["attributes"]["number"] == "Sg"):
			thirdpers += 1
	return thirdpers/allverbpron
		

def sent_proportion(text, tags):
	"""counts all "!" and "?", divides them with all tokens, returns FLOAT"""
	allTokens = len(tags)
	punct = 0
	for word, tag in tags:
		if word == "!" or word == "?":
			punct += 1
	return punct/allTokens

def sym_proportion(text, tags):
	"""is searching for all special characters and divides them with all tokens, returns FLOAT"""
	spec_list = re.findall(r"[^a-zA-Z0-9 ]", text)
	
	return len(spec_list)/len(tags)
	
def adj_proportion(text, tags):
	"""counts all adjectives and divides them with all tokens, returns FLOAT"""
	adj_counter = 0
	for word, tag in tags:
		if tag["pos"] == "ADJA" or tag["pos"] == "ADJD":
			adj_counter += 1
	return adj_counter/len(tags)
	
def noun_proportion(text, tags):
	"""counts all nouns (excluding proper names) and divides them with all tokens, returns FLOAT"""
	noun_counter = 0
	for word, tag in tags:
		if tag["pos"] == "N":
			if "type" in tag["attributes"] and tag["attributes"]["type"] == "Reg":
				noun_counter += 1
	return noun_counter/len(tags)
	
def ne_proportion(text, tags):
	"""counts all proper names and divides them with all tokens (all nouns could be worth a try), returns FLOAT"""
	ne_counter = 0
	for word, tag in tags:
		if tag["pos"] == "N":
			if "type" in tag["attributes"] and tag["attributes"]["type"] == "Name":
				ne_counter += 1
	return ne_counter/len(tags)
	
def pron_proportion(text, tags):
	"""counts all pronouns (maybe restrict them if it does not work properly) and divides them with all tokens, returns FLOAT"""
	pron_counter = 0
	for word, tag in tags:
		if tag["pos"] == "PRO":
			ne_counter += 1
	return ne_counter/len(tags)
	



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
