from flask import render_template, request
from app import app
# from __init__ import get_stories_around_time
# from __init__ import get_time_years_ago
import calendar
import datetime
import requests
import pprint

pp = pprint.PrettyPrinter(indent=4)


# def unix_time(dt):
#     epoch = datetime.utcfromtimestamp(0)
#     delta = dt - epoch
#     return delta.total_seconds()


# def get_time_years_ago():
#     today = datetime.today()
#     today_year = today.year
#     old_year = today_year - 8
#     eight_years_ago = today.replace(year=old_year)
#     return unix_time(eight_years_ago)


# def get_json_from_page(time, page_number):
#     SECONDS_IN_DAY = 86400
#     base_url = "http://hn.algolia.com/api/v1/search?tags=story&"
#     end_time = time
#     start_time = time - SECONDS_IN_DAY
#     date_filter_url = "numericFilters=created_at_i>{0},created_at_i<{1}".format(start_time, end_time)
#     page_query = "&page={}".format(page_number)
#     r = requests.get(base_url + date_filter_url + page_query)
#     json_response = r.json()
#     return json_response


def find_segment_with_period(segment_list):
    for segment in segment_list:
        if "." in segment:
            return segment


def get_sitebit(url):
    print url
    split_by_slashes = (url).split("/")
    print split_by_slashes
    segment = find_segment_with_period(split_by_slashes)
    split_by_periods = (segment).split(".")
    sitebit = ".".join(split_by_periods[-2:])
    return sitebit


# def get_stories_around_time(time):
#     stories = []
#     first_page = get_json_from_page(time, 0)
#     num_pages = first_page["nbPages"]
#     for page_number in range(0, num_pages + 1):
#         json_response = get_json_from_page(time, page_number)
#         for story in json_response["hits"]:
#             del story["_highlightResult"]
#             print story["url"]
#             if story["url"]:
#                 story["sitebit"] = get_sitebit(story["url"])
#             else:
#                 story["url"] = "https://news.ycombinator.com/item?id={}".format(story["objectID"])
#             pp.pprint(story)
#             stories.append(story)
#     return stories


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


def get_start_and_end_posix(string_date):
    month_day_year_tuple = tuple(string_date.split('-'))
    month = int(month_day_year_tuple[1])
    day = int(month_day_year_tuple[2])
    year = int(month_day_year_tuple[0])
    start_datetime = datetime.datetime(year, month, day, 0, 0, 0)
    end_datetime = datetime.datetime(year, month, day, 23, 59, 59)
    start_posix = calendar.timegm(start_datetime.timetuple())
    end_posix = calendar.timegm(end_datetime.timetuple())
    return (start_posix, end_posix)


def get_datetime_date(string_date):
    month_day_year_tuple = tuple(string_date.split('-'))
    month = int(month_day_year_tuple[1])
    day = int(month_day_year_tuple[2])
    year = int(month_day_year_tuple[0])
    return datetime.date(year, month, day)


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


@app.route('/')
def index():
    string_date = request.args.get('date')
    if string_date is None:
        string_date = datetime.date.today().isoformat()
    datetime_date = get_datetime_date(string_date)
    next_day_datetime = datetime_date + datetime.timedelta(days=1)
    next_day_string = next_day_datetime.isoformat()
    prev_day_datetime = datetime_date - datetime.timedelta(days=1)
    prev_day_string = prev_day_datetime.isoformat()

    curr_day_formatted = "{:%b %d, %Y}".format(datetime_date)

    page_num = request.args.get('p')
    if page_num is None:
        page_num = 0
    else:
        page_num = int(page_num)
    stories_and_pages = get_stories_and_pages(string_date, page_num)
    stories = stories_and_pages[0]
    num_pages = stories_and_pages[1]
    days_ago_str = get_days_ago_str(datetime_date)
    if page_num < num_pages - 1:
        next_page_num = page_num + 1
    else:
        next_page_num = None
    return render_template('base.html',
                           stories=stories,
                           page_num=page_num,
                           next_page_num=next_page_num,
                           prev_day_string=prev_day_string,
                           next_day_string=next_day_string,
                           curr_day_formatted=curr_day_formatted,
                           days_ago=days_ago_str)
