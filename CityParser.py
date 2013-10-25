from bs4 import SoupStrainer, BeautifulSoup
import TAutil
import re

class CityParser:
	"""
	Parse all hotels of a city

	return urls of hotels with more than min_reviews
	"""

	def __init__(self, city_page_url, min_reviews=100):
		self.parse_init(city_page_url)
		self.min_reviews = min_reviews
		self.urls = None

	def parse_init(self, city_page_url):
		"""
		initialize the soup
		"""
		city_html = TAutil.open_page(city_page_url)
		strainer = SoupStrainer(id="ACCOM_OVERVIEW")
		self.soup = BeautifulSoup(city_html, parse_only = strainer) 		

	@property
	def hotel_urls(self):
		if not self.urls:
			self.urls = list()	
			while True:
				hotels = self.soup.find_all(id=re.compile(r'hotel_\d*'))
				temp_urls = [self.find_hotel_url(x) for x in hotels if self.large_reviews(x)]
				self.urls.extend(temp_urls)
				try:
					next_page =	TAutil.next_page(self.soup)
				except TypeError:
					break
				self.parse_init(next_page)
		return self.urls

	def large_reviews(self, hotel):
		try:
			temp_str = str(hotel.find('span', class_='more').a.string).strip()
			number_reviews = TAutil.strip_comma(temp_str)
		except AttributeError as e:
			return False
		if number_reviews < self.min_reviews:
			return False
		else:
			return True

	def find_hotel_url(self, hotel):
		return TAutil.wrap_tripadvisor(str(hotel.find(class_='property_title')['href']))