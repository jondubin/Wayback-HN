from flask import render_template, request, redirect
#from enum import Enum
import tldextract
from app import app
# from __init__ import get_stories_around_time
# from __init__ import get_time_years_ago
import calendar
import utils
import datetime
import requests
import pprint
import random

pp = pprint.PrettyPrinter(indent=4)


# def unix_time(dt):
#     epoch = datetime.utcfromtimestamp(0)
#     delta = dt - epoch
#     return delta.total_seconds()

# class RangeType(Enum):
#     day = 1
#     month = 2
#     year = 3


def find_segment_with_period(segment_list):
    for segment in segment_list:
        if "." in segment:
            return segment


def get_sitebit(url):
    ext = tldextract.extract(url)
    return "{}.{}".format(ext.domain, ext.suffix)


def get_stories_and_pages_with_bounds(start_posix, end_posix, page_num):
    base_url = "http://hn.algolia.com/api/v1/search?tags=story&"
    date_filter_url = "numericFilters=created_at_i>{0},created_at_i<{1}".format(start_posix, end_posix)
    page_query = "&page={}&hitsPerPage=30".format(page_num)
    r = requests.get(base_url + date_filter_url + page_query)
    json_response = r.json()
    num_pages = json_response["nbPages"]
    hits = json_response["hits"]
    for story in hits:
        if story["url"]:
            story["sitebit"] = get_sitebit(story["url"])
        else:
            story["url"] = "https://news.ycombinator.com/item?id={}".format(story["objectID"])

    return (json_response["hits"], num_pages)

# TODO: only show more when they are more pages
# TODO: cache, but refresh cache weekly
# TODO: rank counter
# TODO: webarchive link
# TODO: time or days ago
# TODO: weeks
# TODO: if date before or after first/last date, go to first/last
# TODO: show date in header
# TODO: cache older stories not newer ones
# TODO: move code out of views
# TODO: west coast time instead of UTC by using POSIX everywhere (even today)
# TODO: do for weeks, months, years
# TODO: 404 page
# TODO: refactor


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
    start_datetime = datetime.datetime(year, startMonth, startDay, 0, 0, 0)
    end_datetime = datetime.datetime(year, endMonth, endDay, 23, 59, 59)
    start_posix = calendar.timegm(start_datetime.timetuple())
    end_posix = calendar.timegm(end_datetime.timetuple())
    return (start_posix, end_posix)


@utils.invalid_input_decorator
def get_datetime_date(string_date):
    month_day_year_tuple = tuple(string_date.split('-'))
    month = int(month_day_year_tuple[1])
    day = int(month_day_year_tuple[2])
    year = int(month_day_year_tuple[0])
    return datetime.date(year, month, day)


@utils.invalid_input_decorator
def get_stories_and_pages(string_date, page_num):
    start_and_end_posix = get_start_and_end_posix(string_date)
    start_posix = start_and_end_posix[0]
    end_posix = start_and_end_posix[1]
    stories_and_pages = get_stories_and_pages_with_bounds(start_posix, end_posix, page_num)
    stories = stories_and_pages[0]
    num_pages = stories_and_pages[1]
    return (stories, num_pages)


def get_days_ago_str(datetime_date):
    days_ago_delta = datetime.date.today() - datetime_date
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


def get_random_date():
    today = datetime.date.today()
    first_date = datetime.date(2006, 10, 9)
    return get_random_date_bounded(first_date, today)


@app.route('/')
def index():
    today_date = datetime.date.today()
    string_date = request.args.get('date')
    if string_date is None:
        return redirect("/?date={}".format(today_date.isoformat()))
    elif string_date == "random":
        string_date = get_random_date().isoformat()
        return redirect("/?date={}".format(string_date))

    date_split = string_date.split("-")
    date_components = len(date_split)
    if date_components == 1:
        prev_string = int(string_date) - 1
        next_string = int(string_date) + 1
        curr_formatted = string_date
        days_ago_str = get_years_ago_str(today_date.year - int(string_date))
    elif date_components == 2:
        # prev_string = int(string_date) - 1
        # next_string = int(string_date) + 1
        # curr_formatted = string_date
        # days_ago_str = get_years_ago_str(today_date.year - int(string_date))
        pass
    elif date_components == 3:
        datetime_date = get_datetime_date(string_date)
        next_day_datetime = datetime_date + datetime.timedelta(days=1)
        next_string = next_day_datetime.isoformat()
        prev_day_datetime = datetime_date - datetime.timedelta(days=1)
        prev_string = prev_day_datetime.isoformat()
        curr_formatted = "{:%b %d, %Y}".format(datetime_date)
        days_ago_str = get_days_ago_str(datetime_date)

    page_num = request.args.get('p')
    if page_num is None:
        page_num = 0
    else:
        page_num = int(page_num)

    stories_and_pages = get_stories_and_pages(string_date, page_num)
    stories = stories_and_pages[0]
    num_pages = stories_and_pages[1]

    if page_num < num_pages - 1:
        next_page_num = page_num + 1
    else:
        next_page_num = None
    return render_template('show_posts.html',
                           stories=stories,
                           page_num=page_num,
                           next_page_num=next_page_num,
                           prev_string=prev_string,
                           next_string=next_string,
                           curr_day_formatted=curr_formatted,
                           days_ago=days_ago_str)
