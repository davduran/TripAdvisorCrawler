from bs4 import SoupStrainer, BeautifulSoup
import re, json
import TAutil
import ReviewParser

class HotelParser:

    def __init__(self, hotel_url):
        self.city_id_searcher = re.compile(r'(?<=-g)\d*(?=-)')
        self.hotel_id_searcher = re.compile(r'(?<=-d)\d*(?=-)')
        self.reviews = None
        self.parse_init(hotel_url, True)
        
    def parse_init(self, hotel_url, is_hotel_page):
        """
        select review parts of hotel html.
        click the first review title to expand the the review entry
        """
        review_strainer = SoupStrainer(id='REVIEWS')
        self.hotel_html = TAutil.open_page(hotel_url)
        self.hotel_ori_url = hotel_url
        self.soup = BeautifulSoup(self.hotel_html, parse_only = review_strainer)

        # open the first review
        if is_hotel_page:
            first_review = TAutil.wrap_tripadvisor(str(self.soup.find('div', class_='quote').a['href']))
            hotel_html = TAutil.open_page(first_review)
            self.soup = BeautifulSoup(hotel_html, parse_only = review_strainer) 

    @property
    def rating_count(self):
        rating_number_s = self.soup.select('div.col2of2.composite span.compositeCount')
        rating_number = [TAutil.strip_comma(x.string) for x in rating_number_s]
        return rating_number

    @property
    def trip_type(self):
        trip_type_s = self.soup.select('div.trip_type div.value')
        trip_type = [TAutil.strip_comma(x.string) for x in trip_type_s]
        return trip_type

    @property
    def aspect_rating(self):
        aspect_rating_s = self.soup.select('#SUMMARYBOX .sprite-ratings')
        aspect_rating = [float(x['content']) for x in aspect_rating_s]
        return aspect_rating

    @property
    def hotel_id(self):
        hotel_id = self.hotel_id_searcher.search(self.hotel_url).group(0)            
        return hotel_id

    @property
    def city_id(self):
        city_id = self.city_id_searcher.search(self.hotel_url).group(0)
        return city_id

    @property
    def hotel_url(self):
        return self.hotel_ori_url

    @property
    def hotel_reviews(self):
        if not self.reviews:
            self.reviews = list()   
            while True:
                # test whether the page need ajax request
                temp_reviews = self.get_review()
                self.reviews.extend(temp_reviews)
                try:
                    next_page = TAutil.next_page(self.soup)
                except TypeError:
                    break
                self.parse_init(next_page, False)
        return self.reviews

    def check_ajax(self):
        quote = self.soup.find_all('div', class_='quote')
        return any(map(lambda x: not x.string, quote))
        
    def get_review(self):
        temp_reviews = self.soup.find_all(class_='review')

        title_content = []
        if self.check_ajax():
            print(self.soup.find_all('div', class_='quote'))

            review_ids = [ReviewParser.ReviewParser(x).review_id for x in temp_reviews]
            print(review_ids)

            tc = TAutil.fetch_ajax_title_content(review_ids)
            return list(zip(temp_reviews, tc))
        else:
            return list(zip(temp_reviews, [None]*len(temp_reviews)))
       

    def format_hotel(self, file_handler = None):
        text_t = "<hotel_id>{hotel_id}\n\
<city_id>{city_id}\n\
<rating_count>{rating_count}\n\
<trip_type>{trip_type}\n\
<aspect_rating>{aspect_rating}\n\
<hotel_url>{hotel_url}\n"
        text = text_t.format(hotel_id = self.hotel_id, 
            city_id = self.city_id, 
            rating_count = self.rating_count, 
            trip_type = self.trip_type,
            aspect_rating = self.aspect_rating, 
            hotel_url = self.hotel_url)

        if file_handler:
            file_handler.write(text)
        return text