import time
from datetime import datetime

import requests


def get_price_changes():
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    with requests.Session() as s:
        orig = s.get(url).json()
        orig_prices = {x["id"]: x["now_cost"] for x in orig["elements"]}
        orig_prices = dict(
            sorted(orig_prices.items(), key=lambda x: x[1], reverse=True)
        )
        names = {x["id"]: x["web_name"] for x in orig["elements"]}

        while True:
            new = s.get(url).json()
            if new != orig:
                break
            else:
                print("sleeping", datetime.now())
                time.sleep(0.2)

        new_prices = {x["id"]: x["now_cost"] for x in new["elements"]}

        rises = [x for x in orig_prices if orig_prices[x] < new_prices[x]]
        falls = [x for x in orig_prices if orig_prices[x] > new_prices[x]]

    s = ""
    s += "\nRISES\n"
    for player in rises:
        s += f"{names[player]} : {orig_prices[player] / 10} -> {new_prices[player] / 10}\n"

    s += "\nFALLS\n"
    for player in falls:
        s += f"{names[player]} : {orig_prices[player] / 10} -> {new_prices[player] / 10}\n"

    return f"```{s}```"
