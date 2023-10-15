from flask import Flask, redirect, render_template, render_template_string
import time
from bs4 import BeautifulSoup
from requests import get



app = Flask(__name__)

waiting_interval = 5
clean = "<script>document.body.innerHTML = '';</script>"

@app.route('/<match_id>/<match_name>')
def match(match_id, match_name):
    if not any([match_id, match_name]):
        return "Please provide a cricbuzz url"
    
    cricbuzz_url = f"https://www.cricbuzz.com/live-cricket-scores/{match_id}/{match_name}"
    def gen():
        with app.app_context():
            yield render_template("scorecard.html")
        while True:
            try:
                html_data = get(cricbuzz_url).text
                soup = BeautifulSoup(html_data, 'html.parser')
                try:
                    x = soup.find('div', class_='cb-min-bat-rw').text.strip()
                except AttributeError:
                    try:
                        x = soup.find('div', class_='cb-min-stts').text.strip()
                        yield clean
                        yield x
                        return 
                    except AttributeError:
                        try:
                            x = soup.find('div', class_='cb-scrcrd-status').text.strip()
                            yield clean
                            yield x
                            return
                        except AttributeError:
                            yield clean
                            yield "Match not started yet"
                            return
                team_playing = x.split(' ')[0].strip()
                team1, team2 = match_name.split("-vs-")
                team2 = team2.split("-")[0].upper()
                team1 = team1.upper()
                if team_playing == team1:
                    other_team = team2
                else:
                    other_team = team1
                print(team1,team2)
                runs,wickets = x.split(' ')[1].split("/")
                if "." in x.split(' ')[2]:
                    over,ball = x.split(' ')[2].split(".")
                    ball = ball.replace(")","")
                else:
                    over = x.split(' ')[2]
                    ball = 0
                over = over.replace("(","")
                over = over.replace(")","")
                batsmans = soup.find_all('div', class_='cb-col cb-col-50')
                batsman_1 = batsmans[1].text.strip()
                batsman_2 = batsmans[2].text.strip()
                if batsman_2.lower() == "bowler":
                    batsman_2 = ""
                b1_runs = batsmans[1].parent.find_all("div")[1].text.strip()
                b1_balls = batsmans[1].parent.find_all("div")[2].text.strip()
                if batsman_2:
                    b2_runs = batsmans[2].parent.find_all("div")[1].text.strip()
                    b2_balls = batsmans[2].parent.find_all("div")[2].text.strip()
                    b2_balls = f"({b2_balls})"
                else:
                    b2_runs = ""
                    b2_balls = ""

                bowler = batsmans[-2].text.strip()
                bowler_overs = batsmans[-2].parent.find_all("div")[1].text.strip()
                bowler_maidens = batsmans[-2].parent.find_all("div")[2].text.strip()
                bowler_runs = batsmans[-2].parent.find_all("div")[3].text.strip()
                bowler_wickets = batsmans[-2].parent.find_all("div")[4].text.strip()
                bowler_eco = batsmans[-2].parent.find_all("div")[5].text.strip()
                over_recent = soup.find('div', class_='cb-col cb-col-100 cb-font-12 cb-text-gray cb-min-rcnt').text.strip()
                over_recent = over_recent.split("|")[-1]
                over_recent = over_recent.replace(" ", "  ")
                #function update_data(b1_name, b2_name, b1_runs, b1_balls, b2_runs, b2_balls, other_team, team_playing, runs, wickets, over, ball, bowler, over_recent, bowler_wickets, bowler_runs) {
                to_yield = f"<script>update_data('> {batsman_1}', '  {batsman_2}', '{b1_runs}', '{b1_balls}', '{b2_runs}', '{b2_balls}', '{other_team}', '{team_playing}', '{runs}', '{wickets}', '{over}', '{ball}', '{bowler}', '{over_recent}', '{bowler_wickets}', '{bowler_runs}', '{bowler_overs}', '{bowler_maidens}', '{bowler_eco}')</script>"
                yield to_yield

                print(to_yield)
                for x in range(waiting_interval):
                    print(f"waiting for another {waiting_interval-x}") 
                    time.sleep(1)
            except GeneratorExit:
                break
    return app.response_class(gen())

@app.route("/")
def slash():
    link = "https://www.cricbuzz.com/cricket-match/live-scores"
    html = get(link).text
    soup = BeautifulSoup(html, 'html.parser')
    l = []
    for match in soup.find_all("a", class_="text-hvr-underline text-bold"):
        text = match.text.strip().replace(",", "")
        link = "/".join(match["href"].split("/")[2:])
        l.append((text,link))
    return render_template("home.html", matches=l)
    

app.run(port=6969, host="0.0.0.0")