#!/usr/bin/python3


chrono_list = ["also","anfangs","anno","bald","beizeiten","bekanntlich","bereits","bisher","bislang","dadrauf","dadurch","daher","damals","danach","damit","dann","darauf","daraufhin","davor","dazwischen","demnach","demnächst",
               "dereinst","derweil","doch","drauf","eben","ehemals","einmal","einst","einstmals","einstweilen","erwartungsgemäß","ferner","folglich","früher","gerade","gleich","grad","gleichwohl","infolgedessen","indes","jedoch",
               "jüngst","just","künftig","kürzlich","längst","letztens","letztlich","letzthin","letztmals","neulich","schließlich","seitdem","seither","sodann","somit","später","späterhin","vordem","vorgestern","gestern","vorher",
               "vorhin","vormals","weiter","weiters","wodurch","wogegen","womit","wonach","zeither","zuerst","zugleich","zuletzt","überdies"]


#features


def chronologically_structured(text, tags):
        for word in tags.keys():
                for element in chrono_list:
                        if word == element: 
                               return True
        return False


def past_proportion(text, tags, counts=None):
    if counts is None:
        counts = dict(all=0, pres=0)

    for k,v in tags.items():

        if isinstance(v, dict):
            past_proportion(text,tags,counts)
        elif k == "tense":
            counts["all"] += 1
            if v == "Pres":
                counts["pres"] += 1
        print(counts)

    return counts["pres"] / counts["all"]











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
	print(text)
	print(tags.items())
	for elem in res:
		print(elem[0], elem[1])
