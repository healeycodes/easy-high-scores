[![Build Status](https://travis-ci.org/healeycodes/easy-high-scores.svg?branch=master)](https://travis-ci.org/healeycodes/easy-high-scores)

## easy high scores

<br>

High scores API for apps/games/websites. This was a free service I ran for a while to support game jammers :)

![](https://github.com/healeycodes/easy-high-scores/blob/master/preview.png)

![](https://github.com/healeycodes/easy-high-scores/blob/master/preview-routes.png)

<br>

### Features

* Open source
* Beginner friendly
* One-click instant setup
* RESTful API (GET/POST/DELETE)
* A shareable public code, allowing read-only access
* JSON-based, compatible with the latest standard
* An additional simple API relying solely on GET requests
* Submit scores and get updated score-list with one request
* Return top x scores (sorted by numerical data, scores may contain letters)
* Capped at 2000 scores per user, after which the lowest scores get bumped

<br>

### Documention

[GitHub Wiki](https://github.com/healeycodes/easy-high-scores/wiki/easy-high-scores-API)

<br>

### Tech Stack

Back end: Python, Flask, SQLite via SQLalchemy

Front end: HTML5, Bulma CSS-framework

Tests: PyTest

<br>

### Build Steps

Note: This project uses Python3.6 because ```json.load()``` and ```json.loads()``` don't support binary input in lower versions.

```
$ git clone https://github.com/healeycodes/easy-high-scores
$ pip install Flask
$ pip install SQLAlchemy
$ cd easy-high-scores
$ python .\init_db.py
$ python .\run_prod.py
```

```
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

There's also a ```run_debug.py``` script in the same directory for local debugging.

<br>

 ### Testing

 ```
 $ pip install -U pytest
 $ cd easy-high-scores
 $ pytest
 ```

 ```
test_app.py ...................                                          [100%]

========================== 19 passed in 1.60 seconds ==========================
```

<br>

### License

https://mit-license.org/
