#! .\.venv\scripts\python.exe

import os.path
import time
import json
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
plt.style.use('seaborn-white')

BASE_URL = 'https://www.autoscout24.nl/lst?offer=U&cy=NL&'
YEAR_RANGE = (1990, 2020)
COLORS = {'beige': 1,
          'blue': 2,
          'brown': 3,
          'darkgoldenrod': 4,  # bronze
          'yellow': 5,
          'grey': 6,
          'green': 7,
          'red': 10,
          'black': 11,
          'silver': 12,
          'purple': 13,
          'white': 14,
          'orange': 15,
          'gold': 16}


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
    ax = df_scaled.plot(kind="bar", stacked=True,
                        color=COLORS.keys(), legend=False)
    ax.set_facecolor('#e8e8e8')
    plt.xlabel('Year of Production')
    ax.yaxis.set_major_formatter(PercentFormatter())
    plt.savefig('car_colors.png', dpi=600)
    plt.show()


if __name__ == "__main__":
    colors_dict = load_data()
    create_plot(colors_dict)
