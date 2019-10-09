from flask import Flask, jsonify, abort, request
import pandas as pd
import re

app = Flask(__name__)


# sample code for loading the team_info.csv file into a Pandas data frame.  Repeat as
# necessary for other files
def load_teams_data():
    td = pd.read_csv("./team_info.csv")
    return td

def load_player_info_data():
    pid = pd.read_csv("./player_info.csv")
    return pid

def load_skaters_data():
    skaters = pd.read_csv("./game_skater_stats.csv")
    return skaters

def load_goalies_data():
    goalies = pd.read_csv("./game_goalie_stats.csv")
    return goalies

def load_game_teams_stat_data():
    gts = pd.read_csv("./game_teams_stats.csv")    
    return gts

def load_game_data():
    gd = pd.read_csv("./game.csv")
    return gd

def load_game_plays_data():
    gpd = pd.read_csv("./game_plays.csv")
    return gpd

def load_game_plays_players_data():
    gppd = pd.read_csv("./game_plays_players.csv")
    return gppd

#global variables
team_data = load_teams_data()
player_info = load_player_info_data()
game_teams_stat = load_game_teams_stat_data()
game_data = load_game_data()
skaters_data = load_skaters_data()
goalies_data = load_goalies_data()
game_plays_data = load_game_plays_data()
game_plays_players_data = load_game_plays_players_data()
# print(team_data)
# print(player_info)
# print(game_plays)
# print(game_teams_stat)
# print(game_data)
print("successfully loaded teams data")

# Helper function
def won_bool(b):
    if(b):
        return "Yes"
    else:
        return "No"

def get_time_format(time):
    m, s = divmod(time, 60)
    return f'{m:02d}:{s:02d}'

def get_period(p):
    if(p == 1):
        return '1st'
    elif(p == 2):
        return '2nd'
    elif(p == 3):
        return '3rd'
    else:
        return '4th'

def get_current_season_score(des, last_name):
    des_list = des.split(" ")
    name_split = last_name.split(" ")
    index = des_list.index(name_split[len(name_split) - 1])
    if (index + 1 < len(des_list)):
        return des_list[index + 1]
    else:
        abort(404)


@app.route('/')
def index():
    return "NHL API"

# Game Result Summary 
@app.route('/api/results', methods=['GET'])
def get_result_summary(): 
    date = request.args.get('date')
    games = game_data[game_data["date_time"] == date]
    
    # return 404 if there is no game
    if games.shape[0] < 1:
        abort(404)
    

    final_table = games.merge(team_data, left_on="away_team_id", right_on="team_id").merge(team_data, left_on="home_team_id", right_on="team_id", suffixes=("_away", "_home"))
    gamesJSON = []
    for index, row in final_table.iterrows():
        gamesJSON.append({
            "date" : row['date_time'],
            "home_name" : row['abbreviation_home'],
            "home_score" : row['home_goals'],
            "away_name" : row['abbreviation_away'],
            "away_score" : row['away_goals'],
            "outcome" : row['outcome'],
            "type" : row['type'],
            "venue" : row['venue']
        })

    return jsonify(gamesJSON)

# Game Result Details
@app.route('/api/results/<int:game_id>/teams', methods=['GET'])
def get_result_details(game_id):
    # fetch sub dataframe for two teams in the game
    teams = game_teams_stat[game_teams_stat["game_id"] == game_id]
        
    # return 404 if there isn't 2 team ß
    if teams.shape[0] < 2:
        abort(404)
    
    # get the two team 
    team1 = teams.iloc[0]
    team2 = teams.iloc[1]

    team_info1 = team_data[team_data['team_id'] == team1['team_id']]
    team_info2 = team_data[team_data['team_id'] == team2['team_id']]

    # return 404 if there isn't a team from the team_info list
    if team_info1.shape[0] < 1:
        abort(404)

    if team_info2.shape[0] < 1:
        abort(404)

    team_info1_name = team_info1.iloc[0]["abbreviation"]
    team_info2_name = team_info2.iloc[0]["abbreviation"]
    teamsJSON = []
    team_1_stats_json = {
        "abbreviation": team_info1_name,
        "home_or_away": team1["HoA"],
        "won": won_bool(team1["won"]),
        "settled_in": team1["settled_in"],
        "goals": team1["goals"].item(),
        "shots": team1["shots"].item(),
        "hits": team1["hits"].item(),
        "penalty_minutes": team1["pim"].item(),
        "power_play_opportunities": team1["powerPlayOpportunities"].item(),
        "power_play_goals": team1["powerPlayGoals"].item(),
        "face_off_win_percentage": team1["faceOffWinPercentage"].item(),
        "give_aways": team1["giveaways"].item(),
        "take_aways": team1["takeaways"].item()
    }
    team_2_stats_json = {
        "abbreviation": team_info2_name,
        "home_or_away": team2["HoA"],
        "won": won_bool(team2["won"]),
        "settled_in": team2["settled_in"],
        "goals": team2["goals"].item(),
        "shots": team2["shots"].item(),
        "hits": team2["hits"].item(),
        "penalty_minutes": team2["pim"].item(),
        "power_play_opportunities": team2["powerPlayOpportunities"].item(),
        "power_play_goals": team2["powerPlayGoals"].item(),
        "face_off_win_percentage": team2["faceOffWinPercentage"].item(),
        "give_aways": team2["giveaways"].item(),
        "take_aways": team2["takeaways"].item()
    }
    teamsJSON.append(team_1_stats_json)
    teamsJSON.append(team_2_stats_json)

    return jsonify(teamsJSON)

