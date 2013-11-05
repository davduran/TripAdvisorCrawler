from bs4 import SoupStrainer, BeautifulSoup
from datetime import datetime
import re
import TAutil


class ReviewParser:
	def __init__(self, reviewer_tag, tc=None):
		self.init(reviewer_tag)
		self.date_searcher = re.compile(r'(?<=Reviewed ).*')
		self.tc = tc

	def init(self, reviewer_tag):
		self.reviewer_tag = reviewer_tag

	@property
	def username(self):
		username_div = self.reviewer_tag.find('div', class_='username')
		try:
			username = str(username_div.span.string).strip()
		except AttributeError:
			try:
				username = str(username_div.string).strip()
			except AttributeError:
				username = ''
		return username

	@property
	def badges(self):
		"""
			totalReviewBadge contains title and counts
			helpfulVotes contains the number of helpful votes
		"""
		try: 
			totalReviewBadge = self.reviewer_tag.find('div', class_='totalReviewBadge')

			try: 
				reviewerTitle = str(totalReviewBadge.find('div', class_='reviewerTitle').string)
			except AttributeError:
				reviewerTitle = ''

			counts = totalReviewBadge.find_all('span', class_='badgeText')
			try:
				review_count = TAutil.strip_comma(counts[0].string)
			except (AttributeError, IndexError):
				review_count = -1

			try:
				hotel_review_count = TAutil.strip_comma(counts[1].string)
			except (AttributeError, IndexError):
				hotel_review_count = -1
		except AttributeError:
			reviewerTitle = ''
			review_count = -1
			hotel_review_count = -1

		try:
			helpfulVotes = str(self.reviewer_tag.select('div.helpfulVotesBadge span.badgeText')[0].string)
			helpful_count = TAutil.strip_comma(helpfulVotes)
		except (AttributeError, IndexError):
			helpful_count = -1
		return reviewerTitle, review_count, hotel_review_count, helpful_count

	@property
	def review_date(self):
		reviewed_date = str(self.reviewer_tag.find('span', class_='ratingDate').contents[0].string).strip()
		reviewed_date = self.date_searcher.search(reviewed_date).group()
		reviewed_date = datetime.strptime(reviewed_date, '%B %d, %Y')
		return reviewed_date.strftime('%Y-%m-%d')


	@property
	def review_id(self):
		return str(self.reviewer_tag['id'])[2:]

	@property
	def review_title(self):
		if self.tc:
			text = self.tc['name']
		else:
			text = str(self.reviewer_tag.find('div', class_='quote').string)
		return TAutil.process_text(text)

	@property
	def review_content(self):
		if self.tc:
			text = self.tc['body']
		else:
			text = self.reviewer_tag.find('div', class_='entry').p.strings
			text = ' '.join(text)
		return TAutil.process_text(text)

	@property
	def trip_type(self):
		try:
			t_type = str(self.reviewer_tag.find(class_='recommend-titleInline').string)
		except AttributeError:
			return ""
		s = t_type.split()[-1]
		if s not in ['business', 'couple', 'family', 'friends', 'solo']:
			s = ""
		return s

	@property
	def numHlp(self):
		try:
			return TAutil.strip_comma(self.reviewer_tag.find('span', class_='numHlpIn').string)
		except AttributeError:
			return 0

	@property
	def rate_overall(self):
		return float(self.reviewer_tag.find(class_='rate_s').img['content'])

	@property
	def rate_aspect(self):
		rate_list = [-1]*len(TAutil.aspects_name)
		r_list = self.reviewer_tag.find_all(class_='recommend-answer')
		if r_list:
			for r in r_list:
				try:
					i = TAutil.aspects[next(r.stripped_strings)]
					v = float(r.img['content'])
					rate_list[i] = v
				except KeyError:
					pass
		return rate_list

	def format_review(self, hotel_id, file_handler = None):
# 		text_t = "<hotel_id>{0}\n\
# <review_id>{1}\n\
# <username>{2}\n\
# <badges>{3}\n\
# <review_date>{4}\n\
# <rate_overall>{5}\n\
# <rate_aspect>{6}\n\
# <trip_type>{7}\n\
# <numHlp>{8}\n\
# <review_title>{9}\n\
# <review_content>{10}\n"
		# text = text_t.format(hotel_id, self.review_id, self.username, self.badges, \
		# 	self.review_date, self.rate_overall, self.rate_aspect, self.trip_type, self.numHlp, self.review_title, self.review_content)
		text_list = [self.review_id, hotel_id, self.username]
		text_list.extend(self.badges)
		text_list.extend([self.review_date, self.rate_overall])
		text_list.extend(self.rate_aspect)
		text_list.extend([self.trip_type, self.numHlp, self.review_title, self.review_content])
		text_mysql = '\t'.join([str(u) for u in text_list]) + '\n'

		if file_handler:
			file_handler.write(text_mysql)
		return text_mysql
