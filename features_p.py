#!/usr/bin/python3

func_dict = {"example_p": "extract_example_p", "anteil_verb": "extract_anteil_verb"}

def extract_example_p(text, tags):
    return "Beispiel J"
    
    
def extract_anteil_verb(text, tags):
	verb_count = 0
	total = len(tags)
	for word in tags:
		if word.pos == "verb":
			verb_count += 1
	
	result = verb_count/ total
		
	return result 


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
	
		
