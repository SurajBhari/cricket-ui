from flask import Flask, redirect, render_template, render_template_string, jsonify
import time
from bs4 import BeautifulSoup
from requests import get
from json import load, loads, dump, dumps



app = Flask(__name__)

waiting_interval = 5
clean = "<script>document.body.innerHTML = '';</script>"

@app.route('/<match_id>/<match_name>/')
def match(match_id, match_name):
    if not any([match_id, match_name]):
        return "Please provide a cricbuzz url"
    
    cricbuzz_url = f"https://www.cricbuzz.com/live-cricket-scores/{match_id}/{match_name}"
    # take out the flags
    html_data = get(cricbuzz_url.replace("live-cricket-scores","cricket-match-squads")).text
    soup = BeautifulSoup(html_data, 'html.parser')
    team1_flag = soup.find("a", class_="cb-team1").find("img")["src"]
    team2_flag =soup.find("a", class_="cb-team2").find("img")["src"]
    return render_template("scorecard.html", team1_flag=team1_flag, team2_flag=team2_flag, api_link="/api/"+match_id)
    
@app.route("/api/<match_id>")
def api(match_id):
    api_link = f"https://www.cricbuzz.com/api/cricket-match/commentary/{match_id}"
    data = get(api_link).json()
    toss_win_str = f"{data['matchHeader']['tossResults']['tossWinnerName']} won the toss and elected for {data['matchHeader']['tossResults']['decision']}"
    runs = data['miniscore']['batTeam']['teamScore']
    wickets = data['miniscore']['batTeam']['teamWkts']
    bwlr = data['miniscore']['bowlerStriker']
    bowler = bwlr['bowlName'].split(" ")[-1]
    bowler_wickets = bwlr['bowlWkts']
    bowler_runs = bwlr['bowlRuns']
    bowler_overs = bwlr['bowlOvs']
    bowler_maidens = bwlr['bowlMaidens']
    bowler_eco = bwlr['bowlEcon']
    b1 = data['miniscore']['batsmanStriker']
    b2 = data['miniscore']['batsmanNonStriker']
    t1 = data['matchHeader']['matchTeamInfo'][-1]['bowlingTeamShortName']
    t2 = data['matchHeader']['matchTeamInfo'][-1]['battingTeamShortName']
    batsman_1 = b1['batName'].split(" ")[-1]
    batsman_2 = b2['batName'].split(" ")[-1]
    b1_runs = b1['batRuns']
    b1_balls = b1['batBalls']
    b2_runs = b2['batRuns']
    b2_balls = b2['batBalls']
    other_team = t1
    team_playing = t2
    over = data['miniscore']['overs']
    over_recent = data['miniscore']['recentOvsStats'].split("|")[-1]
    try:
        target = data['miniscore']['target']
    except KeyError:
        target = 0
    if target:
        if runs >= target:
            need_string = f'{team_playing} Won.'
        else:
            need_string = f'{team_playing} needs {target - runs} runs to win.'
    else:
        need_string = ""
    data = {
        "toss_win_str": toss_win_str,
        "runs": runs,
        "wickets": wickets,
        "bowler": bowler,
        "bowler_wickets": bowler_wickets,
        "bowler_runs": bowler_runs,
        "bowler_overs": bowler_overs,
        "bowler_maidens": bowler_maidens,
        "bowler_eco": bowler_eco,
        "batsman_1": batsman_1,
        "batsman_2": batsman_2,
        "b1_runs": b1_runs,
        "b1_balls": b1_balls,
        "b2_runs": b2_runs,
        "b2_balls": b2_balls,
        "other_team": other_team,
        "team_playing": team_playing,
        "over": over,
        "over_recent": over_recent,
        "target": target,
        "need_string": need_string
    }
    return jsonify(data)    

@app.route("/")
def slash():
    link = "https://www.cricbuzz.com/cricket-match/live-scores"
    html = get(link).text
    soup = BeautifulSoup(html, 'html.parser')
    l = []
    for match in soup.find_all("a", class_="text-hvr-underline text-bold"):
        text = match.text.strip().replace(",", "")
        link = "/".join(match["href"].split("/")[2:]) + "/"
        l.append((text,link))
    return render_template("home.html", matches=l)
    

app.run(port=6969, host="0.0.0.0", debug=True)