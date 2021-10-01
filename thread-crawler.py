import os, requests, csv, sys, re
from queue import Queue
from threading import Thread
from time import time
import htmlextractor
import tfidf


class crawlWorker(Thread):
	def __init__(self,queue,urlData,name):
		Thread.__init__(self)
		self.queue = queue
		self.urlData = urlData
		self.name = name
	def run(self):
		while True:
			urlIndex = self.queue.get()
			try:
				self.urlData[urlIndex]['startTime'] = time()
				print(self.name,'getting',self.urlData[urlIndex]['url'])
				HTMLData = self.getData(self.urlData[urlIndex]['url'])
				for index,thisData in HTMLData.items():
					if HTMLData[index].type == 'body':
						pageContent = HTMLData[index].data
				self.urlData[urlIndex]['content'] = pageContent
				self.urlData[urlIndex]['endTime'] = time()
			except Exception as e:
				print(e)
			finally:
				self.queue.task_done()

	def getData(self,url):
		parser = htmlextractor.HTMLextractor()
		parser.addExtractor(htmlextractor.dataDefinition('body','body'))
		
		html = self.fetchURL(url)
		html = re.sub(r'<script\b[^>]*>([\s\S]*?)<\/script>','',html)
		html = re.sub(r'<style\b[^>]*>([\s\S]*?)<\/style>','',html)
		parser.feed(html)

		return parser.extractedData
	def fetchURL(self,URL):
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0',
			'Accept-Language': '*/*',
			'Referer': 'google.com',
			'Accept-Encoding': 'gzip, deflate'
			}
		HTTPrequest = requests.get(URL,headers = headers)
		return HTTPrequest.text

class crawlThreader:
	def __init__(self):
		self.workers = 5
		self.urlData = {}
		self.queue = Queue()
	def startWorkers(self):
		for i in range(self.workers):
			worker = crawlWorker(self.queue,self.urlData,'worker' + str(i))
			worker.daemon = True
			worker.start()
	def crawlList(self,urls):
		index = 0
		for thisURL in urls:
			self.urlData[index] =  {'url':thisURL,'content':'','startTime':0,'endTime':0}
			index = index + 1
		for index,thisURL in self.urlData.items():
			self.queue.put(index)
		self.startWorkers()
		self.queue.join()
	def exportCrawl(self,csvPath):
		with open(csvPath, 'w', newline = '', encoding = "utf-8") as csvfile:
			output = csv.writer(csvfile, delimiter = ',', quotechar = '"')
			header = ['URL','Start Time','End Time','Body Content']
			output.writerow(header)
			for index,thisURL in self.urlData.items():
				row = []
				row.append(self.urlData[index]['url'])
				row.append(self.urlData[index]['startTime'])
				row.append(self.urlData[index]['endTime'])
				content = re.sub('\s+',' ',self.urlData[index]['content'])
				row.append(content)
				output.writerow(row)

def main():
	startTime = time()
	
	crawler = crawlThreader()
	urls = []
	pageCategory = []
	
	csvPath = 'test-urls.csv'
	with open(csvPath,'r') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=',')
		for row in csv_reader:
			urls.append(row[0])
			pageCategory.append(row[1])
	crawler.crawlList(urls)

	print('Run Time',time() - startTime)
	
	t = tfidf.tfidf('test-site-tfidf')
	
	for index,thisURL in crawler.urlData.items():
		content = re.sub('\s+',' ',crawler.urlData[index]['content'])
		t.addDocument(tfidf.document(crawler.urlData[index]['url'],content,[pageCategory[index]]))
	
	t.scoreDocuments()
	t.scoreCategories()
	
	crawler.exportCrawl('test-site-crawl.csv')
	
if __name__ == '__main__':
	main()