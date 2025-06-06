import os
from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
from .classification import classify_column
from .translations import TRANSLATIONS

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def get_text(lang: str, key: str) -> str:
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)


@app.route('/', methods=['GET', 'POST'])
def index():
    lang = request.args.get('lang', 'en')
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            return redirect(request.url)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        return redirect(url_for('results', filename=file.filename, lang=lang))
    return render_template('index.html', text=get_text(lang, 'upload'), lang=lang, tr=TRANSLATIONS.get(lang, TRANSLATIONS['en']))


@app.route('/results')
def results():
    lang = request.args.get('lang', 'en')
    filename = request.args.get('filename')
    if not filename:
        return redirect(url_for('index'))
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_excel(filepath)
    classifications = []
    for column in df.columns:
        samples = df[column].dropna().astype(str).tolist()[:5]
        classification = classify_column(column, samples)
        classifications.append(classification)
    return render_template('results.html', classifications=classifications, lang=lang, tr=TRANSLATIONS.get(lang, TRANSLATIONS['en']))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
