#!/usr/bin/python3


chrono_list = ["also","anfangs","anno","bald","beizeiten","bekanntlich","bereits","bisher","bislang","dadrauf","dadurch","daher","damals","danach","damit","dann","darauf","daraufhin","davor","dazwischen","demnach","demnächst",
               "dereinst","derweil","doch","drauf","eben","ehemals","einmal","einst","einstmals","einstweilen","erwartungsgemäß","ferner","folglich","früher","gerade","gleich","grad","gleichwohl","infolgedessen","indes","jedoch",
               "jüngst","just","künftig","kürzlich","längst","letztens","letztlich","letzthin","letztmals","neulich","schließlich","seitdem","seither","sodann","somit","später","späterhin","vordem","vorgestern","gestern","vorher",
               "vorhin","vormals","weiter","weiters","wodurch","wogegen","womit","wonach","zeither","zuerst","zugleich","zuletzt","überdies"]


#basic functions
def tokenizeFile(readyToTokenize):
        fixedExpressions = ['Mr.', 'etc.', 'Mrs.', 'Ms.', 'Dr.']
        returnList = []
        currentWord = ''
        for character in readyToTokenize:
            if currentWord+character in fixedExpressions:
                returnList.append(currentWord+character)
                currentWord = ''
            elif character == '.' or character == ',' or character == '!' or character == '?':
                returnList.append(currentWord)
                returnList.append(character)
                currentWord = ''
            elif character.isspace():
                if len(currentWord) > 0:
                    returnList.append(currentWord)
                    currentWord = ''
            else:
                currentWord += character
        return returnList

        

#features
def chronologically_structured(text, tags):
      
	
	










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
