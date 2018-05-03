from flask import Flask

app = Flask(__name__)

import easy_high_scores.models
import easy_high_scores.controllers
