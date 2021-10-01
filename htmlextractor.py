import os, csv, glob, copy, gc, time
from html.parser import HTMLParser

class dataDefinition:
	def __init__(self,type,tag):
		self.type = type
		self.tag = tag
		self.attributes = []
		self.requestedData = ''
		self.parentType = ''
class dataExtractor:
	def __init__(self,id,type,tag,active = True):
		self.id = id
		self.type = type
		self.tag = tag
		self.active = active
		self.data = ''
		self.depth = 1
		self.parentID = -1
		self.children = []
	def __str__(self):
		return self.data
	def addData(self,newData):
		if(self.active):
			self.data = self.data + " " + newData
	def addLevel(self):
		if(self.active):
			self.depth += 1
	def removeLevel(self):
		if(self.active):
			self.depth -= 1
			if(self.depth <= 0):
				self.active = False
class HTMLextractor(HTMLParser):
	
	def __init__(self, *args, **kwargs):
		super(HTMLextractor, self).__init__(*args, **kwargs)
		self.definitions = []
		self.extractedData = {}
	def addExtractor(self,dataDefinition):
		self.definitions.append(dataDefinition)
	def getDefinitions(self,tag,attrs):
		matchingDefs = []
		for thisDefinition in self.definitions:
			extractorMatch = True
			if(tag == thisDefinition.tag):
				if(thisDefinition.attributes != []):
					if(attrs != []):
						for thisAttribute in thisDefinition.attributes:
							if(thisAttribute[0] in [thisAttr[0] for thisAttr in attrs]):
								for tagAttribute in attrs:
									if(tagAttribute[0] == thisAttribute[0]):
										if(tagAttribute != thisAttribute and thisAttribute[1] != '*'):
											extractorMatch = False
											break
							else:
								extractorMatch = False
								break
					else:
						extractorMatch = False
			else:
				extractorMatch = False
			if(extractorMatch == True):
				matchingDefs.append(thisDefinition)
		return matchingDefs
	
	def handle_starttag(self,tag,attrs):
		for index,thisData in self.extractedData.items():
			if(self.extractedData[index].tag == tag):
				self.extractedData[index].addLevel()
		
		foundDefs = self.getDefinitions(tag,attrs)
		for thisDef in foundDefs:
			dataID = len(self.extractedData)
			self.extractedData[dataID] = dataExtractor(dataID,thisDef.type,thisDef.tag)
			
			if(thisDef.requestedData != ''):
				for thisAttribute in attrs:
					if(thisAttribute[0] == thisDef.requestedData):
						self.extractedData[dataID].addData(thisAttribute[1])

			if(thisDef.parentType != ''):
				for index,thisData in self.extractedData.items():
					if(self.extractedData[index].type == thisDef.parentType and self.extractedData[index].active == True):
						self.extractedData[index].children.append(dataID)
						self.extractedData[dataID].parentID = index

	def handle_endtag(self,tag):
		for index,thisData in self.extractedData.items():
			if(self.extractedData[index].tag == tag):
				self.extractedData[index].removeLevel()
	def handle_data(self,data):
		for thisDefinition in self.definitions:
			if(thisDefinition.requestedData == ''):
				for index,thisData in self.extractedData.items():
					if(self.extractedData[index].type == thisDefinition.type):
						self.extractedData[index].addData(data)
	def exportToCSV(self,csvPath):
		if(self.definitions != [] and self.extractedData != {}):
			with open(csvPath, 'w', newline = '', encoding="utf-8") as csvfile:
				output = csv.writer(csvfile, delimiter=',', quotechar='"')
				csvHeader = ['Name','Extracted Data','Characters']
				output.writerow(csvHeader)
				
				for thisExtractor in self.definitions:
					for thisData in thisExtractor.foundData:
						if(self.extractedData[thisData].data != ''):
							chrCount = str(len(self.extractedData[thisData].data))
							output.writerow([thisExtractor.name,self.extractedData[thisData].data,chrCount])