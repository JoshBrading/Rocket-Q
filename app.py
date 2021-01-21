import requests
import json
import uuid
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import default
import config

app = Flask(__name__)
app.secret_key = config.secret_key

# global
ENV = 'dev'
url = ''
if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = config.local_db
    url = 'http://localhost:5000/'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = config.remote_db
    url = 'http://rocket-q.tacki.xyz/'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class RQ_Messages(db.Model):
    __tablename__ = 'RQ_Messages'
    access_code = db.Column(db.String(200), primary_key=True)
    user_name = db.Column(db.String(200), unique=True)
    user_id = db.Column(db.Integer, unique=True)
    start_message = db.Column(db.String(200))
    stop_message = db.Column(db.String(200))
    next_message = db.Column(db.String(200))
    join_message = db.Column(db.String(200))
    leave_message = db.Column(db.String(200))
    queue_message = db.Column(db.String(200))
    queue_empty_message = db.Column(db.String(200))
    player_list = db.Column(db.String(2000))
    active = db.Column(db.Integer)
    save_queue = db.Column(db.Integer)

    def __init__(self, user_name, user_id, access_code, start_message, stop_message, next_message, join_message, leave_message, queue_message, queue_empty_message, player_list, active, save_queue):
        self.user_name = user_name
        self.user_id = user_id
        self.access_code = access_code
        self.start_message = start_message
        self.stop_message = stop_message
        self.next_message = next_message
        self.join_message = join_message
        self.leave_message = leave_message
        self.queue_message = queue_message
        self.queue_empty_message = queue_empty_message
        self.player_list = player_list
        self.active = active
        self.save_queue = save_queue


@app.route('/')
def index():  # Twitch API Integration
    code = request.args.get('code')
    channel_name = request.args.get('channel_name')
    user_command = request.args.get('user')
    action = request.args.get('action')
    access_code = request.args.get('uuid')
    if code is not None:
        response_access_data = requests.post('https://id.twitch.tv/oauth2/token?client_id=30pnsqm8mnjstg23mto3e9hfgaymdt&client_secret=4z8l0pwmvhso3nurfoaphbba9ucgms&code=' +
                                             code + '&grant_type=authorization_code&redirect_uri=' + url)
        try:
            access_token = json.loads(response_access_data.text)[
                'access_token']
            response_user_data = requests.get('https://api.twitch.tv/helix/users', headers={
                'Authorization': 'Bearer ' + access_token, 'Client-ID': '30pnsqm8mnjstg23mto3e9hfgaymdt'})
            session['user_id'] = json.loads(response_user_data.text)[
                'data'][0]['id']
            session['user_display'] = json.loads(response_user_data.text)[
                'data'][0]['display_name']
            session['user_login'] = json.loads(response_user_data.text)[
                'data'][0]['name']
        except:
            print('Error: KeyError')
        database_add()

        if db.session.query(RQ_Messages.save_queue).filter(RQ_Messages.user_id == session['user_id']).first()[0] == 0:
            save_queue = False
        else:
            save_queue = True
        return render_template('Setup.html',
                               access_code=db.session.query(RQ_Messages.access_code).filter(
                                   RQ_Messages.user_id == session['user_id']).first()[0],
                               username=session['user_display'],
                               start_message=db.session.query(RQ_Messages.start_message).filter(
                                   RQ_Messages.user_id == session['user_id']).first()[0],
                               stop_message=db.session.query(RQ_Messages.stop_message).filter(
                                   RQ_Messages.user_id == session['user_id']).first()[0],
                               next_message=db.session.query(RQ_Messages.next_message).filter(
                                   RQ_Messages.user_id == session['user_id']).first()[0],
                               join_message=db.session.query(RQ_Messages.join_message).filter(
                                   RQ_Messages.user_id == session['user_id']).first()[0],
                               leave_message=db.session.query(RQ_Messages.leave_message).filter(
                                   RQ_Messages.user_id == session['user_id']).first()[0],
                               queue_message=db.session.query(RQ_Messages.queue_message).filter(
                                   RQ_Messages.user_id == session['user_id']).first()[0],
                               queue_empty_message=db.session.query(RQ_Messages.queue_empty_message).filter(
                                   RQ_Messages.user_id == session['user_id']).first()[0],
                               save_queue=save_queue,
                               url=url)
    elif access_code is not None:
        return authenticate(channel_name, access_code, user_command, action)

    else:
        return render_template('Index.html')


def authenticate(channel_name, access_code, user, action):
    if db.session.query(RQ_Messages).filter(RQ_Messages.access_code == access_code).count() == 1:
        if db.session.query(RQ_Messages).filter(RQ_Messages.user_name == channel_name).count() == 1:
            return output_handler(access_code, user, action)
        else:
            return default.ERROR_MISMATCH
    elif db.session.query(RQ_Messages).filter(RQ_Messages.user_name == channel_name).count() == 1:
        return default.ERROR_MISMATCH
    else:
        return default.ERROR_USER_DOES_NOT_EXIST


