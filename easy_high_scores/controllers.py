from easy_high_scores import app
from easy_high_scores.database import db_session as db
from easy_high_scores.models import User, Highscore
from flask import request, jsonify, render_template
import json
import easy_high_scores.keys as keys
import uuid

                                                ############################
                                                #### ROUTES/CONTROLLERS ####
                                                ############################

# home page
@app.route('/')
def hello():
    return 'Hello, World!'

# create new user
@app.route('/api/register')
def register():
    new_priv_key = keys.gen_priv_key()
    new_pub_key = keys.gen_pub_key(new_priv_key)
    new_user = User(public_key=new_pub_key)
    db.add(new_user)
    db.commit()
    return 'private key: {}'.format(new_priv_key)

                                                #### RESTFUL API ####

# RESTful access to user's high score database
@app.route('/api/<string:private_key>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def restful(private_key):

    public_key = keys.gen_pub_key(private_key)
    if user_check(public_key) == False:
        return 'No user with that ID found.', 500

    if request.method == 'GET':
        return get_all_scores(public_key)

    if request.method == 'POST':
        return add_all_scores(public_key, request.data)
    
    if request.method == 'DELETE':
        return delete_all_scores(request.data)

# reset user's high score database
@app.route('/api/reset/<string:private_key>')
def reset_user_database(private_key):
    public_key = keys.gen_pub_key(private_key)
    if user_check(public_key) == False:
        return 'No user with that ID found.', 500

    return reset_user_scores(public_key)

                                                #### SIMPLE API ####

# get scores
@app.route('/api/get/<string:private_key>')
def simple_get_score(private_key):
    public_key = keys.gen_pub_key(private_key)
    if user_check(public_key) == False:
        return 'No user with that ID found.', 500

    return get_all_scores(public_key)

# add scores
# formatted as "name-score|name-score"
@app.route('/api/add/<string:private_key>/<string:score_list>')
def simple_add_score(private_key, score_list):

    public_key = keys.gen_pub_key(private_key)
    if user_check(public_key) == False:
        return 'No user with that ID found.', 500

    scores_to_add = score_list.split('|')
    score_list = []
    for score in scores_to_add:
        new_score = {}
        new_score['name'] = score[score.index('-') + 1:]
        new_score['score'] = score[:score.index('-')]
        score_list.append(new_score)
    
    return add_all_scores(public_key, json.dumps(score_list))

# delete scores
# formatted as "id|id"
@app.route('/api/delete/<string:private_key>/<string:id_list>')
def simple_delete_score(private_key, id_list):

    public_key = keys.gen_pub_key(private_key)
    if user_check(public_key) == False:
        return 'No user with that ID found.', 500

    id_list = id_list.split('|')
    ids_to_delete = []
    for id_ in id_list:
        id_as_dict = {}
        id_as_dict['id'] = id_
        ids_to_delete.append(id_as_dict)
    
    return delete_all_scores(json.dumps(ids_to_delete))
    

                                                #### APP LOGIC ####

# is there a user with that public key?
def user_check(public_key, private_key=None):
    if private_key != None:
        public_key = keys.gen_pub_key(private_key)

    if User.query.filter(User.public_key == public_key).first() == None:
        return False
    else:
        return True

# get all scores
def get_all_scores(public_key):
    score_rows = Highscore.query.filter(Highscore.user == public_key).all()
    score_list = []
    for row in score_rows:
        score_list.append({"id":row.uuid, "name":row.name, "score":row.score})
    return jsonify(score_list)

# add all scores
def add_all_scores(public_key, request_data):
    try:
        submitted_json = json.loads(request_data)
        scores_to_add = []
        for new_score in submitted_json:
            high = Highscore(user=public_key, uuid=uuid.uuid4().hex, name=new_score['name'], score=new_score['score'])
            scores_to_add.append(high)

        # amount of high scores is capped for each user
        all_scores = Highscore.query.all()
        if len(all_scores) > 1999:
            # sort low to high, scores filtered by float_from_string
            all_scores.sort(key=lambda k: float_from_string(k['score']))

            # remove the lowest scores
            for i in range(0, len(scores_to_add)):
                all_scores[i].delete()

        db.bulk_save_objects(scores_to_add)
        db.commit()
        return 'Success.'
    except:
        return render_template('json_error.txt'), 500

# delete all scores
def delete_all_scores(request_data):
    try:
        submitted_json = json.loads(request_data)
        for score in submitted_json:
            score_uuid = score['id']
            Highscore.query.filter(Highscore.uuid == score_uuid).delete()
        db.commit()
        return 'Success.'
    except:
        return render_template('json_error.txt'), 500

# reset user's score databse
def reset_user_scores(public_key):
    Highscore.query.filter(Highscore.user == public_key).delete()
    db.commit()
    return 'Success.'


                                                #### HELPER METHODS ####

# get numbers and the first decimal point from mixed string
# e.g., "1.2.ab345" returns 1.2345
def float_from_string(string):
    float_string = ''
    one_dot = False
    for i in string:
        if i.isdigit():
            float_string += i
        if i == '.' and one_dot == False:
            float_string += i
            one_dot = True
    
    # handle erroneous strings
    try:
        float(float_from_string)
    except:
        return 0
    
    return float(float_string)


                                                #### FLASK SHUTDOWN ####

# remove database sessions at the end of the request
# or when the application shuts down
@app.teardown_appcontext
def shutdown_session(exception=None):
    db.remove()
