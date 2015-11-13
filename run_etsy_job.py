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

	def getJSONResponse(self,url):
		resp = requests.get(url)
           	return json.loads(resp.text)

	def completeURL(self,urlParameters):
 		url =  "%s%sapi_key=%s" % (self.baseUrl,urlParameters,self.apiKey)
		return url

	def getAllListingDescriptionsForShop(self,shop) : 
		list = []
		url = self.completeURL('shops/%s/listings/active?' % shop)
		data =  self.getJSONResponse(url)
 		listingCount = data['count']
		listings = data['results']
		descriptionString = ""
		for listing in listings:
			descriptionString+=" " + listing['description'].replace("\n"," ")
#		description =  (' '.join(listing['description']) for listing in listings)
		return descriptionString

	def runChallenge(self):
		# This gets the featured 50 shops from etsy
		url = self.completeURL('shops?limit=50&offset=0&')
		data = self.getJSONResponse(url) 
		shops = data['results']

		#empty dict to store shop and totalDescriptionString
		shopDescriptionMap = {}

		for shop in shops:
			description =  self.getAllListingDescriptionsForShop(shop['shop_id'])
			shopDescriptionMap[shop['shop_name']] = description 
		
		for shop in shopDescriptionMap:
			print shop
			self.getTop5wordsForShop(shopDescriptionMap[shop])		



	def getTop5wordsForShop(self,description):
		map = {}
		words = description.split()
		for word in words:
			lowerWord = word.lower().encode('utf-8').strip()
			curatedWord = re.sub('[^A-Za-z0-9]+','', lowerWord)
			word = curatedWord if len(curatedWord) > 3 else None
			if curatedWord in map:
				map[word]+=1
			else:
				map[word]=1
#		orderedWords = OrderedDict(sorted(map.items(), key=lambda t: t[1],reverse=True)) 
#		first5Words = {k: orderedWords[k] for k in orderedWords.keys()[:5]}	
		first5Words = collections.Counter(map).most_common(5)

		print first5Words

try:
	apiKey = sys.argv[1]
except IndexError:
	sys.exit("apiKey can't be null")
etsy = Etsy(apiKey)
dictShopDescription = etsy.runChallenge()	
