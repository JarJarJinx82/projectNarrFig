#!/usr/bin/python3


def example_m(text, tags):
	"""Beispielfunktion von Michi"""
	return "Beispiel M"










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