import logging
from datetime import datetime

from flask import Flask, render_template, request
from flask_mobility import Mobility
from requests import get

INFO_ENDPOINT = 'https://api.bloodlibrary.info/api/sets'
UPDATE_INTERVAL = 12 * 3600

app = Flask(__name__)
Mobility(app)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

data = None
data_last_update = datetime.min


def get_info():
    global data
    global data_last_update
    if (datetime.now() - data_last_update).total_seconds() > UPDATE_INTERVAL:
        raw_data = get(INFO_ENDPOINT).json()
        data = [
            {**zet,
             'total_cards': len(zet['cards']),
             'total_images': sum(1 for card in zet['cards'] if card['image'])
             }
            for zet in raw_data]
        data_last_update = datetime.now()
    return data


get_info()


@app.route("/", methods=['GET'])
def cards_panel():
    data = get_info()
    return render_template('allcards.html', zets=data, is_mobile=request.MOBILE)


if __name__ == '__main__':
    app.run(port=8080)
