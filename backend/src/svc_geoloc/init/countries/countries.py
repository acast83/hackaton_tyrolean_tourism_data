import os
import csv
import uuid
import json

current_file_folder = os.path.dirname(os.path.realpath(__file__))

result = []

with open(current_file_folder+'/countries.csv') as f:
    for country in csv.reader(f):
        code, value_en, value_local, default_languages = country
        # print(country)

        result.append({
            'id': str(uuid.uuid4()),
            'code': code,
            'value_en': str(value_en),
            'value_local': str(value_local),
            'languages': list(default_languages.split('|'))
        })

with open(current_file_folder+'/../countries.json','wt') as f:
    json.dump(result, f, indent=1, ensure_ascii=False)