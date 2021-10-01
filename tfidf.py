import re, glob, math, os, time, csv

stopwords = ["a","about","above","after","again","against","all","am","an","and","any","are","as","at","be","because","been","before","being","below","between", "both", "but", "by", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from", "further", "had", "has", "have", "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "it", "it's", "its", "itself", "let's", "me", "more", "most", "my", "myself", "nor", "of", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "she", "she'd", "she'll", "she's", "should", "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "we", "we'd", "we'll", "we're", "we've", "were", "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with", "would", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves" ]
wordboundaries = [' ','.',',','!','?','(',')','[',']','{','}','-','_','+','=',';',':','"','@','#','$','%','^','&','*','|','\\',"/","<",">","\n","\r\n"]

class document():
	def __init__(self,contentName,content,categories = []):
		self.name = contentName
		self.content = content
		self.categories = categories
		self.terms = {}
		self.ngrams = {}
		self.categoryIDs = []
		self.totalTerms = 0
class word():
	def __init__(self,wordName):
		self.name = wordName
		self.relatedDocumentIDs = []
		self.relatedCategoryIDs = []
		self.relatedWordIDs = []
		
class category():
	def __init__(self,categoryName):
		self.name = categoryName
		self.ngrams = {}
		self.terms = {}
		self.relatedDocumentIDs = []

