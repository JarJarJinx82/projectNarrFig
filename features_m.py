#!/usr/bin/python3

func_dict = {"example_m": "extract_example_m"}

def extract_example_m(text, tags):
    return "Beispiel M"
    
    
if __name__ == "__main__":
	import pickle
	testfile = open("test.test", "rb")
	text = pickle.load(testfile)
	tags = pickle.load(testfile)
	testfile.close()
	res = []
	for k, v in func_dict:
		func = eval(v)
		res.append(func(text, tags))
	print(text)
	for elem in res:
		print(elem)
