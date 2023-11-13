import re
import pandas as pd
import sqlite3

from flask import Flask, jsonify

from flask import request
import flask
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

app = Flask(__name__)

app.json_provider_class = LazyJSONEncoder
swagger_template = dict(
    info = {
        'title' : "API Documentation for Data Processing and Modeling",
        'version' : "1.0.0",
        'description' : "Dokumentasi API untuk Data Processing dan Modeling",
    },
    host = "127.0.0.1:5000/"
)

swagger_config = {
    "headers" : [],
    "specs" : [
        {
            "endpoint": "docs",
            "route" : "/docs.json",
        }
    ],
    "static_url_path": "/flasgger_static",
    # "static_folder": "static",  # must be set by user
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template, config = swagger_config)

def clean_tweet(text):
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = ' '.join(text.split())
    text = text.lower()

    return text
    
conn = sqlite3.connect('challenge_gold.db')

@swag_from("docs/text_processing.yml", methods = ['POST'])
@app.route('/text-processing', methods=['POST'])
def text_processing():
    
    text = request.form.get('text')
    
    json_response = {
        'status_code': 200,
        'description': "Teks yang sudah diproses",
        'data': clean_tweet(text),
    }

    response_data = jsonify(json_response)
    return response_data

@swag_from("docs/file_processing.yml", methods=['POST'])
@app.route('/file-processing', methods=['POST'])
def file_processing():
    try:
        file = request.files['file']

        if file:
            original_file_path = file.filename

            data = pd.read_csv(file, encoding='ISO-8859-1')
            data['cleaned_text'] = data['Tweet'].apply(clean_tweet)
            cleaned_data = data.to_json(orient='records')

            conn = sqlite3.connect('challenge_gold.db')

            table_name = "data_sosmed"
            data.to_sql(table_name, conn, if_exists='append', index=False)
            conn.commit()

            json_response = {
                'status_code': 200,
                'description': "Data yang sudah diproses",
                'data': cleaned_data,
            }

            response_data = jsonify(json_response)
            return response_data
        else:
            return jsonify({'error': 'File not found in request.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)