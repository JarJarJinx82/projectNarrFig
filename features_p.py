#!/usr/bin/python3


def example_p(text, tags):
	return "Beispiel P"


def anteil_verb(text, tags):
	verb_count = 0
	total = len(tags)
	for word, tag in tags.items():
		if tag["pos"][0] == "V":
			verb_count += 1
	
	result = verb_count/ total
		
	return result 


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
	for elem in res:
		print(elem[0], elem[1])