class tfidf():
	def __init__(self,name = 'tfidf'):
		self.name = name
		self.ngrams = {}
		self.terms = {}
		self.documents = {}
		self.categories = {}
	def scoreDocuments(self):
		global stopwords
		start = int(round(time.time() * 1000))
		print('Scoring document terms')
		docIDs = []
		termScores = {}
		for docIndex,thisDoc in self.documents.items():
			docIDs.append(docIndex)
		for termIndex,thisTerm in self.terms.items():
			termScores[termIndex] = {}
			for docIndex in docIDs:
				if termIndex in self.documents[docIndex].terms:
					tf = self.documents[docIndex].terms[termIndex] / self.documents[docIndex].totalTerms
					idf = math.log(len(self.documents) / len(self.terms[termIndex].relatedDocumentIDs))
					tfidf = tf * idf
					termScores[termIndex][docIndex] = tfidf
				else:
					termScores[termIndex][docIndex] = 0
		
		end = int(round(time.time() * 1000))
		print("Run time:" + str(end - start))
		print('Scoring document ngrams')
		start = int(round(time.time() * 1000))
		
		ngramScores = {}
		for ngramIndex,thisNgram in self.ngrams.items():
			ngramScores[ngramIndex] = {}
			ngramFrequency = 0
			for docIndex in docIDs:
				if ngramIndex in self.documents[docIndex].ngrams:
					ngramFrequency = ngramFrequency + self.documents[docIndex].ngrams[ngramIndex]
					score = 0
					for thisTermID in self.ngrams[ngramIndex].relatedWordIDs:
						score = score + termScores[thisTermID][docIndex]
					score = score / len(self.ngrams[ngramIndex].name.split(' '))
					ngramScores[ngramIndex][docIndex] = score
				else:
					ngramScores[ngramIndex][docIndex] = 0
			topDoc = 0
			docSum = 0
			for docIndex in docIDs:
				docSum = docSum + ngramScores[ngramIndex][docIndex]
				if ngramScores[ngramIndex][docIndex] > ngramScores[ngramIndex][topDoc]:
					topDoc = docIndex
			ngramScores[ngramIndex]['frequency'] = ngramFrequency
			if topDoc == 0:
				ngramScores[ngramIndex]['doc'] = '-'
			else:
				ngramScores[ngramIndex]['doc'] = self.documents[topDoc].name
		end = int(round(time.time() * 1000))
		print("Run time:" + str(end - start))
		csvPath = self.name + ' - documents.csv'
		with open(csvPath, 'w', newline = '', encoding = "utf-8") as csvfile:
			output = csv.writer(csvfile, delimiter = ',', quotechar = '"')
			header = ['Ngram','Frequency','Relevant Document']
			for docIndex,thisDoc in self.documents.items():
				header.append(self.documents[docIndex].name)
			output.writerow(header)
			
			for ngramIndex,thisScore in ngramScores.items():
				thisRow = [self.ngrams[ngramIndex].name,ngramScores[ngramIndex]['frequency'],ngramScores[ngramIndex]['doc']]
				for docIndex,thisDoc in self.documents.items():
					thisRow.append(ngramScores[ngramIndex][docIndex])
				output.writerow(thisRow)
	
	def scoreCategories(self):
		global stopwords
		print('Scoring category terms')
		catIDs = []
		termScores = {}
		for catIndex,thisDoc in self.categories.items():
			catIDs.append(catIndex)
		for termIndex,thisTerm in self.terms.items():
			termScores[termIndex] = {}
			
			for catIndex in catIDs:
				if termIndex in self.categories[catIndex].terms:
					totalTerms = 0
					for docID in self.categories[catIndex].relatedDocumentIDs:
						totalTerms = totalTerms + self.documents[docID].totalTerms
					tf = self.categories[catIndex].terms[termIndex] / totalTerms
					idf = math.log(len(self.categories) / len(self.terms[termIndex].relatedCategoryIDs))
					tfidf = tf * idf
					termScores[termIndex][catIndex] = tfidf
				else:
					termScores[termIndex][catIndex] = 0
		print('Scoring category ngrams')
		ngramScores = {}
		for ngramIndex,thisNgram in self.ngrams.items():
			ngramScores[ngramIndex] = {}
			ngramFrequency = 0
			for catIndex in catIDs:
				if ngramIndex in self.categories[catIndex].ngrams:
					ngramFrequency = ngramFrequency + self.categories[catIndex].ngrams[ngramIndex]
					score = 0
					for thisTermID in self.ngrams[ngramIndex].relatedWordIDs:
						score = score + termScores[thisTermID][catIndex]
					score = score / len(self.ngrams[ngramIndex].name.split(' '))
					ngramScores[ngramIndex][catIndex] = score
				else:
					ngramScores[ngramIndex][catIndex] = 0
			topCat = 0
			catSum = 0
			for catIndex in catIDs:
				catSum = catSum + ngramScores[ngramIndex][catIndex]
				if ngramScores[ngramIndex][catIndex] > ngramScores[ngramIndex][topCat]:
					topCat = catIndex
			ngramScores[ngramIndex]['frequency'] = ngramFrequency
			if catSum == 0:
				ngramScores[ngramIndex]['cat'] = '-'
			else:
				ngramScores[ngramIndex]['cat'] = self.categories[topCat].name
		csvPath = self.name + ' - categories.csv'
		with open(csvPath, 'w', newline = '', encoding = "utf-8") as csvfile:
			output = csv.writer(csvfile, delimiter = ',', quotechar = '"')
			header = ['Ngram','Frequency','Relevant Category']
			for catIndex,thisCat in self.categories.items():
				header.append(self.categories[catIndex].name)
			output.writerow(header)
			
			for ngramIndex,thisScore in ngramScores.items():
				thisRow = [self.ngrams[ngramIndex].name,ngramScores[ngramIndex]['frequency'],ngramScores[ngramIndex]['cat']]
				for catIndex,thisCat in self.categories.items():
					thisRow.append(ngramScores[ngramIndex][catIndex])
				output.writerow(thisRow)

	def addNgram(self,ngram,docID):
		ngramID = -1
		for index,thisNgram in self.ngrams.items():
			if(thisNgram.name == ngram):
				ngramID = index
				break
		if ngramID == -1:
			ngramID = len(self.ngrams)
			self.ngrams[ngramID] = word(ngram)
			
		if docID not in self.ngrams[ngramID].relatedDocumentIDs:
			self.ngrams[ngramID].relatedDocumentIDs.append(docID)
		if ngramID in self.documents[docID].ngrams:
			self.documents[docID].ngrams[ngramID] = self.documents[docID].ngrams[ngramID] + 1
		else:
			self.documents[docID].ngrams[ngramID] = 1
		for catID in self.documents[docID].categoryIDs:
			if ngramID in self.categories[catID].ngrams:
				self.categories[catID].ngrams[ngramID] = self.categories[catID].ngrams[ngramID] + 1
			else:
				self.categories[catID].ngrams[ngramID] = 1
		return ngramID
	def addTerm(self,term,docID):
		termID = -1
		for index,thisTerm in self.terms.items():
			if(thisTerm.name == term):
				termID = index
				break
		if termID == -1:
			termID = len(self.terms)
			self.terms[termID] = word(term)
			
		if docID not in self.terms[termID].relatedDocumentIDs:
			self.terms[termID].relatedDocumentIDs.append(docID)
		if termID in self.documents[docID].terms:
			self.documents[docID].terms[termID] = self.documents[docID].terms[termID] + 1
		else:
			self.documents[docID].terms[termID] = 1
		for catID in self.documents[docID].categoryIDs:
			if catID not in self.terms[termID].relatedCategoryIDs:
				self.terms[termID].relatedCategoryIDs.append(catID)
			if termID in self.categories[catID].terms:
				self.categories[catID].terms[termID] = self.categories[catID].terms[termID] + 1
			else:
				self.categories[catID].terms[termID] = 1
		return termID
		
	def addDocument(self,document):
		docID = len(self.documents)
		print('Added',docID)
		self.documents[docID] = document
		for thisCategory in document.categories:
			self.addCategory(thisCategory,docID)
		self.processDocument(docID)
	
	def addCategory(self,categoryName,docID):
		catID = -1
		for index,thisCat in self.categories.items():
			if thisCat.name == categoryName:
				catID = index
				break
		if catID == -1:
			catID = len(self.categories)
			self.categories[catID] = category(categoryName)
		self.categories[catID].relatedDocumentIDs.append(docID)
		self.documents[docID].categoryIDs.append(catID)
	def processDocument(self,docID):
		global stopwords
		global wordboundaries
		
		content = str(self.documents[docID].content)
		content = re.sub('[0-9]','',content)
		termRegex = "+|\\".join(wordboundaries)
		phrases = re.split("\.|\?|\!",content)
		
		for thisPhrase in phrases:
			termIDs = []
			terms = re.split(termRegex,thisPhrase)
			terms = [thisTerm.lower().strip() for thisTerm in terms]
			for thisTerm in terms:
				if(thisTerm != '' and thisTerm not in stopwords):
					termIDs.append(self.addTerm(thisTerm,docID))
					self.documents[docID].totalTerms = self.documents[docID].totalTerms + 1
			ngramIDs = []
			maxSize = 5
			wordCount = len(terms)	
			if(wordCount > 1):
				for strLen in range(1,maxSize):
					for start in range(wordCount - strLen + 1):
						if(terms[start] not in stopwords and terms[(start + strLen - 1)] not in stopwords):
							thisGram = " ".join(terms[start:(start + strLen)]).strip()
							if(thisGram != '' and thisGram not in stopwords):
								ngramIDs.append(self.addNgram(thisGram,docID))
			for thisNgramID in ngramIDs:
				for thisTermID in termIDs:
					if self.ngrams[thisNgramID].name.find(self.terms[thisTermID].name) != -1:
						if thisTermID not in self.ngrams[thisNgramID].relatedWordIDs:
							self.ngrams[thisNgramID].relatedWordIDs.append(thisTermID)
