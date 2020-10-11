#! .\.venv\scripts\python.exe

import os.path
import time
import json
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
sns.set(style='ticks', context='talk')

BASE_URL = 'https://www.autoscout24.nl/lst?offer=U&cy=NL&'
YEAR_RANGE = (1990, 2020)
COLORS = {'beige': 1, 'blue': 2, 'brown': 3, 'darkgoldenrod': 4, 'yellow': 5, 'grey': 6, 'green': 7,
          'red': 10, 'black': 11, 'silver': 12, 'purple': 13, 'white': 14, 'orange': 15, 'gold': 16}


def scrape_color_count(color_id, year):
    url = BASE_URL + f'bcol={color_id}&fregform={year}&fregto={year}'
    request = requests.get(url)
    soup = BeautifulSoup(request.content, 'html.parser')
    search_results = soup.find('span', {'class': 'cl-filters-summary-counter'})
    return int(''.join(filter(str.isdigit, search_results.text)))


def scrape_data(start_year, end_year):
    colors_dict = {}
    for color, color_id in COLORS.items():
        colors_dict[color] = {}
        for year in range(start_year, end_year+1):
            try:
                color_count = scrape_color_count(color_id, year)
                colors_dict[color][year] = color_count
            except Exception as e:
                print(e)
            time.sleep(1)
            print(color, year)

    with open('temp.json', 'w') as f:
        json.dump(colors_dict, f)


def load_data():
    if os.path.isfile('temp.json'):
        with open('temp.json', 'r') as f:
            return json.load(f)
    else:
        return scrape_data(YEAR_RANGE[0], YEAR_RANGE[1])


def process_data(colors_dict):
    df = pd.DataFrame(colors_dict)

    # Combine similar colors
    df['brown'] = df['brown'] + df['bronze']
    df['grey'] = df['grey'] + df['silver']
    df['yellow'] = df['yellow'] + df['gold']
    df.drop(['bronze', 'silver', 'gold'], axis=1, inplace=True)
    df_scaled = df.div(df.sum(axis=1), axis=0) * 100
    df_scaled = df_scaled[df_scaled.sum().sort_values(ascending=False).index]
    return df_scaled


def create_plot(data):
    # Create figure and axis
    fig, ax = plt.subplots()
    fig.set_size_inches(16, 8)

    # Prepare plot data
    x = data.index.values
    y = data.T
    colors = ['#adadad', '#1c1c1c', '#1678e0', '#e02a16', '#f7f7f7', '#2ac41b',
              '#f7f5cb', '#f0e83e', '#47462e', '#ffc400', '#af1df2']  # or colors = data.columns

    # Create Stackplot
    ax.stackplot(x, y, colors=colors, edgecolor='none')

    # Set limits
    ax.set_xlim(['1990', '2020'])
    ax.set_ylim([0, 100])

    # Format labels and titles
    plt.title('Colors of Cars in The Netherlands',
              fontsize=22, fontweight='bold')
    plt.xlabel('Year of Production', fontsize=14)
    plt.xticks(rotation=45)
    ax.tick_params(labelright=True)
    ax.yaxis.set_ticks_position('both')
    ax.yaxis.set_major_formatter(PercentFormatter())

    # Save and show figure
    plt.tight_layout()
    plt.savefig('car_colors.png', dpi=600)
    plt.show()


if __name__ == "__main__":
    colors_dict = load_data()
    df = process_data(colors_dict)
    create_plot(df)
