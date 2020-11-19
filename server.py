from flask import Flask, request, render_template, flash, redirect, session, jsonify
import crud
from jinja2 import StrictUndefined
from model import connect_to_db

app = Flask(__name__)
app.secret_key = "ABC"
app.jinja_env.undefined = StrictUndefined

@app.route('/')
def show_login():
    """Show hello.html template."""
    return render_template('homepage.html')

@app.route('/createuser')
def create_user():
    """Show greet.html template """
    # user = create_player(user, pw, bio, sport, city)
    return render_template('createuser.html')

@app.route('/search')
def search():
    """ see teammates that share your city and sport """
    #collect current user info
    flash(f"These are all the potential teammates based on your location and activity interest!")
    profile = crud.get_player_by_id(session['current_user'])
    #collect matching info
    potentials = []
    sport_potentials = crud.get_players_by_sport(profile.sport)
    city_potentials = crud.get_players_by_city(profile.city)
    players = crud.get_players()
    #check all players for matches
    for player in players:
        if (player in city_potentials) and (player in sport_potentials):
            potentials.append(player)
    return render_template('findteammates.html', potentials=potentials)

@app.route('/nav')
def navigate():
    """ Show Navigation page """
    return render_template("nav.html")

@app.route('/add.json')
def add_player():
    user_id = session['current_user']
    team_id = session['current_team']
    user = crud.get_player_by_id(user_id)
    team = crud.get_team_by_id(team_id)
    # if crud.is_new_player(user,team):
    #     is_new = True
    # else:
    #     is_new = 'old'
    new_player = crud.create_team_player(user, team) 
    new_player = new_player.user.username

    return jsonify(new_player, user_id, crud.is_new_player(user,team))
   

@app.route('/login')
def login():
    """allow user to login """
    username = request.args.get('username')
    password = request.args.get('password')

    users_login = crud.get_player_by_username(username)
    
    if users_login == None:
        flash(f'Looks like you have not made an account yet!')
        return redirect('/')
    elif users_login.password == password:
        session['current_user'] = users_login.user_id
        flash(f'Nice to see you back, {users_login.username}!')
        return redirect('/nav')
    else:
        flash(f'The password you inputed for {users_login.username} is incorrect. Try again!')
        return redirect('/')

@app.route('/createteam')
def create_team():
    """ form to create new team is rendered """
    #TODO: create a playing location? ie park? so people don't join teams that meet hella far
    return render_template("createteam.html")

@app.route('/teams', methods=["POST"])
def register_team():
    #TODO: add park portion thru ajax, such when a city is selected, only parks in that city show
    team_name = request.form.get('team_name')
    description = request.form.get('description')
    city_id = request.form.get('cities')
    team_city = crud.get_city_by_id(city_id) #change to crud.get_city(city)
    #create the sport
    sport_id = request.form.get('sports')
    team_sport = crud.get_sport_by_id(sport_id) #get_sport_by_id
    #create park
    # park = request.form.get('park')
    # teams_park = crud.create_park(park, team_city)
    # TODO: my_session = session['my_teams'][crud.get_team_by_id(team_id).team_id] assuming one user could 
    # have already created a team
    if crud.get_team_by_teamname(team_name):
        flash(f'Sorry! That team name is already in use!')
        return redirect('/createteam')
    else:
        my_team = crud.create_team(team_name, description, team_sport, team_city)
        session['my_teams'] = my_team.team_id
        flash(f'Your team {my_team.team_name} has been created!')
        return redirect('/teams')

@app.route('/teams')
def display_teams():
    """ displays all teams"""
    teams = crud.get_teams()
    return render_template('teams.html', teams=teams)

@app.route('/teams/<team_id>')
def show_team(team_id):
    """Show details of a particular team """
    team = crud.get_team_by_id(team_id)
    players = crud.get_teams_players(team)
    session['current_team'] = team_id #stores the team id of the current team page user in on
    return render_template('team_details.html', team=team, players=players)

@app.route('/users/<user_id>')
def show_player(user_id):
    """Show details of a particular player """
    player = crud.get_player_by_id(user_id)
    return render_template('user_details.html', player=player)

@app.route('/users', methods=["POST"])
def register_user():
    """create user and adds them to the database"""
    #create city
    city_id = request.form.get('cities')
    c = crud.get_city_by_id(city_id) 
    #create sport
    sport_id = request.form.get('sports')
    s = crud.get_sport_by_id(sport_id)
    
    #create player
    username = request.form.get('username')
    password = request.form.get('password')
    bio = request.form.get('bio')
    if crud.get_player_by_username(username):
        flash(f'Sorry! That username is already in use!')
        return redirect('/createuser')
    else:
        crud.create_player(username, password, bio, s, c)
        flash(f'Player created! Please login')
        return redirect('/')

@app.route('/users')
def display_user():
    """ display all users that have been created """
    users = crud.get_players()

    return render_template('users.html', users=users)

if __name__ == "__main__":
    connect_to_db(app)
    app.run(debug=True, host='0.0.0.0')