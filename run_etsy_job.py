import requests,json
import re
import collections
from operator import itemgetter
from mrjob.job import MRJob
import sys

class Etsy:

	def __init__(self,apiKey):
		self.apiKey = apiKey
		self.baseUrl = 'https://openapi.etsy.com/v2/'

	def getJSONResponse(self,url,parameters):
		resp = requests.get(url,parameters)
           	return json.loads(resp.text)

	def completeURL(self,urlParameters):
 		url =  "%s%s" % (self.baseUrl,urlParameters)
		return url

	def getAllListingDescriptionsForShop(self,shop) : 
		list = []
		url = self.completeURL('shops/%s/listings/active' % shop)
		data =  self.getJSONResponse(url,{'api_key':self.apiKey})
 		listingCount = data['count']
		listings = data['results']
		descriptionString = ""
		for listing in listings:
			descriptionString+=" " + listing['description'].replace("\n"," ")
		description =  (' '.join(listing['description']) for listing in listings)
		return descriptionString

	def runChallenge(self):
		# This gets the featured 50 shops from etsy
		url = self.completeURL('shops')
		data = self.getJSONResponse(url,{'limit':'50','offset':'0','api_key':self.apiKey}) 
		
		# Not paginating, since the no. of listings returned per shop are consistently lower than 50
		
		shops = data['results']

		#empty dict to store shop and totalDescriptionString
		shopDescriptionMap = {}

		for shop in shops:
			description =  self.getAllListingDescriptionsForShop(shop['shop_id'])
			shopDescriptionMap[shop['shop_name']] = description 
		
		for shop in shopDescriptionMap:
			wordList = self.getTop5wordsForShop(shopDescriptionMap[shop])		
			print "%s = %s" % (shop,wordList)


	def getTop5wordsForShop(self,description):
		map = {}
		words = description.split()
		for word in words:
			# requests gets unicode data. Encoding back to utf-8
			lowerWord = word.lower().encode('utf-8').strip()
			
			# Curating word to substitute any letter which is not alphanumeric
			curatedWord = re.sub('[^A-Za-z0-9]+','', lowerWord)

			# Not using fancy nltk to do stop words and stemming
			# To avoid lots of and's and or's etc. Trying to only 
			#  look for words that are more than 3 letters in length
			word = curatedWord if len(curatedWord) > 3 else None
			if curatedWord in map:
				map[word]+=1
			else:
				map[word]=1
		return collections.Counter(map).most_common(5)

try:
	apiKey = sys.argv[1]
except IndexError:
	sys.exit("apiKey can't be null")
etsy = Etsy(apiKey)
dictShopDescription = etsy.runChallenge()	
