# By manuals from https://flask.palletsprojects.com/en/2.2.x/quickstart/
#
# run:
#
# python -m flask --app server --debug run
# or
# flask --app web --debug run
#
# Run in server prod mode:
#
# export FLASK_APP=server.py
# export FLASK_ENV=development
# export FLASK_DEBUG=0
# flask run
#
# Runnning with SSL:
# flask run --cert=cert.pem --key=key.pem
#

import cotton
import imageio.v3 as iio
import io

import datetime
import sys
import os

templates = [0, 1, 2, 3, 4, 5, 6, 7]

template_viewports = [
    [[238, 63], [643, 349], [642, 710], [239, 387]],
    [[238, 63-160], [643, 133], [642, 764], [239, 427]],
    [[0, 0], [800-1, 0], [800-1, 600-1], [0, 600-1]],
    [[469, -210], [1324, 271], [1320, 965], [469, 437]],
    [[0, 0], [1024-1, 0], [1024-1, 868-1], [0, 868-1]],
    [[0, 0], [1080-1, 0], [1080-1, 854-1], [0, 854-1]],
    [[0, 0], [865-1, 0], [865-1, 475-1], [0, 475-1]],
    [[0, 0], [710-1, 0], [710-1, 475-1], [0, 475-1]],
]

# aspect ratio of the view port in the template image
template_aspects = [
    (3, 2),
    (1, 1),
    (4, 3),
    (16, 10),
    (1024, 868),
    (1080, ),
    (865, 475),
    (710, 475),
]


sys.path.append(os.path.split(os.getcwd())[0])

from markupsafe import escape
from flask import Flask, url_for, request, render_template, make_response, redirect , send_from_directory, send_file

import time

app = Flask(__name__, static_folder='static')


@app.route('/robots.txt')
@app.route('/t')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

@app.route("/", methods=['GET'])
def idx():
    try:
        templates_with = [(i, False) for i in templates]
        templates_with[0] = (0, True)

        return render_template("index.html",
                               templates=templates_with
                               )
    except Exception as ex:
        raise ex


@app.route('/convert', methods = ['POST'])
def cottonify():

    if request.method == 'POST':
        f = request.files['file']
        template_id = int(request.form.get('t', '0'))

        print (template_id)

        if template_id not in templates:
            return ""

        src = iio.imread(f)

        template = iio.imread(os.path.join('c_templates', f"{template_id}.png")).copy()

        img = cotton.cottonify(src, template, template_viewports[template_id], template_aspects[template_id], noise=True)

        bytes = iio.imwrite(r'<bytes>', img, extension=".png")
        id = (datetime.datetime.now() - datetime.datetime(2022, 2, 24, 0, 0, 0)).total_seconds()

        return send_file(
            io.BytesIO(bytes),
            mimetype = 'image/png',
            as_attachment = False,
            download_name = f'{id}.png'
        )

@app.route('/i/<int:img_id>')
def get_attachment(img_id):
    img_id = int(img_id)
    if img_id not in templates:
        return ""
    return send_file(
        os.path.join('c_templates', f"{img_id}.png"))
