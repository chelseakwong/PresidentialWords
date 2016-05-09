import json,os,heapq, string, random
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
from textblob import TextBlob
from moviepy.editor import *
from num2words import num2words

searchKey=['believe']
# for i in range(100):
# 	searchKey.append(num2words(i))
# for j in range(10):
# 	searchKey.append(num2words(10**j))
# searchKey = ['you','must','should']

searchPhrase = "God"

def joinAll():
	allClips = []
	for i in os.listdir(os.getcwd()+"/mostfreq2sorted/"):
		vidName = 'mostfreq2sorted/'+i
		if ".DS" in vidName:
			continue
		allClips.append(VideoFileClip(vidName))
	
	final_clip = concatenate_videoclips(allClips,method="compose")
	final_clip.write_videofile("final_2.mp4",fps=24, temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac") 				
	
	# allVids = []
	# allWords = getMostCommonWords()
	# # startAt = allWords.index("never")
	# # allWords = allWords[startAt:]
	# print allWords
	# count = 1
	# it = 0
	# for i in os.listdir(os.getcwd()+"/freq2/"):
	# 	vidName = 'freq2/'+i
	# 	allVids.append(vidName)
	# # sort by frequency
	# for word in allWords:
	# 	for vid in allVids:
	# 		if word in vid:
	# 			if (count % 10 == 0):
	# 				try:
	# 					final_clip = concatenate_videoclips(allClips,method="compose")
	# 					final_clip.write_videofile("freq_"+str(it)+".mp4",fps=24, temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")
	# 				except:
	# 					break
	# 				count = 1
	# 				it += 1
	# 				allClips = []
	# 				allClips.append(VideoFileClip(vid))
	# 			else:
	# 				allClips.append(VideoFileClip(vid))
	# 				count += 1

	# if (len(allClips)>0):
	# 	final_clip = concatenate_videoclips(allClips,method="compose")
	# 	final_clip.write_videofile("freq_"+str(it)+".mp4",fps=24, temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")
	# return




def txtToVid():
	txtFile = "trump.txt"
	f = open(txtFile).read()
	blob = TextBlob(f)
	goodJsons = []
	mapping = {}
	part = 0
	for i in os.listdir(os.getcwd()+"/speeches/"):
		i = i.split('.txt',1)[0]
		txtFileName = 'speeches/'+i+".txt"
		mp3FileName = 'audio/'+i+".mp3"
		alignName = 'alignedJsons/'+i+".json"
		vidName = 'videos/'+i+'.mp4'
		if not(os.path.isfile(txtFileName) and os.path.isfile(mp3FileName) and 
				os.path.isfile(alignName) and os.path.isfile(vidName)):
			continue
		else: 
			goodJsons.append(alignName)
			mapping[alignName] = vidName

	for sent in blob.sentences:
		totalFail = 0
		prevIndex = 0
		# print sent
		sentList = sent.words
		allClips = []
		allVids = []
		print sent
		for word in sentList:
			tryIndex = 0
			fail = 0
			random.shuffle(goodJsons)
			currJson = goodJsons[tryIndex]
			with open(currJson) as data_file:
				data = json.load(data_file)
			entryItem = getWordJson(word,data['words'])
			
			while (entryItem == 0):
				tryIndex += 1
				# fail to find this word
				if (tryIndex >= len(goodJsons)):
					fail = 1
					break
				# try next one
				currJson = goodJsons[tryIndex]
				with open(currJson) as data_file:
					data = json.load(data_file)
				entryItem = getWordJson(word,data['words'])
			
			if (fail != 1):
				# vidname, {'word':hi, begin, end, etc}
				item = {'vid':mapping[currJson], 'entry':entryItem}
				allClips.append(item)
			
			else:
				totalFail += 1
				if (totalFail >= len(sentList)/2):
					print ("!!!! ABANDON SHIP!!!!!")
					break

		# now have this sentencewith sounds
		for seg in allClips:
			filename = seg['vid']
			begin = seg['entry']['start'] -0.1
			end = seg['entry']['end'] +0.1
			clip = VideoFileClip(filename).subclip(begin,end).speedx(0.9)
			# adjClip = clip.fx(vfx.speedx,final_duration=10)
			allVids.append(clip)

		if (len(allVids) > 0):
			final_clip = concatenate_videoclips(allVids,method="compose")
			final_clip.write_videofile("trump"+str(part)+".mp4",fps=24, temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")
			part += 1
	return


def getWordJson(word,data):
	random.shuffle(data)
	for i in xrange(len(data)):
		if (data[i]['case']=="success") and (data[i]['word'].lower() == word.lower()):
			return data[i]
	return 0


# get 30 most common words, subtract the common english words
# from speeches	
def getMostCommonWords():
	allFiles = []
	for i in os.listdir(os.getcwd()+"/speeches/"):
		vidName = 'videos/'+i[:-4]+".mp4"
		print vidName
		if (os.path.isfile(vidName)):
			allFiles.append(i)
	countDict = filesToDict(allFiles)
	# print len(countDict)
	heap = [(-value, key) for key,value in countDict.items()]
	largest = heapq.nsmallest(25, heap)
	largest = [(key, -value) for value, key in largest]
	longList = [val for (val,key) in largest]
	print largest
	return longList


# return {'word':count,....} for all words in all speeches
def filesToDict(filenames):
	# get most common english words and exclude from search
	commonwords = []
	maxNum = 500
	numToList = 0
	with open("commonwords.txt",'r') as f:
		for line in f:
			for word in line.split():
				if (numToList >= maxNum):
					break
				commonwords.append(word)
				numToList += 1

	dict = {}
	# go through each file's words and add to dict
	for i in xrange(len(filenames)):
		filename = "speeches/"+filenames[i]
		# go through each word update/init entry
		if not(os.path.isfile(filename)):
			continue
		with open(filename,'r') as f:
			for line in f:
				# print line
				for word in line.split():
					# all words in lower case
					smallWord = word.lower()
					# only strings with letters
					if not word.isalpha():
						continue
					# only uncommon words
					if (smallWord in commonwords):
						continue
					# udpate entry
					if (smallWord in dict):
						num = dict[smallWord]
						num += 1;
						dict[smallWord] = num
					# create entry
					else:
						dict[smallWord] = 1
	return dict

# not used here, but will save dictionary to json
def saveDictToFile(dict):
	jsonFileName = 'wordcount.json'
	result = json.dumps(dict)
	with open(jsonFileName,'w') as f:
		json.dump(result,f,indent=4)
	return

def makeLongVideo():
	listWords = getMostCommonWords()
	# return
	for word in listWords:
		print "======"+str(listWords.index(word))+word+"========="
		makeVideo(word)
	return

def joinSameWords():
	fileDict = {}
	allFiles = []
	for i in os.listdir(os.getcwd()+"/mostfreq4/"):
		found = False
		temp = i[:-4]
		exclude = set(['1','2','3','4','5','6','0'])
		realName = ''.join(ch for ch in temp if ch not in exclude)
		for key in fileDict:
			if (key == realName):
				a = fileDict[key]
				a.append(i)
				found=True
		if not found:
			tempArr = [i]
			fileDict[realName] = tempArr

	mostCommon = getMostCommonWords() #list of most common words
	# print fileDict
	print TextClip.list('font')
	count = 1
	for word in mostCommon:
		txt = "%d. %s" % (count,word)
		txt_clip = TextClip(txt, fontsize=30, bg_color='black', color='white').set_pos('center').set_duration(2)
		# txt_clip = txt_clip.set_pos('center').set_duration(4)
		print word
		listVids = [txt_clip]
		for vidName in fileDict[str(word)]:
			actVidname = "mostfreq4/"+vidName
			listVids.append(VideoFileClip(actVidname))
		# print listVids
		final_clip = (concatenate_videoclips(listVids,method="compose").fx(vfx.fadein,duration=1)
																		.fx(vfx.fadeout,duration=0.5))
		newVidName = "mostfreq4combo/"+word + "_full.mp4"
		final_clip.write_videofile(newVidName,fps=24, temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")
		count += 1
	return


def makeMasterVideo():
	allSpeeches = [ 'First Inaugural Address, Franklin Roosevelt',
		'Pearl Harbor Address to the Nation, Franklin Roosevelt',
		'Atoms for Peace, Dwight Eisenhower',
		'Ich bin ein Berliner, John F Kennedy',
		'Greater Houston Ministerial Association Address, John F Kennedy',
		'Inaugural Address, John F Kennedy',
		'Let Us Continue, Lyndon B Johnson',
		'On Vietnam and Not Seeking Reelection, Lyndon B Johnson',
		'Checkers, Richard M Nixon',
		'Resignation Speech, Richard M Nixon',
		'The Great Silent Majority, Richard M Nixon',		
		'A Crisis of Confidence, Jimmy Carter',
		'Remarks at the Brandenburg Gate, Ronald Reagan',
		'40th Anniversary of D-Day Address, Ronald Reagan',
		'A Time for Choosing, Ronald Reagan',
		'The Challenger Disaster Address, Ronald Reagan',
		'2008 DNC Speech, William Jefferson Clinton',					
		'2004 DNC Keynote Address, Barack Obama' ]
	
	allVids = []

	# for i in os.listdir(os.getcwd()+"/mostfreq3combo/"):
		# allVids.append(VideoFileClip("mostfreq3combo/"+i))
	mostCommon = getMostCommonWords() #list of most common words
	for word in mostCommon:
		filename = "mostfreq4combo/"+word+"_full.mp4"
		allVids.insert(0,VideoFileClip(filename))

	titleTxt = TextClip("25 most common words\n from presidential speeches", fontsize=30, bg_color='black', color='white').set_pos('center').set_duration(5)
	videoTxt = TextClip("\n".join(allSpeeches), fontsize=12, bg_color='black',color='white').set_pos('center').set_duration(15)
	allVids.insert(0,videoTxt)
	allVids.insert(0,titleTxt)

	final_clip = concatenate_videoclips(allVids,method="compose").fx(vfx.fadein,duration=1)
	newVidName = "25most_presidential_words.mp4"
	final_clip.write_videofile(newVidName,fps=24, temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")
	return



def getStringOnly(name):
	temp = name[:-4]
	exclude = set(['1','2','3','4','5','0'])
	realName = ''.join(ch for ch in temp if ch not in exclude)
	return realName

def makeVideo(word):
	# either getwordtiming or getsentencestiming
	timings = getWordTiming([word])
	# timings = getSentencesTiming(searchKey)
	# timings = getPhraseTiming(searchPhrase)
	finalFilename = "mostfreq4/"+"".join(word)
	allVids = []
	random.shuffle(timings)
	# timings = timings[50:]
	count = 1
	its = 0

	for seg in timings:

		if ((count % 15) == 0):
			# clear all and make a video now
			final_clip = concatenate_videoclips(allVids,method="compose")
			final_clip.write_videofile(finalFilename+str(its)+".mp4",fps=24, temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")
			count = 1
			its += 1
			allVids = []
		if ((its>3)):
			return
		else:
			# for sentences
			# 
			# 
			# filename = seg['vid']
			# begin = seg['allWords'][-1]['start']
			# end = seg['allWords'][0]['end']

			# for words
			# 
			# 
			filename = seg['vid']
			begin = seg['entry']['start'] 
			end = seg['entry']['end'] 
			# print "begin time: "+str(begin)
			# print "end time: "+str(end)
			clip = VideoFileClip(filename).subclip(begin,end)
			allVids.append(clip)
			count += 1
		# continue
	if (len(allVids)>0):
		final_clip = concatenate_videoclips(allVids,method="compose")
		final_clip.write_videofile(finalFilename+str(its)+".mp4",fps=24, temp_audiofile="temp-audio.m4a", remove_temp=True, codec="libx264", audio_codec="aac")
	return

# Get words to when sentences containing these words are said
def getSentencesTiming(words):
	allClips = []
	found = 0
	actualFiles = 0
	for i in os.listdir(os.getcwd()+"/speeches/"):
		i = i.split('.txt',1)[0]
		txtFileName = 'speeches/'+i+".txt"
		mp3FileName = 'audio/'+i+".mp3"
		alignName = 'alignedJsons/'+i+".json"
		vidName = 'videos/'+i+'.mp4'
		if not(os.path.isfile(alignName) and os.path.isfile(vidName)):
			continue
		else:
			matches = wordsToSentence(words,txtFileName)
			actualFiles += 1
			if (len(matches) > 0):
				times = getTimes(matches,alignName)
				if (len(times) == 0):
					continue
				for entry in times:
					print "******************* result found *******************"		
					# entry is sentence, times[entry] is array is words said
					if (len(entry.split()) > 20): 
						continue
					print txtFileName
					print "sentence: "+entry
					currEntry = times[entry]
					timeBegin = currEntry[-1]
					timeEnd = currEntry[0]
					found += 1

					print "begin: "+ timeBegin['word'] +" time: "+str(timeBegin['start'])
					print "end: "+ timeEnd['word'] +" time: "+str(timeEnd['end'])
					newDict = {'vid':vidName, 'sentence':entry, 'allWords': currEntry}
					allClips.append(newDict)

	print "found: "+str(found)
	return allClips

# return a dict where each entry is segment in clips when phrase is said
def getPhraseTiming(phrase):
	listOfPhrases = phrase.split()
	allClips = []
	found = 0
	for i in os.listdir(os.getcwd()+"/speeches/"):
		i = i.split('.txt',1)[0]
		txtFileName = 'speeches/'+i+".txt"
		mp3FileName = 'audio/'+i+".mp3"
		alignName = 'alignedJsons/'+i+".json"
		vidName = 'videos/'+i+'.mp4'
		if not(os.path.isfile(txtFileName) and os.path.isfile(mp3FileName) and 
				os.path.isfile(alignName) and os.path.isfile(vidName)):
			continue
		else:
			# matches and shortMatches are arrays of strings to be found in files
			matches = phraseToSentence(listOfPhrases,txtFileName)
			shortMatches = shortenPhrases(matches, phrase)
			times = getTimes(shortMatches,alignName)
			# print times
			if (len(times) == 0):
				continue
			for entry in times:
				found += 1
				print "******************* result found *******************"		
				# entry is sentence, times[entry] is array is words said
				print txtFileName
				print "sentence: "+entry
				currEntry = times[entry]
				timeBegin = currEntry[-1]
				timeEnd = currEntry[0]

				print "begin: "+ timeBegin['word'] +" time: "+str(timeBegin['start'])
				print "end: "+ timeEnd['word'] +" time: "+str(timeEnd['end'])
				newDict = {'vid':vidName, 'allWords':currEntry}
				allClips.append(newDict)
	print "found: "+str(found)
	return allClips

# cut sentences containing phrase to only when phrase is said to end of sent
def shortenPhrases(matches,phrase):
	# max 8 words come after when phrase is said
	phraseList = phrase.split()
	results = []
	maxLength = 15 + len(phraseList)
	for sent in matches:
		sentList = sent.lower().split()
		correctList = []
		for eaWord in sentList:
			exclude = set(string.punctuation)
			eaWord = ''.join(ch for ch in eaWord if ch not in exclude)
			correctList.append(eaWord)

		# find occurance of first word said
		# print correctList
		# print phraseList
		try:
			indFirst = correctList.index(phraseList[0].lower())
		except:
			break
		resList = correctList
		if (indFirst > 0):
			resList = correctList[indFirst:]
		if len(resList) > maxLength:
			resList = resList[:maxLength]
		results.append(resList)
	return results



# given a phrase and file name, find sentences ontaining the phrase
def phraseToSentence(words,filename):
	f = open(filename).read()
	blob = TextBlob(f)
	matches = []
	for sent in blob.sentences:
		prevIndex = 0
		sentList = sent.words
		# go over each word in words and see if found
		if (len(words)==1) and (words[0] in sentList):
			matches.append(str(sent))
		else:
			found = 0
			for word in words:
				if not((word in sentList) 
					and (sentList.index(word)==prevIndex+1)):
					found = -1
					break
				else:
					prevIndex = sentList.index(word)
			if (found != -1):
				matches.append(str(sent))
	return matches




# given a word and filename, find the sentences containing the word
def wordsToSentence(words, filename):
	# 1. find sentences
	f = open(filename).read()
	blob = TextBlob(f)
	search_words = set(words)
	matches = []
	for sentence in blob.sentences:
		words = set(sentence.words)
		if search_words & words:  # intersection
			# if (sentence.sentiment[0] >0):
			# 	# print "============================="
			# 	# print sentence.sentiment
			# 	# print str(sentence)
			matches.append(str(sentence))
	# print matches
	return matches

# get times when are sentences said
def getTimes(arrSentences, filename):
	dict = {}
	with open(filename) as data_file:
		data = json.load(data_file)
	
	allWords = data['words']

	for s in arrSentences:
		result = findSentence(allWords, s)
		if (result != False):
			sStr = ' '.join(word for word in s)
			dict[sStr] = result
	return dict

def findWordInJson(word, data):
	indices = []
	for i in xrange(len(data)):
		if (data[i]['case']=="success") and (data[i]['word'].lower() == word.lower()):
			indices.append(i)
	return indices

# get times when a single word is said
def getWordTiming(words):
	allClips = []
	found = 0
	actualFiles = 0
	for word in words:
		for i in os.listdir(os.getcwd()+"/speeches/"):
			i = i.split('.txt',1)[0]
			txtFileName = 'speeches/'+i+".txt"
			mp3FileName = 'audio/'+i+".mp3"
			alignName = 'alignedJsons/'+i+".json"
			vidName = 'videos/'+i+'.mp4'
			if not(os.path.isfile(alignName) and os.path.isfile(vidName)):
				continue
			else:
				occurences = []
				with open(alignName) as data_file:
					data = json.load(data_file)
					allWords = data['words']
					indicesOccurence = findWordInJson(word,allWords)
					for j in indicesOccurence:
						currEntry = allWords[j]
						timeBegin = currEntry['start']
						timeEnd = currEntry['end']
						found += 1
						newDict = {'vid':vidName, 'entry':currEntry}
						allClips.append(newDict)
						found += 1
	print "found: "+str(found)
	return allClips


# find beginning and end of this sentence
def findSentence(allWords, sentence):
	# print sentence
	# listWords = sentence.split()
	listWords = sentence
	correct = []
	for w in listWords:
		exclude = set(string.punctuation)
		s = ''.join(ch for ch in w if ch not in exclude)
		s = s.lower()
		correct.append(s)
	listWords = correct

	# first get list of words of first word occurring
	firstWords = findWordInJson(listWords[0],allWords)
	# curr index is index in listWords
	currIndex = 1
	# next tier is next set of indices to iterate for next word
	nextTier = []
	# 2d list that keeps track of all, longest is result
	# init 2d list
	history = []
	for i in firstWords:
		tempWord = allWords[i]
		# print tempWord
		tempArr = []
		tempArr.append(tempWord)
		history.append(tempArr)
	if (len(history) == 0):
		return False

	# go through each index, see if proceeding matches
	while currIndex < len(listWords):
		for index in firstWords:
			if (index+1 < len(allWords)):
				currWord = listWords[currIndex]
				if ((allWords[index+1]['case']=='success') and 
					(allWords[index+1]['word'].lower()==currWord)):
					nextTier.append(index+1)

					for sList in history:
						if (sList[0]['word'].lower() == listWords[currIndex-1].lower()):
							if (sList[0]['start'] == allWords[index]['start']):
								sList.insert(0,allWords[index+1])
		
		currIndex += 1
		firstWords = nextTier

	if (len(findLongest(history)) < len(listWords)):
		# print 'len found: '+str(len(findLongest(history)))
		# print 'len need: '+str(len(listWords))
		return False
	return findLongest(history)


# def findAndAdd(alist, lastWord, newWord):
# 	print "lastword: ",lastWord
# 	print "newword: ",newWord
# 	for sList in alist:
# 		if sList[0] == lastWord:
# 			sList.insert(0,newWord)
# 			return

def findLongest(list):
	longest = list[0]
	for sList in list:
		if (len(sList) > len(longest)):
			longest = sList
	return longest

# get rid of extra spaces
def standardizeSpeeches():
	for i in os.listdir(os.getcwd()+"/speeches/"):
		newLines=[]
		if not('.txt' in i):
			continue
		with open('speeches/'+i,'r') as f:
			f.seek(0,0)
			for line in f:
				# print line
				line = line.replace('\n'," ")
				line = line.replace('\t'," ")
				line = line.replace('.', ". ")
				for j in xrange(1,15):
					spaces = " "*j
					line = line.replace(spaces," ")
				newLines.append(line)
		with open('speeches/'+i,'w') as d:
			for s in newLines:
				d.write(s)
# txtToVid()
# getMostCommonWords()
# standardizeSpeeches()
makeLongVideo()
joinSameWords()
# joinAll()
makeMasterVideo()