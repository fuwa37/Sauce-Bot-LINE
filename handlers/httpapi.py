from handlers.sauce import get_source, comment_builder
from flask import request, Blueprint, jsonify, render_template

api = Blueprint('api', __name__)


@api.route('/upload', methods=['GET', 'POST'])
def upload():
    return render_template('upload.html')


@api.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        form = request.form
        force = form.get('force')
        trace = form.get('trace')

        f = request.files
        if f:
            f = f.get('file')
        else:
            f = form.get('url')

        print(form)

        r = get_source.get_source_data(f, force=force, trace=trace)
        return comment_builder.build_comment(r)
