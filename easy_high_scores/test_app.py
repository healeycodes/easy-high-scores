import os
import pytest
import json
from easy_high_scores import easy_high_scores

# set up test client
@pytest.fixture
def client():
    easy_high_scores.app.config['TESTING'] = True
    client = easy_high_scores.app.test_client()

    yield client

# check init_db
def test_create_database():
    try:
        os.remove('data.db')
    except OSError:
        pass
    
    easy_high_scores.database.init_db()
    assert os.path.isfile('data.db')

# check private and public key generation
def test_key_gen():
    key_one = easy_high_scores.keys.gen_priv_key()
    key_two = easy_high_scores.keys.gen_priv_key()
    assert len(key_one) == 64 and len(key_two) == 64
    assert key_one != key_two
    assert easy_high_scores.keys.gen_pub_key('') == 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'

# check register
def test_register(client):
    register_one = client.get('/api/register').data
    register_two = client.get('/api/register').data
    assert register_one != register_two
    assert b'private key' in register_one
    assert len(register_one) == 88 # check byte count of response

# check GETing scores
def test_get_scores(client):
    user_priv_key = json.loads(client.get('/api/register').data)['private key']
    get = client.get('/api/' + user_priv_key).data

    # response should be empty array
    assert b'[]' in get

# check POSTing scores
def test_add_scores(client):
    user_priv_key = json.loads(client.get('/api/register').data)['private key']
    scores = json.dumps([{'name':'Alice', 'score':'123'}])
    post = client.post('/api/' + user_priv_key, data=scores,
        content_type='application/json')
    
    # check response
    assert b'OK' in post.data
    
    # check if stored correctly
    get = client.get('/api/' + user_priv_key).data
    assert b'Alice' in get
    assert b'123' in get

# check POSTing erroneous scores
def test_add_erroneous_scores(client):
    user_priv_key = json.loads(client.get('/api/register').data)['private key']
    scores = json.dumps([{'naame':'Bob', 'score':'456'}]) # the error is on this line
    post = client.post('/api/' + user_priv_key, data=scores,
        content_type='application/json')
    
    # check response
    assert b'Error!' in post.data
    
    # check if not stored
    get = client.get('/api/' + user_priv_key).data
    assert b'Bob' not in get
    assert b'456' not in get

# check DELETEing scores
def test_delete_scores(client):
    user_priv_key = json.loads(client.get('/api/register').data)['private key']
    scores = json.dumps([{'name':'Alice', 'score':'123'}])
    post = client.post('/api/' + user_priv_key, data=scores,
        content_type='application/json')
    
    # check whether we have a score to delete
    assert b'OK' in post.data
    get = client.get('/api/' + user_priv_key).data
    assert b'Alice' in get
    assert b'123' in get

    # get ID of added score
    score_uuid = json.loads(get)[0]['id']
    score_to_delete = json.dumps([{'id':score_uuid}])

    # now delete
    delete = client.delete('/api/' + user_priv_key, data=score_to_delete,
        content_type='application/json').data
    assert b'OK' in delete

    # check that delete was successful
    get = client.get('/api/' + user_priv_key).data
    # response should be empty array
    assert b'[]' in get

# check score filtering function
def test_score_filter():
    assert easy_high_scores.controllers.float_from_string('123') == 123
    assert easy_high_scores.controllers.float_from_string('123.1.1') == 123.11
    assert easy_high_scores.controllers.float_from_string('1a2b3') == 123

# check user cap of 2000 high scores
def test_user_cap(client):
    user_priv_key = json.loads(client.get('/api/register').data)['private key']

    # fill up 2000 slots of scores
    many_scores = []
    for i in range(0,2000):
        many_scores.append({'name':'Alice', 'score':'123'})
    
    # add scores
    many_scores = json.dumps(many_scores)
    post = client.post('/api/' + user_priv_key, data=many_scores,
        content_type='application/json').data
    assert b'OK' in post
    
    # check length of response (i.e., the amount of scores)
    # after adding another 2000 scores, it should remain the same
    # because the extra 2000 scores should have been discarded
    scores_length = len(client.get('/api/' + user_priv_key).data)
    post = client.post('/api/' + user_priv_key, data=many_scores,
        content_type='application/json').data
    assert b'OK' in post
    assert len(client.get('/api/' + user_priv_key).data) == scores_length

    # now try and add a lower score which should be filtered out
    lower_score = json.dumps([{'name':'Alice', 'score':'1'}])
    post = client.post('/api/' + user_priv_key, data=lower_score,
        content_type='application/json').data
    assert b'OK' in post

    # check that lower scores was not added
    get = client.get('/api/' + user_priv_key).data
    assert b'"1"' not in get
