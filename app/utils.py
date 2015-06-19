import tldextract
import calendar
import time
import random
import datetime
import pytz
import requests_cache


SECONDS_IN_A_DAY = 60 * 60 * 24
SECONDS_IN_4_DAYS = 4 * SECONDS_IN_A_DAY

cache_recent = requests_cache.CachedSession(cache_name='recent', expire_after=300)
cache_old = requests_cache.CachedSession(cache_name='old', expire_after=SECONDS_IN_4_DAYS)

pacific = pytz.timezone('US/Pacific-New')


def get_todays_date():
    return datetime.datetime.now(pacific).date()


def find_segment_with_period(segment_list):
    for segment in segment_list:
        if "." in segment:
            return segment


def get_sitebit(url):
    ext = tldextract.extract(url)
    return "{}.{}".format(ext.domain, ext.suffix)


def get_start_and_end_posix(string_date):
    month_day_year_tuple = tuple(string_date.split('-'))
    date_segments = len(month_day_year_tuple)
    year = int(month_day_year_tuple[0])
    if date_segments == 3:
        startMonth = endMonth = int(month_day_year_tuple[1])
        startDay = endDay = int(month_day_year_tuple[2])
    elif date_segments == 2:
        startMonth = endMonth = int(month_day_year_tuple[1])
        startDay = 1
        endDay = calendar.monthrange(year, startMonth)[1]
    elif date_segments == 1:
        startMonth = 1
        endMonth = 12
        startDay = 1
        endDay = 31
    start_datetime = datetime.datetime(year, startMonth, startDay, 0, 0, 0, tzinfo=pacific)
    end_datetime = datetime.datetime(year, endMonth, endDay, 23, 59, 59, tzinfo=pacific)
    start_posix = int(start_datetime.strftime("%s"))
    end_posix = int(end_datetime.strftime("%s"))
    return start_posix, end_posix


def get_datetime_date(string_date):
    month_day_year_tuple = tuple(string_date.split('-'))
    month = int(month_day_year_tuple[1])
    day = int(month_day_year_tuple[2])
    year = int(month_day_year_tuple[0])
    return datetime.datetime(year, month, day, tzinfo=pacific).date()


def is_valid_date(string_date):
    date_components = string_date.split("-")
    num_date_components = len(date_components)
    if num_date_components < 1 or num_date_components > 3:
        return False
    if num_date_components == 2 or num_date_components == 1:
        date_components.append(1)
    if num_date_components == 1:
        date_components.append(1)
    for component in date_components:
        try:
            int(component)
        except ValueError:
            return False
    try:
        datetime.datetime(int(date_components[0]), int(date_components[1]), int(date_components[2]), tzinfo=pacific).date()
    except:
        return False
    return True


def get_stories_and_pages(string_date, page_num):
    start_and_end_posix = get_start_and_end_posix(string_date)
    start_posix = start_and_end_posix[0]
    end_posix = start_and_end_posix[1]
    base_url = "http://hn.algolia.com/api/v1/search?tags=story&"
    date_filter_url = ("numericFilters=created_at_i>{0},created_at_i<{1}"
                      .format(start_posix, end_posix))
    page_query = "&page={}&hitsPerPage=30".format(page_num)
    if time.time() - start_posix <= SECONDS_IN_4_DAYS:
        r = cache_recent.get(base_url + date_filter_url + page_query)
    else:
        r = cache_old.get(base_url + date_filter_url + page_query)
    r.raise_for_status()
    json_response = r.json()
    return get_stories_and_pages_from_json(json_response)


def get_stories_and_pages_from_json(json_response):
    num_pages = json_response["nbPages"]
    hits = json_response["hits"]
    for story in hits:
        if story["url"]:
            story["sitebit"] = get_sitebit(story["url"])
        else:
            story["url"] = ("https://news.ycombinator.com/item?id={}"
                           .format(story["objectID"]))
    stories = json_response["hits"]
    return stories, num_pages


def get_days_ago_str(datetime_date):
    days_ago_delta = get_todays_date() - datetime_date
    days_ago = days_ago_delta.days
    if days_ago == 0:
        return "today"
    elif days_ago == 1:
        return "1 day ago"
    else:
        return "{} days ago".format(days_ago)


def get_years_ago_str(years_ago):
    if years_ago == 0:
        return "this year"
    elif years_ago == 1:
        return "1 year ago"
    else:
        return "{} years ago".format(years_ago)


def get_random_date_bounded(start, end):
    return start + datetime.timedelta(
        seconds=random.randint(0, int((end-start).total_seconds())))


def get_months_ago(year, month):
    todays_date = get_todays_date()
    curr_year = todays_date.year
    curr_month = todays_date.month
    months_ago = 12 * (curr_year - year) + (curr_month - month)
    return months_ago


def get_months_ago_str(months_ago):
    if months_ago == 0:
        return "this month"
    elif months_ago == 1:
        return "1 month ago"
    else:
        return "{} months ago".format(months_ago)


def get_random_date():
    first_date = datetime.datetime(2006, 10, 9, tzinfo=pacific).date()
    return get_random_date_bounded(first_date, get_todays_date())


def get_next_prev_month_year(curr_month, curr_year):
    next_month = (curr_month % 12) + 1
    if next_month == 1:
        next_year = curr_year + 1
    else:
        next_year = curr_year
    next_month_year = "{}-{}".format(next_year, next_month)
        
    prev_month = (curr_month - 2) % 12 + 1
    if prev_month == 12:
        prev_year = curr_year - 1
    else:
        prev_year = curr_year
    prev_month_year = "{}-{}".format(prev_year, prev_month)
    return next_month_year, prev_month_year
