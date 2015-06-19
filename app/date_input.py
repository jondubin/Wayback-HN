from utils import (get_next_prev_month_year,
                   get_years_ago_str,
                   get_datetime_date,
                   get_days_ago_str,
                   get_months_ago,
                   get_months_ago_str)
import datetime
from calendar import month_abbr

                  
class DateInput(object):
    def __init__(self, date_str, todays_date):
        self.date_str = date_str
        self.todays_date = todays_date
        self.date_split_by_dashes = date_str.split("-")
        self.prev_date_str = None
        self.next_date_str = None
        self.curr_date_formatted = None
        self.days_ago_str = None
        self.no_stories_text = None
        self.first_date = None
        self.last_date = None
        self.day_month_or_year = None
        num_date_components  = len(self.date_split_by_dashes)
        if num_date_components == 1:
            self.initialize_year(date_str)
        elif num_date_components == 2:
            self.initialize_year_month(date_str)
        elif num_date_components ==3:
            self.initialize_year_month_day(date_str)
            
    def initialize_year(self, date_str):
        self.prev_date_str = int(date_str) - 1
        self.next_date_str = int(date_str) + 1
        self.curr_date_formatted = date_str
        self.days_ago_str = get_years_ago_str(self.todays_date.year - int(date_str))
        self.first_date = "2006"
        self.last_date = self.todays_date.year
        self.day_month_or_year = "year"

    def initialize_year_month(self, date_str):
        year = int(self.date_split_by_dashes[0])
        month = int(self.date_split_by_dashes[1])
        next_prev_month_year = get_next_prev_month_year(month, year)
        self.next_date_str = next_prev_month_year[0]
        self.prev_date_str = next_prev_month_year[1]
        self.curr_date_formatted = "{} {}".format(month_abbr[month], year)
        self.days_ago_str = get_months_ago_str(get_months_ago(year, month))
        self.first_date = "2006-10"
        self.last_date = "{}-{}".format(self.todays_date.year, self.todays_date.month)
        self.day_month_or_year = "month"

    def initialize_year_month_day(self, date_str):
        datetime_date = get_datetime_date(date_str)
        prev_day_datetime = datetime_date - datetime.timedelta(days=1)
        self.prev_date_str = prev_day_datetime.isoformat()
        next_day_datetime = datetime_date + datetime.timedelta(days=1)
        self.next_date_str = next_day_datetime.isoformat()
        self.curr_date_formatted = "{:%b %d, %Y}".format(datetime_date)
        self.days_ago_str = get_days_ago_str(datetime_date)
        self.first_date = "2006-10-9"
        self.last_date = self.todays_date.isoformat()
        self.day_month_or_year = "day"

