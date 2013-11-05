import sys, logging, time, traceback
import os.path
import CityParser, HotelParser, ReviewParser

# url = "http://www.tripadvisor.com/Hotels-g60763-New_York_City_New_York-Hotels.html"
url = "http://www.tripadvisor.com/Hotels-g60713-San_Francisco_California-Hotels.html"
data_path = '../data/sf/'
error_file = '../data/error_log.txt'

def crawl():
	ferror = open(error_file, 'w')

	if not os.path.exists(data_path):
		os.makedirs(data_path)

	print('Parsing City {0}'.format(url))

	try:
		# with minimal review greater or equal than 100
		cp = CityParser.CityParser(url, 100)
	except:
		error_msg = 'Error in CityParser {0}'.format(url)
		print(error_msg)
		ferror.write(error_msg)
		return

	print('Fetching hotel urls.', end='')

	try:
		hotel_urls = cp.hotel_urls;
	except:
		error_msg = 'Error in hotel_urls {0}'.format(url)
		print(error_msg)
		ferror.write(error_msg)
		return

	print('{0} hotles'.format(len(hotel_urls)))

	for hotel_url in hotel_urls:
		# hp = HotelParser('http://www.tripadvisor.com/Hotel_Review-g34438-d85205-Reviews-Sofitel_Miami-Miami_Florida.html#REVIEWS')
		print('Fetching hotel page. {0}'.format(hotel_url))

		try:
			hp = HotelParser.HotelParser(hotel_url)
			hotel_file = 'hotel_{0}.txt'.format(hp.hotel_id)
			fout = open(os.path.join(data_path, hotel_file),'w')
			hp.format_hotel(fout)
			fout.close()
		except:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			error_msg = 'Error in hotel info {0}'.format(hotel_url)
			print(error_msg)
			traceback.print_exception(exc_type, exc_value, exc_traceback)
			ferror.write(error_msg)
		print('Fetching review info.')
		
		review_file = 'hotelreview_{0}.txt'.format(hp.hotel_id)
		fout = open(os.path.join(data_path, review_file),'w')
		for r in hp.hotel_reviews:
			try:
	 			x = ReviewParser.ReviewParser(*r)
	 			x.format_review(hp.hotel_id, fout)
	 			fout.write('\n')
	 			print('Fetched review {0}'.format(x.review_id))
			except:
				exc_type, exc_value, exc_traceback = sys.exc_info()
				error_msg = 'Error in review info {0}.{1}'.format(hp.hotel_id, x.review_id)
				print(error_msg)
				traceback.print_exception(exc_type, exc_value, exc_traceback)
				ferror.write(error_msg)
				input()
		fout.close()

	ferror.close()

if __name__=='__main__':
	crawl()