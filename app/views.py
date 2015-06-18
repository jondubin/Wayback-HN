from flask import render_template, request, redirect
from app import app
import datetime
from date_input import DateInput
from utils import (get_random_date,
                   is_valid_date,
                   get_years_ago_str,
                   get_datetime_date,
                   get_days_ago_str,
                   get_stories_and_pages)


@app.route('/')
def index():
    todays_date = datetime.date.today()
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


    if is_valid_date(date_str):
        is_valid_input = True
    else:
        is_valid_date(date_str)
        date_str = todays_date.isoformat()
        is_valid_input = False

    date_input = DateInput(date_str, todays_date)
    stories_and_pages = get_stories_and_pages(date_str, page_num)

    stories = stories_and_pages[0]
    num_pages = stories_and_pages[1]

    if page_num < num_pages - 1:
        next_page_num = page_num + 1
    else:
        next_page_num = None

    return render_template('show_posts.html',
                           date_input=date_input,
                           stories=stories,
                           page_num=page_num,
                           next_page_num=next_page_num,
                           is_valid_input=is_valid_input)
