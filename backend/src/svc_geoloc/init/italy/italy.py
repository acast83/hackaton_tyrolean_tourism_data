import psycopg2
import os

import sys
import json
import csv
import uuid

current_file_folder = os.path.dirname(os.path.realpath(__file__))

json_result = {}

provinces_by_code = {}


def fix_chars(s):
    s = s.replace('–', '-')
    return s


regions_by_it_name = {}
regions_by_id = {}

PROVINCE_UPPER_2_CODE = {}

with open('provinces-it.csv', 'rt') as f:
    for l in csv.reader(f, delimiter=','):

        it_name, code, reg_it_name = l

        if fix_chars(reg_it_name) not in regions_by_it_name:
            _idr = str(uuid.uuid4())

            regions_by_id[_idr] = {
                'value_it': fix_chars(reg_it_name)
            }

            regions_by_it_name[fix_chars(reg_it_name)] = {
                'id_region': _idr,
                'value_it': fix_chars(reg_it_name),
            }

        if code == 'ROMA':
            code = 'RM'

        if code in provinces_by_code:
            print(f'code {code} already presented in provinces_by_code')
            sys.exit()

        PROVINCE_UPPER_2_CODE[fix_chars(it_name).upper()] = code

        provinces_by_code[code] = {
            'id': 'TODO',  # str(uuid.uuid4()),
            'id_region': regions_by_it_name[fix_chars(reg_it_name)]['id_region'],
            'it_region': fix_chars(reg_it_name),
            'value_it': fix_chars(it_name)
        }

with open('provinces-de.csv', 'rt') as f:
    for l in csv.reader(f, delimiter=','):

        code, de_name, reg_de_name = l[0], l[1], l[3]

        if code not in provinces_by_code:
            print(f'code {code} is not presented in provinces_by_code generated for italian language')
            sys.exit()

        reg = provinces_by_code[code]['id_region']
        regions_by_id[reg]['value_de'] = fix_chars(reg_de_name)

        provinces_by_code[code]['de_region'] = fix_chars(reg_de_name)
        provinces_by_code[code]['value_de'] = fix_chars(de_name)

with open('provinces-en.csv', 'rt') as f:
    for l in csv.reader(f, delimiter=','):

        '''A,South Tyrol,Bolzano,BZ,Trentino-South Tyrol,North-East,531178,7400,69,116,Arno Kompatscher (SVP)'''

        code, en_name, reg_en_name = l[3], l[1], l[4]

        if code not in provinces_by_code:
            print(f'code {code} is not presented in provinces_by_code generated for italian language')
            sys.exit()

        reg = provinces_by_code[code]['id_region']
        regions_by_id[reg]['value_en'] = fix_chars(reg_en_name)

        provinces_by_code[code]['en_region'] = fix_chars(reg_en_name)
        provinces_by_code[code]['value_en'] = fix_chars(en_name)

_regions = []
for i in regions_by_id.keys():
    _regions.append({'id': i, 'local_value': regions_by_id[i]['value_it'],
                     'translations':
                         {'it': regions_by_id[i]['value_it'],
                          'de': regions_by_id[i]['value_de'],
                          'en': regions_by_id[i]['value_en']}})

json_result = {'regions': []}

for r in range(len(_regions)):
    json_result['regions'].append(_regions[r])

connection_coverage = psycopg2.connect(
    user="impresaone",
    password="123",
    host="localhost",
    port="5432",
    database="coverage_full"
)

curr = connection_coverage.cursor()

curr.execute(f"select id, name from addresses_italy_provinces")

# a_provinces = []
a_cities = []

provinces_sinonims = {
    'FORLI\' CESENA': 'FORLÌ-CESENA',
    'MASSA CARRARA': 'MASSA-CARRARA',
    'MONZA E DELLA BRIANZA': "MONZA E BRIANZA",
    'PESARO URBINO': 'PESARO E URBINO',
    'BARLETTA ANDRIA TRANI': 'BARLETTA-ANDRIA-TRANI',
    'VERBANO CUSIO OSSOLA': 'VERBANO-CUSIO-OSSOLA',
}

for t in curr.fetchall():

    db_id_province, italian_province_name = t[0], t[1]

    if italian_province_name in provinces_sinonims:
        italian_province_name = provinces_sinonims[italian_province_name]

    if italian_province_name not in PROVINCE_UPPER_2_CODE:
        print("NOT_FOUND ", italian_province_name)
        sys.exit()

    province_code = PROVINCE_UPPER_2_CODE[italian_province_name]
    provinces_by_code[province_code]['id'] = db_id_province

_provinces = []
for p in provinces_by_code:
    _p = {'id': provinces_by_code[p]['id'],
          'code': p, 'id_region': provinces_by_code[p]['id_region'],
          'local_value': provinces_by_code[p]['value_it'],
          'translations': {
              'it': provinces_by_code[p]['value_it'],
              'de': provinces_by_code[p]['value_de'],
              'en': provinces_by_code[p]['value_en'],
          }
          }

    _provinces.append(_p)

json_result['provinces'] = []

for p in range(len(_provinces)):
    json_result['provinces'].append(_provinces[p])

with open('cities_it2de_upper.json') as f:
    it2de_upper = json.load(f)

_cities = []

curr.execute(f"select id, province_id, name, istat_code from addresses_italy_commune")
for t in curr.fetchall():

    trans = {'it': t[2]}

    if t[2] in it2de_upper:
        trans['de'] = it2de_upper[t[2]]

    _cities.append({'id': t[0], 'id_province': t[1], 'local_value': t[2], 'translations': trans})

json_result['municipalities'] = []
for c in range(len(_cities)):
    json_result['municipalities'].append(_cities[c])

with open(current_file_folder + '/../italy.json', 'wt') as f:
    json.dump(json_result, f, indent=1, ensure_ascii=False)
