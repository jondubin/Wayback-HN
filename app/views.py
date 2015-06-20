from flask import render_template, request, redirect, url_for
from app import app
import os
import json
from date_input import DateInput
from utils import (get_random_date,
                   is_valid_date,
                   get_stories_and_pages,
                   get_stories_and_pages_from_json,
                   get_todays_date)


@app.route('/')
def index():
    todays_date = get_todays_date()
    date_str = request.args.get('date', default=todays_date.isoformat())
    page_num = request.args.get('p', default=0, type=int)

    date_str_split = date_str.split('-')
    if date_str_split[0] == "random":
        random_date = get_random_date()
        if date_str_split[1] == "day":
            return redirect("/?date={}-{}-{}".format(random_date.year, random_date.month, random_date.day))
        elif date_str_split[1] == "month":
            return redirect("/?date={}-{}".format(random_date.year, random_date.month))
        elif date_str_split[1] == "year":
            return redirect("/?date={}".format(random_date.year))

    if date_str_split[0] == "current":
        if date_str_split[1] == "day":
            return redirect("/?date={}-{}-{}".format(todays_date.year, todays_date.month, todays_date.day))
        elif date_str_split[1] == "month":
            return redirect("/?date={}-{}".format(todays_date.year, todays_date.month))
        elif date_str_split[1] == "year":
            return redirect("/?date={}".format(todays_date.year))

    if not is_valid_date(date_str):
        date_str = todays_date.isoformat()
        message = "Date input is invalid, here are stories from today:"
    else:
        message = None

    print todays_date.isoformat()
    date_input = DateInput(date_str, todays_date)

    try:
        stories_and_pages = get_stories_and_pages(date_str, page_num)
    except Exception:
        message = "We had trouble fetching stories (our server might be having a rough time). " \
                  "Instead, here are stories from the first day Hacker News was online:"
        date_input = DateInput("2006-10-9", todays_date)
        with open(os.path.dirname(os.path.realpath(__file__)) + '/static/first_day.json') as json_file:
            json_response = json.load(json_file)
            stories = get_stories_and_pages_from_json(json_response)[0]
        return render_template('show_posts.html',
                                date_input=date_input,
                                stories=stories,
                                message=message,
                                page_num=1)

    stories = stories_and_pages[0]
    num_pages = stories_and_pages[1]

    if page_num < num_pages - 1:
        next_page_num = page_num + 1
        next_page_url = "?date={}&p={}".format(date_str, next_page_num)
    else:
        next_page_url = None
    
    return render_template('show_posts.html',
                           date_input=date_input,
                           stories=stories,
                           page_num=page_num,
                           next_page_url=next_page_url,
                           message=message)