def output_handler(access_code, user_command, action):
    if action == 'start':
        return db.session.query(RQ_Messages.start_message).filter(
            RQ_Messages.access_code == access_code).first()[0]
    elif action == 'stop':
        if db.session.query(RQ_Messages.save_queue).filter(RQ_Messages.user_id == session['user_id']).first()[0] == 0:
            update = RQ_Messages.query.filter_by(access_code=access_code).update({
                RQ_Messages.player_list: ''})
            db.session.commit()

        return db.session.query(RQ_Messages.stop_message).filter(
            RQ_Messages.access_code == access_code).first()[0]
    elif action == 'next':

        player = ''
        player_list_raw = db.session.query(RQ_Messages.player_list).filter(
            RQ_Messages.access_code == access_code).first()[0]
        if player_list_raw != '':
            player_list_dict = json.loads(player_list_raw)
            del player_list_dict[list(player_list_dict.keys())[0]]
            try:
                player = list(player_list_dict.keys())[0]
                player_list = json.dumps(player_list_dict)
                update = RQ_Messages.query.filter_by(access_code=access_code).update(
                    {RQ_Messages.player_list: player_list})
                db.session.commit()
                return db.session.query(RQ_Messages.next_message).filter(
                    RQ_Messages.access_code == access_code).first()[0].replace('$user', player)
            except:
                update = RQ_Messages.query.filter_by(access_code=access_code).update({
                    RQ_Messages.player_list: ''})
                db.session.commit()
        return "<p> q empty </p>"
    elif action == 'join':
        add_player(user_command, access_code)
        return db.session.query(RQ_Messages.join_message).filter(
            RQ_Messages.access_code == access_code).first()[0].replace('$user', user_command)
    elif action == 'leave':
        remove_player(user_command, access_code)
        return db.session.query(RQ_Messages.leave_message).filter(
            RQ_Messages.access_code == access_code).first()[0].replace('$user', user_command)
    elif action == 'queue':
        try:
            player_list_raw = db.session.query(RQ_Messages.player_list).filter(
                RQ_Messages.access_code == access_code).first()[0]
            player_list_dict = json.loads(player_list_raw)
            player_list = ', '.join(player_list_dict.keys())
            return db.session.query(RQ_Messages.queue_message).filter(
                RQ_Messages.access_code == access_code).first()[0].replace('$list', player_list)
        except:
            return db.session.query(RQ_Messages.queue_empty_message).filter(
                RQ_Messages.access_code == access_code).first()[0]
    else:
        return default.ERROR_INVALID_ACTION


def add_player(user, access_code):
    player_list_raw = db.session.query(RQ_Messages.player_list).filter(
        RQ_Messages.access_code == access_code).first()[0]

    if player_list_raw != '':
        player_list_dict = json.loads(player_list_raw)
        player_list_dict[user] = 0
    else:
        player_list_dict = {user: 0}
    player_list = json.dumps(player_list_dict)
    update = RQ_Messages.query.filter_by(access_code=access_code).update(
        {RQ_Messages.player_list: player_list})
    db.session.commit()


def remove_player(user, access_code):
    player_list_raw = db.session.query(RQ_Messages.player_list).filter(
        RQ_Messages.access_code == access_code).first()[0]

    if player_list_raw != '':
        player_list_dict = json.loads(player_list_raw)
        if user in player_list_dict:
            del player_list_dict[user]
    else:
        return
    player_list = json.dumps(player_list_dict)
    update = RQ_Messages.query.filter_by(access_code=access_code).update(
        {RQ_Messages.player_list: player_list})
    db.session.commit()


def database_add():
    user_name = session['user_display']
    user_name = user_name.lower()
    user_id = session['user_id']
    if db.session.query(RQ_Messages).filter(RQ_Messages.user_id == user_id).count() == 0:

        access_code = uuid.uuid4()
        start_message = default.START_MESSAGE
        stop_message = default.STOP_MESSAGE
        next_message = default.NEXT_MESSAGE
        join_message = default.JOIN_MESSAGE
        leave_message = default.LEAVE_MESSAGE
        queue_message = default.QUEUE_MESSAGE
        queue_empty_message = default.QUEUE_EMPTY_MESSAGE
        player_list = ''
        active = '0'
        save_queue = '0'

        data = RQ_Messages(user_name, user_id, access_code, start_message,
                           stop_message, next_message, join_message, leave_message, queue_message, queue_empty_message, player_list, active, save_queue)
        db.session.add(data)
        db.session.commit()
    return redirect('Setup.html')


@ app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        user_id = session['user_id']
        start_message = request.form['start_message']
        stop_message = request.form['stop_message']
        next_message = request.form['next_queue']
        join_message = request.form['join_queue']
        leave_message = request.form['leave_queue']
        queue_message = request.form['queue_message']
        queue_empty_message = request.form['queue_empty_message']
        try:
            save_queue = request.form['save_queue']
        except:
            save_queue = '0'
        print(save_queue)
        if start_message != '':
            update = RQ_Messages.query.filter_by(user_id=user_id).update(
                {RQ_Messages.start_message: start_message})
        if stop_message != '':
            update = RQ_Messages.query.filter_by(user_id=user_id).update(
                {RQ_Messages.stop_message: stop_message})
        if next_message != '':
            update = RQ_Messages.query.filter_by(user_id=user_id).update(
                {RQ_Messages.next_message: next_message})
        if join_message != '':
            update = RQ_Messages.query.filter_by(user_id=user_id).update(
                {RQ_Messages.join_message: join_message})
        if leave_message != '':
            update = RQ_Messages.query.filter_by(user_id=user_id).update(
                {RQ_Messages.leave_message: leave_message})
        if queue_message != '':
            update = RQ_Messages.query.filter_by(user_id=user_id).update(
                {RQ_Messages.queue_message: queue_message})
        if queue_empty_message != '':
            update = RQ_Messages.query.filter_by(user_id=user_id).update(
                {RQ_Messages.queue_empty_message: queue_empty_message})
        update = RQ_Messages.query.filter_by(user_id=user_id).update(
            {RQ_Messages.save_queue: save_queue})
        db.session.commit()

        return redirect('Setup.html')


@ app.route('/commands', methods=['POST'])
def Commands():
    print('called')
    return render_template('index.html', commands='')


if __name__ == '__main__':
    app.run()
