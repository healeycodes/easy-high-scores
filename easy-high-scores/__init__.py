from flask import Flask

app = Flask(__name__)

import highscores.models
import highscores.controllers
