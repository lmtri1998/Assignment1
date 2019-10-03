from flask import Flask, jsonify, abort
import pandas as pd

app = Flask(__name__)


# sample code for loading the team_info.csv file into a Pandas data frame.  Repeat as
# necessary for other files
def load_teams_data():
    td = pd.read_csv("./team_info.csv")
    return td

def load_player_info_data():
    pid = pd.read_csv("./player_info.csv")
    return pid

def load_game_plays_data():
    gpd = pd.read_csv("./game_plays.csv")
    return gpd

def load_game_teams_stat_data():
    gts = pd.read_csv("./game_teams_stats.csv")    
    return gts

def load_game_data():
    gd = pd.read_csv("./game.csv")
    return gd
    
#global variables
team_data = load_teams_data()
player_info = load_player_info_data()
game_plays = load_game_plays_data()
game_teams_stat = load_game_teams_stat_data()
game_data = load_game_data()
print(team_data)
print(player_info)
print(game_plays)
print(game_teams_stat)
print(game_data)
print("successfully loaded teams data")


@app.route('/')
def index():
    return "NHL API"

# Game Result Details
@app.route('/api/results/<int:game_id>/teams', methods=['GET'])
def get_result_details(game_id):
    # fetch sub dataframe for two teams in the game
    teams = game_teams_stat[game_teams_stat["game_id"] == "game_id"]
    # return 404 if there isn't one team ß
    if teams.shape[0] < 1:
        abort(404)
    
    # get the two team 
    team1 = teams.iloc[0]
    team2 = teams.iloc[1]

    team_info1 = team_data[team_data['team_id'] == team1['team_id']]
    team_info2 = team_data[team_data['team_id'] == team2['team_id']]

    team_1_stats_json = {
        "abbreviation": team_info1["abbreviation"],
        "city": team_info1["shortName"],
        "name": team_info1["teamName"],
        "home or away" : team1["HoA"],
        "won" : team1["won"],
        "settled in": team1["settled_in"],
        "goals": team1["goals"],
        "shots": team1["shots"],
        "hits": team1["hits"],
        "penalty minutes": team1["pim"],
        "power play opportunities": team1["powerPlayOpportunities"],
        "power play goals": team1["powerPlayGoals"],
        "face off win percentage": team1["faceOffWinPercentage"],
        "give aways": team1["giveaways"],
        "take aways": team1["takeaways"]
    }
    team_2_stats_json = {
        "abbreviation": team_info2["abbreviation"],
        "city": team_info2["shortName"],
        "name": team_info2["teamName"],
        "home or away" : team2["HoA"],
        "won" : team2["won"],
        "settled in": team2["settled_in"],
        "goals": team2["goals"],
        "shots": team2["shots"],
        "hits": team2["hits"],
        "penalty minutes": team2["pim"],
        "power play opportunities": team2["powerPlayOpportunities"],
        "power play goals": team2["powerPlayGoals"],
        "face off win percentage": team2["faceOffWinPercentage"],
        "give aways": team2["giveaways"],
        "take aways": team2["takeaways"]
    }
    teamsJSON = [team_1_stats_json, team_2_stats_json]

    return jsonify(teamsJSON)

# game player stats
@app.route('/api/results/<int:game_id>/players', methods=['GET'])
def get_result_players(game_id):
    


# route mapping for HTTP GET on /api/schedule/TOR
@app.route('/api/teams/<string:team_id>', methods=['GET'])
def get_task(team_id):
    # fetch sub dataframe for all teams (hopefully 1) where abbreviation=team_id
    teams = team_data[team_data["abbreviation"] == "team_id"]

    # return 404 if there isn't one team
    if teams.shape[0] < 1:
        abort(404)

    # get first team
    team = teams.iloc[0]

    # return customized JSON structure in lieu of Pandas Dataframe to_json method
    teamJSON = {"abbreviation": team["abbreviation"],
                "city": team["shortName"],
                "name": team["teamName"]}

    # jsonify easly converts maps to JSON strings
    return jsonify(teamJSON)


if __name__ == '__main__':
    app.run(debug=True)
