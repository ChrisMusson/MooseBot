import time
from datetime import datetime

import requests


def fetch(session, url):
    while True:
        try:
            r = session.get(url)
            if r.status_code == 200:
                return r.json()
            else:
                time.sleep(0.5)
        except Exception:
            time.sleep(0.5)
            continue


def get_price_changes():
    url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    with requests.Session() as s:
        orig = fetch(s, url)
        orig_prices = {x["id"]: x["now_cost"] for x in orig["elements"]}
        orig_prices = dict(
            sorted(orig_prices.items(), key=lambda x: x[1], reverse=True)
        )
        names = {x["id"]: x["web_name"] for x in orig["elements"]}

        while True:
            new = fetch(s, url)
            if new != orig:
                break
            else:
                print("sleeping", datetime.now())
                time.sleep(1)

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


if __name__ == "__main__":
    get_price_changes()
