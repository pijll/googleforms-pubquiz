#!/bin/bash

CURRDIR=$(dirname $0)

source $CURRDIR/../venv/bin/activate

export PYTHONPATH=$CURRDIR/../googleformspubquiz

export FLASK_APP=$CURRDIR/../googleformspubquiz/ui_flask
export FLASK_ENV=development

flask run
