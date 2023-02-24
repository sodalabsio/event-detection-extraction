"""Main Executable"""
import time
import warnings
import argparse
import pandas as pd
from datetime import datetime

# custom imports
from src.news import get_news
# from src.twitter import get_tweets
from src.stream import create_streamgraph
from src.event import run_event_extraction
from src.utils import validate_args, check_cache, create_folder

warnings.filterwarnings("ignore")

TRUSTED_SOURCES = ['ABC News', 'The Guardian',
                   'Reuters', 'BBC', 'NPR', 'Amnesty International']

if __name__ == '__main__':
    """Main function"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', type=str, required=True,
                        help='Query to search for. Country or place full name, for example')
    parser.add_argument('--start-date', type=str, required=True,
                        help='Start date of the event in YYYY-MM-DD format')
    parser.add_argument('--end-date', type=str, required=True,
                        help='End date of the event in YYYY-MM-DD format')
    parser.add_argument('--source', type=str, default='news', choices=['news', 'twitter'],
                        required=True, help='Source of events to pull from such as news or twitter (only news is supported currently)')
    parser.add_argument('--output-path', type=str,
                        help='Output directory to write the results', required=True)
    parser.add_argument('--trusted-only', type=lambda x: (str(x).lower() == 'true'), required=False,
                        help='Whether to use trusted news sources to filter by (optional)', default=False)
    parser.add_argument('--event-confidence', type=float,
                        help='A minimum confidence threshold for events', default=0.5)
    parser.add_argument(
        '--top-k', type=int, help='The number of top events to surface based on frequency (should be less than 15)', required=False, default=10)

    args = parser.parse_args()

    tic = time.perf_counter()
    validate_args(args)

    # run name and paths
    run_name = f"{args.query}_{args.start_date}_{args.end_date}"
    news_path = f"{args.output_path}/{run_name}_news.csv"
    events_path = f"{args.output_path}/{run_name}_events.csv"
    streamgraph_path = f"{args.output_path}/{run_name}_streamgraph.html"

    # create the output dir (if it does not exist already)
    create_folder(args.output_path)

    # parse date/times
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d").date()
    start_time = f"{start_date.strftime('%m-%d-%Y')}"  # T00:00:00"
    end_time = f"{end_date.strftime('%m-%d-%Y')}"  # T23:59:59"

    # 1. run query through Google News
    print(f"==> Fetching data from {args.source} .. ")
    if check_cache(path=news_path):
        df = pd.read_csv(news_path)

    else:
        df = get_news(args.query, start_time, end_time)
        df.to_csv(news_path, index=False)

    print(f'Top {args.top_k} outlets (by frequency):')
    print(df.media.value_counts()[:args.top_k])

    # 2. run event detection
    print(
        f"==> Running event extraction with event confidence: {args.event_confidence} .. ")
    if check_cache(path=events_path):
        df = pd.read_csv(events_path)

    else:
        events = run_event_extraction(df)
        # merge events with news
        df = pd.concat([df, pd.DataFrame(events)], axis=1)
        df.to_csv(events_path, index=False)

    # 3. filter events by confidence + outlets (if applicable)
    df['date'] = df.datetime
    df['datetime'] = df.datetime.apply(lambda x: int(
        datetime.strptime(x, '%Y-%m-%d').strftime("%s")))
    df['event'] = df.event.apply(str.lower)  # case normalize all event names
    # filter by confidence
    df_sub = df.loc[df.confidence >= args.event_confidence, :]
    
    # 4. filter by trusted sources (if applicable)
    if args.trusted_only == True:
        print(f"==> Filtering by trusted sources: {', '.join(TRUSTED_SOURCES)} ..")
        df_sub = df_sub.loc[df_sub.media.isin(TRUSTED_SOURCES), :]

    # 5. sort events based on their frequency (only retain top-k)
    print(f"==> Top-{args.top_k} events:")
    top_events = df.event.groupby(df_sub.event).size().sort_values(
        ascending=False).head(args.top_k).to_dict()
    df_sub = df_sub.loc[df_sub.event.isin(
        top_events.keys()), :]  # filter by top-k events
    print(", ".join(list(top_events.keys())))

    # 6. create streamgraphs
    print(f"==> Generating streamgraph ..")
    if args.trusted_only:
        plot_title = f'Event Streamgraph for "{args.query}" from {args.start_date} to {args.end_date} (confidence >= {args.event_confidence}, trusted sources: {", ".join(TRUSTED_SOURCES)})'
    else:
        plot_title = f'Event Streamgraph for "{args.query}" from {args.start_date} to {args.end_date} (confidence >= {args.event_confidence})'
    
    create_streamgraph(df_sub, plot_title, streamgraph_path)

    print(f"==> Execution completed.")
    print(f"Total time elapsed: {time.perf_counter() - tic:0.4f} seconds.")
