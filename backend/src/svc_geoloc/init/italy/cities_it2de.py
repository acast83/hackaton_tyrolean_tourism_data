import json
import csv
import uuid

with open('istat-cities.json') as f:
    j = json.load(f)
    
it2de = {}
it2de_upper = {}

for city in j:
    if city['Denominazione in tedesco']:
        it2de[city['Denominazione in italiano']] = city['Denominazione in tedesco']
        it2de_upper[city['Denominazione in italiano'].upper()] = city['Denominazione in tedesco'].upper()
        

with open('cities_it2de.json','w') as f:
    json.dump(it2de, f, indent=1, ensure_ascii=False)

with open('cities_it2de_upper.json','w') as f:
    json.dump(it2de_upper, f, indent=1, ensure_ascii=False)
