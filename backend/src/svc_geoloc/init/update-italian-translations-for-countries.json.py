import json,csv

with open('world-in-italian.csv','rt') as f:
    wii = {l[1].upper(): l[3] for l in csv.reader(f)}

with open('countries.json') as f:
    countries = json.load(f)    

for country in countries:
    code=country['code']
    if code not in wii:
        print(f'skipping {code}')
        continue
        
    translations = country["translations"] if "translations" in country else {}
    translations['it'] = wii[code]

    country['translations'] = translations
    
with open('countries.json.updated','wt') as f:
    json.dump(countries,f,indent=1,ensure_ascii=False)
        
print('countries.json.updated has been created copy it into countries.json if you approve it')