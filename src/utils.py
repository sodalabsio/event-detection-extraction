import os
import datetime
from datetime import datetime
from dateutil.parser import parse


def create_folder(path):
    """Create a folder if it does not exist already."""
    if not os.path.exists(path):
        os.makedirs(path)


def is_valid_date(date):
    """Check if the date is in proper format."""
    if date:
        try:
            parse(date)
            return True
        except:
            return False
    return False


def validate_args(args):
    """Validate the arguments passed to the script."""
    if args.event_confidence < 0 or args.event_confidence > 1:
        raise ValueError("Event confidence must be between 0 and 1.")

    if args.top_k > 15:
        raise ValueError("Top-k must be less than 15.")

    if not (is_valid_date(args.start_date) and is_valid_date(args.end_date)):
        raise ValueError(
            "Start date and end date must be in proper YYYY-MM-DD format.")

    if datetime.strptime(args.start_date, "%Y-%m-%d").date() >= datetime.strptime(args.end_date, "%Y-%m-%d").date():
        raise ValueError("Start date must be before end date.")


def check_cache(path):
    """Check if the file exists in the cache."""
    if os.path.exists(path):
        print(f"==> File: {path} exists .. loading from cache .. ")
        return True
    else:
        print(f"==> File: {path} does not exist .. running .. ")
        return False


def to_datetime(date_str, year):
    """Convert a date string to a datetime object. Handle the `date_str` 
    both including/excluding the year.
    """
    # check if for example, if `date_str` has Sept instead of Sept and apply fix accordingly
    comps = date_str.split()
    # NB: assuming month always comes in second position
    comps[1] = comps[1][:3]
    date_str = ' '.join(comps)
    try:
        return datetime.strptime(f'{date_str} {year}', '%d %b %Y').strftime('%Y-%m-%d')

    except Exception as e:
        return datetime.strptime(f'{date_str}', '%d %b %Y').strftime('%Y-%m-%d')
