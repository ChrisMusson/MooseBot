import requests


def get_provisional_bonus(gw_matches, only_live_matches, top_n):
    # takes a response from fixtures endpoint as input
    all_bonus = []
    for match in gw_matches:
        condition = (
            match["started"]
            if not only_live_matches
            else (match["started"] and not match["finished"])
        )

        match_bonus = []
        if condition:
            bps_stats = [x for x in match["stats"] if x["identifier"] == "bps"][0]
            all_players = bps_stats["h"] + bps_stats["a"]
            all_players = sorted(all_players, key=lambda x: x["value"], reverse=True)

            if not top_n:  # just return the people who score >= 1 bonus
                bps = 3
                while bps >= 1:
                    top_bonus = [
                        x for x in all_players if x["value"] == all_players[0]["value"]
                    ]
                    n = len(top_bonus)
                    for player in top_bonus:
                        # bonus[player["element"]] = bps
                        match_bonus.append(
                            {
                                "id": player["element"],
                                "baps": player["value"],
                                "bonus": bps,
                            }
                        )

                    all_players = all_players[n:]
                    bps -= n

            else:
                bps = 3
                while len(match_bonus) < top_n:
                    top_bonus = [
                        x for x in all_players if x["value"] == all_players[0]["value"]
                    ]
                    n = len(top_bonus)
                    for player in top_bonus:
                        match_bonus.append(
                            {
                                "id": player["element"],
                                "baps": player["value"],
                                "bonus": bps,
                            }
                        )

                    all_players = all_players[n:]
                    bps = max(0, bps - n)
                match_bonus = match_bonus[:top_n]
            all_bonus.append({"id": match["id"], "bonus": match_bonus})

    return all_bonus


def get_bonus_strings(fixtures_data, name_map, team_map, only_live_matches, top_n=None):
    strings = []
    bps = get_provisional_bonus(fixtures_data, only_live_matches, top_n)
    for match in bps:
        match_string = ""
        fixture = [x for x in fixtures_data if x["id"] == match["id"]][0]
        goals = [x for x in fixture["stats"] if x["identifier"] == "goals_scored"][0]
        own_goals = [x for x in fixture["stats"] if x["identifier"] == "own_goals"][0]
        gw = fixture["event"]

        h_goals = sum(map(lambda x: x["value"], goals["h"])) + sum(
            map(lambda x: x["value"], own_goals["a"])
        )
        a_goals = sum(map(lambda x: x["value"], goals["a"])) + sum(
            map(lambda x: x["value"], own_goals["h"])
        )
        scoreline = f"{team_map[fixture['team_h']]} {h_goals}-{a_goals} {team_map[fixture['team_a']]}"
        match_string += f"GW {gw}: {scoreline}"

        for player in match["bonus"]:
            line = f"{player['bonus']} - {name_map[player['id']]} ({player['baps']})"
            match_string += f"\n{line}"

        strings.append(match_string)

    return strings


def bonus(gameweek, team, only_live_matches):
    static_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
    all_strings = []

    with requests.Session() as s:
        static_data = s.get(static_url).json()

        if not gameweek:
            current = [x for x in static_data["events"] if x["is_current"]]
            if current:
                gameweeks = [current[0]["id"]]
            else:
                previous = [x for x in static_data["events"] if x["is_previous"]]
                gameweeks = [previous[0]["id"]]
        else:
            gameweeks = [int(x) for x in gameweek.split(",")]

        name_map = {x["id"]: x["web_name"] for x in static_data["elements"]}
        team_map = {x["id"]: x["name"] for x in static_data["teams"]}
        team_abbrev_map = {x["id"]: x["short_name"] for x in static_data["teams"]}

        for gw in gameweeks:
            fixture_url = f"https://fantasy.premierleague.com/api/fixtures/?event={gw}"
            fixtures_data = s.get(fixture_url).json()

            if team:
                teams = [x.upper() for x in team.split("|")]
                fixtures_data = [
                    x
                    for x in fixtures_data
                    if team_abbrev_map[x["team_h"]] in teams
                    or team_abbrev_map[x["team_a"]] in teams
                ]

            all_strings += get_bonus_strings(
                fixtures_data, name_map, team_map, only_live_matches
            )

    s = ""
    for output in all_strings:
        s += output
        s += "\n\n"

    return s
