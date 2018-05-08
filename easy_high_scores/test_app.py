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

    # check length
    assert len(key_one) == 64 and len(key_two) == 64

    # check for randomness
    assert key_one != key_two

    # SHA256 test vector
    assert easy_high_scores.keys.gen_pub_key('') == 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'

# check register
def test_register(client):
    register_one = client.get('/api/register').data
    register_two = client.get('/api/register').data
    assert register_one != register_two
    assert b'private key' in register_one
    assert len(register_one) == 88 # check byte count of response

# check requesting with bad private key
def test_bad_request(client):
    get = client.get('/api/' + 'bad private key')

    print(get.status_code)
    assert get.status_code == 404

# check GETing scores
def test_get_scores(client):
    user_priv_key = json.loads(client.get('/api/register').data)['private key']
    get = client.get('/api/' + user_priv_key)

    # response should be empty array
    assert b'[]' in get.data
    assert get.status_code == 200

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
    
    # check error message
    assert b'Error!' in post.data

    # check 'bad request' status code
    assert post.status_code == 400
    
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

# check top x scores
def test_top_x_scores(client):
    user_priv_key = json.loads(client.get('/api/register').data)['private key']
    top = client.get('/api/top/1/' + user_priv_key).data

    # response should be empty array at first
    assert b'[]' in top

    # add three scores
    many_scores = []
    for i in range(0,3):
        many_scores.append({'name':'Alice', 'score':'123'})
    many_scores = json.dumps(many_scores)
    post = client.post('/api/' + user_priv_key, data=many_scores,
        content_type='application/json').data
    assert b'OK' in post

    # get top 1 scores
    top = client.get('/api/top/1/' + user_priv_key).data
    assert top.count(b'"123"') == 1 and top.count(b'"Alice"') == 1

    # get top 2 scores
    top = client.get('/api/top/2/' + user_priv_key).data
    assert top.count(b'"123"') == 2 and top.count(b'"Alice"') == 2

# check add/return scores
def test_add_return(client):
    user_priv_key = json.loads(client.get('/api/register').data)['private key']

    # add two scores
    many_scores = []
    for i in range(0,2):
        many_scores.append({'name':'Alice', 'score':'123'})
    many_scores = json.dumps(many_scores)
    post = client.post('/api/' + user_priv_key, data=many_scores,
        content_type='application/json').data
    assert b'OK' in post

    # add another score with add/return
    addreturn = client.get('/api/addreturn/' + user_priv_key + '/Chris-100', data=many_scores,
        content_type='application/json').data
    
    # were the other two scores returned
    assert addreturn.count(b'"123"') == 2 and addreturn.count(b'"Alice"') == 2

    # was the new score returned as well?
    assert addreturn.count(b'"100"') == 1 and addreturn.count(b'"Chris"') == 1

# check get public key from private
def test_get_public_key(client):
    user_priv_key = json.loads(client.get('/api/register').data)['private key']

    public_key = client.get('/api/public_key/' + user_priv_key).data

    # is the correct public key returned for our random private key
    assert easy_high_scores.keys.gen_pub_key(user_priv_key).encode() in public_key
