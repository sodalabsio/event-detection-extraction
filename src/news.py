"""Google News Module"""
import pandas as pd
from GoogleNews import GoogleNews
from src.utils import to_datetime

# global constants
REGION = 'US'
ENCODING = 'utf-8'
LANG = 'en'


def normalize_date(df, year):
    """Normalize the date column"""
    df['datetime'] = df.date.apply(
        lambda x: to_datetime(x, year))
    return df


def dedup_entries(df):
    """Deduplicate entries"""
    df = df.loc[~df.duplicated(['title', 'datetime']), :]
    return df


def get_news(query: str, start_time: str, end_time: str):
    """Get news from Google News"""
    all_news = []
    # NB: make sure start_time and end_time are in the same year
    # Google News results do not indicate the year of the news
    assert start_time.split('-')[2] == end_time.split('-')[2]
    year = start_time.split('-')[2]
    # NB: reinitializing eliminates the cached results
    google_news = GoogleNews(lang=LANG,
                             encode=ENCODING,
                             region=REGION,
                             start=start_time,
                             end=end_time,
                             )
    google_news.enableException(True)
    print(google_news.getVersion())
    print(google_news.user_agent)
    google_news.get_news(query)
    results = google_news.results()
    temp_results = []
    for result in results:
        result['query'] = query
        temp_results.append(result)

    print(f"Total hits: {len(temp_results)}")
    all_news.extend(temp_results)
    df = pd.DataFrame(all_news)
    df = normalize_date(df, year)
    df = dedup_entries(df)
    return df
