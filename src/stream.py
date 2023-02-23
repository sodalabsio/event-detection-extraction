"""Streamgraph Module"""
import mpld3
import datetime
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

# colors for the streamgraph
COLOR_MAP = ['#d73027', '#fee090', '#e0f3f8', '#abd9e9', '#4575b4','#8dd3c7', 
            '#bebada', '#d9d9d9', '#80b1d3', '#fdb462', '#b3de69', '#fccde5', 
            '#fb8072', '#bc80bd', '#ccebc5']


def gaussian_smooth(x, y, grid, sd):
    """Smooth the data using a Gaussian kernel."""
    weights = np.transpose([stats.norm.pdf(grid, m, sd) for m in x])
    weights = weights / weights.sum(0)
    return (weights * y).sum(1)


def generate_vis(x, y, event_names, plot_title, save_path):
    """Generate the streamgraph visualization."""
    # , subplot_kw=dict(facecolor='#EEEEEE'))
    fig, ax = plt.subplots(figsize=(10, 7))
    x_ = [int(str(z)[:5]) for z in x]
    grid = np.linspace(x_[0], x_[-1], num=300)
    y_smoothed = [gaussian_smooth(x_, y_, grid, 1) for y_ in y]
    stream = ax.stackplot(grid, y_smoothed, baseline="sym",
                          labels=event_names, colors=COLOR_MAP)

    labels = [label.get_text() for label in ax.xaxis.get_majorticklabels()]
    date_labels = [datetime.datetime.fromtimestamp(
        int('{:<010d}'.format(int(float(d))))).strftime("%Y-%m-%d") for d in labels]

    # set ticks values

    # ax.set_xticks([int(float(label)) for label in labels])

    # set tick labels
    ax.xaxis.set_ticklabels(date_labels)
    # ax.set_xticklabels(date_labels, rotation=90);
    ax.xaxis.set_ticks([float(label) for label in labels])

    ax.set_title(plot_title)
    # ax.legend(title="Top 10 events", loc='upper left', prop={'size': 9});
    ax.legend(title="Top events", loc='upper left', prop={'size': 9})

    fig.tight_layout()

    tooltips = []
    for i, s in enumerate(stream):
        # label = f'<div class="tooltiptext">{[event_names[i]]}</div>'
        # _labels = [f'{event_names[i]}: {k}' for k in date_labels]
        tooltip = mpld3.plugins.PointHTMLTooltip(s, labels=[event_names[i]],
                                                 hoffset=10, voffset=10,
                                                 css='.mpld3-tooltip{background-color: #fffff; padding: 8px}'
                                                 )
        mpld3.plugins.connect(fig, tooltip)

    # mpld3.enable_notebook()
    mpld3.save_html(fig, save_path)
    mpld3.display()


def create_streamgraph(df, plot_title, save_path):
    """Main streamgraph function."""
    df = df[['title', 'desc', 'date', 'datetime', 'link',
             'img', 'media', 'site', 'event', 'confidence']].copy()
    event_names = df.event.sort_values(ascending=True).unique().tolist()
    x = df.datetime.sort_values(ascending=True).unique().tolist()
    x_labels = df.date.sort_values(ascending=True).unique().tolist()
    date_map = dict(zip([int(str(z)[:5]) for z in x], x_labels))
    df['event_count'] = 1
    df_pivot = pd.pivot_table(df, values='event_count', index='datetime', columns='event',
                              aggfunc='count')
    df_pivot.fillna(0, inplace=True)
    df_pivot.reset_index(inplace=True)
    df_melt = pd.melt(df_pivot, id_vars='datetime', value_vars=event_names)
    df_melt.sort_values(['datetime', 'event'], ascending=True)

    y = []
    for event in event_names:
        counts = df_melt[df_melt.event == event].sort_values(
            ['datetime'], ascending=True).value
        y.append(np.array(counts, dtype='int64'))

    generate_vis(x, y, event_names, plot_title, save_path)
