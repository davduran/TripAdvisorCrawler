import urllib.request, urllib.parse, http.cookiejar, html.parser
import gzip
import codecs
import re, json


comma_number_s = re.compile(r'\b[1-9]\d{0,2}(,\d{3})*\b|\b[1-9]\d*\b|\b0\b')
html_token_s = re.compile(r'<br/>|“|”|\n')
aspects_name = ['Sleep Quality', 'Location', 'Rooms', 'Service', 'Value', 'Cleanliness']
aspects = dict(zip(aspects_name, range(len(aspects_name))))

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
opener.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36'), 
('Accept-Encoding','gzip, deflate'), ('Accept', 'text/html'), ('Connection', 'keep-alive')]

def open_page(url):
	"""
	Open a web page
	"""
	page = gzip.GzipFile(fileobj = opener.open(url))
	return page.read().decode('utf-8')

def wrap_tripadvisor(r_url):
	"""
	Add http://www.tripadvisor.com/
	"""
	return "http://www.tripadvisor.com/" + r_url

def strip_comma(str_num):
	try:
		return int(comma_number_s.search(str_num).group().replace(',', ''))
	except AttributeError:
		return None

def next_page(soup):
	return wrap_tripadvisor(str(soup.find('a', class_='sprite-pageNext')['href']))

def process_text(text):
	return html_token_s.sub('', text)

def save_hotel_review(hotel_text, reviews_text):
	pass

def open_json(r_url):
	t = opener.open(r_url).read().decode('utf-8')
	return re.sub(r'[\t\n\r\\]', '', t)

def fetch_ajax_title_content(review_ids):
	url_t = "http://www.tripadvisor.com/UserReviewController?a=reviewWithAnswers&r=" + ':'.join(review_ids)
	print(url_t)
	return json.loads(open_json(url_t))