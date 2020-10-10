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
sns.set_style(style='ticks')

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


def create_plot(colors_dict):
    df = pd.DataFrame(colors_dict)
    df_scaled = df.div(df.sum(axis=1), axis=0) * 100

    colors = COLORS.keys()
    fig, ax = plt.subplots()
    fig.set_size_inches(20, 10)
    ax.stackplot(df_scaled.index.values, df_scaled.T,
                 colors=colors, labels=df_scaled.columns)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc='upper right')
    ax.set_facecolor('#f2f2f2')
    # ax = df_scaled.plot(kind='bar', stacked=True,
    #                     color=COLORS.keys(), figsize=(20, 10))
    # ax.legend(bbox_to_anchor=(1.1, 1.05))
    ax.set_xlim(['1990', '2020'])
    plt.xticks(rotation=45)
    ax.set_ylim([0, 100])
    plt.title('Colors of Cars in The Netherlands by Production Year', fontsize=18)
    plt.xlabel('Year of Production', fontsize=14)
    ax.yaxis.set_major_formatter(PercentFormatter())
    plt.tight_layout()
    plt.savefig('car_colors.png', dpi=600)
    plt.show()


if __name__ == "__main__":
    colors_dict = load_data()
    create_plot(colors_dict)