# game player stats
@app.route('/api/results/<int:game_id>/players', methods=['GET'])
def get_result_players(game_id):
    # fetch sub dataframe for all skaters
    skaters = skaters_data[skaters_data["game_id"] == game_id]
    goalies = goalies_data[goalies_data["game_id"] == game_id]

    # return 404 if there is no skaters or goalies
    if skaters.shape[0] < 1:
        abort(404)

    if goalies.shape[0] < 1:
        abort(404)

    skaters_with_infos = skaters.set_index('player_id').join(player_info.set_index('player_id'))
    goalies_with_infos = goalies.set_index('player_id').join(player_info.set_index('player_id'))

    # do a loop here
    playersJSON = {
        "Skaters": skaters_with_infos.to_dict(orient='records'),
        "Goalies": goalies_with_infos.to_dict(orient='records')
    }

    return jsonify(playersJSON)

# Scoring timeline
@app.route('/api/results/<int:game_id>/scoringsummary', methods=['GET'])
def get_scoring_summary(game_id):
    game_plays = game_plays_data[game_plays_data['game_id'] == game_id]
    # return 404 if no play was found
    if game_plays.shape[0] < 1:
        abort(404)

    game_plays_with_teams = game_plays.merge(team_data, left_on="team_id_for", right_on="team_id").merge(team_data, left_on="team_id_against", right_on="team_id", suffixes=("_for", "_against"))
    join_with_game_plays_players = game_plays_with_teams.merge(game_plays_players_data, on=['play_id', 'game_id', 'play_num'])
    final_table = join_with_game_plays_players.merge(player_info, on='player_id')
    final_table = final_table[final_table['event'] == 'Goal'].sort_values(by=['dateTime'])
    # final_table_scorer = final_table[final_table['playerType'] == 'Scorer']
    # final_table_assist = final_table[final_table['playerType'] == 'Assist']
    print(final_table)
    play_id_lists = final_table.play_id.unique()
    play_lists = {
        '1st': [],
        '2nd': [],
        '3rd': [],
        '4th': []
    }

    for i in play_id_lists:
        get_plays = final_table[final_table['play_id'] == i]
        print(get_plays)
        # return 404
        if(get_plays.shape[0] < 1):
            abort(404)
        info = get_plays.iloc[0]
        # all_season_scores = re.findall(r'\d+', info['description'])

        
        # if(len(all_season_scores) != get_plays.shape[0] - 1):
        #     abort(500)

        dataJSON = {
            'team_for': info['abbreviation_for'],
            'team_against': info['abbreviation_against'],
            'goals_home' : info['goals_home'],
            'goals_away': info['goals_away'],
            'time': get_time_format(info['periodTime']),
            'period': get_period(info['period']),
            'assists': []
        }
        
        for index, row in get_plays.iterrows():
            if(row['playerType'] == 'Scorer'):
                dataJSON.update({
                    'scorer': {
                        'name': row['firstName'] + " " + row['lastName'] + " " + get_current_season_score(row['description'], row['lastName']),
                        'link': row['link']
                    }
                })
            if(row['playerType'] == 'Assist'):
                dataJSON['assists'].append({
                    'name':row['firstName'] + " " + row['lastName'] + " " + get_current_season_score(row['description'], row['lastName']),
                    'link': row['link']
                })  
        play_lists[get_period(info['period'])].append(dataJSON)   
    return jsonify(play_lists)
        

# route mapping for HTTP GET on /api/schedule/TOR
@app.route('/api/teams/<int:team_id>', methods=['GET'])
def get_task(team_id):
    # fetch sub dataframe for all teams (hopefully 1) where abbreviation=team_id
    teams = team_data[team_data["team_id"] == team_id]
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
