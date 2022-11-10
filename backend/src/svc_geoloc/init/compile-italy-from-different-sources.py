import json
import csv

with open('italy.json') as f:
    italy = json.load(f)

provinces = {p['id']: p for p in italy['provinces']}

#with open('istat.coverage.json') as f:
#    istat = json.load(f)

with open('istat.coverage.in.province.csv') as f:
    istat2 = {}
    for r in csv.reader(f):
        istat2[r[0]+':'+r[1]]=r[2]

with open('italy/cities_it2de.json') as f:
    it2de = json.load(f)
    id2de_lckey = {i.lower():it2de[i] for i in it2de}

with open('italy/zip.json') as f:
    z = json.load(f)
    istat2zip={}
    name2zip={}
    for c in z:
        istat2zip[c['codice']]=c['cap']

        name2zip[c['sigla']+':'+c['nome'].upper()]=c['cap']
        
print(json.dumps(name2zip,indent=1))
        
lvs={}

def icap(s):
    s = s.title()
    for w in ('del', 'sulla', 'strada', 'allo', 'in', 'di', 'dei'):
        s = s.replace(f' {w.capitalize()} ',f' {w.lower()} ')
    return s    

remove_dupl = set()
for comune in italy['municipalities']:
#    local_value=comune['local_value'].upper()

    province = provinces[comune['id_province']]
    prov_loc_value = f'{province["code"]}:{comune["local_value"].upper()}'

    if prov_loc_value in lvs:
        if lvs[prov_loc_value]['id_province']!=comune['id_province']:
            print('isto ime u drugoj provinciji',prov_loc_value, lvs[prov_loc_value]['istat_code']==comune['istat_code'], lvs[prov_loc_value]['id_province']==comune['id_province'])
    
        if lvs[prov_loc_value]['id_province']==comune['id_province']:
            remove_dupl.add(comune['id'])
            continue

#    print(prov_loc_value)
        
    lvs[prov_loc_value]=comune

    if prov_loc_value in istat2:
        comune['istat_code']=istat2[prov_loc_value]
        
    comune['local_value'] = icap(comune['local_value'].lower())
    comune['translations']['it'] = comune['local_value']

    if comune['local_value'].lower() in id2de_lckey:
        comune['translations']['de'] = id2de_lckey[comune['local_value'].lower()]

#    print ('istat_code' in comune, comune['istat_code'] in istat2zip)
#    if 'istat_code' in comune and comune['istat_code'] in istat2zip and len(istat2zip[comune['istat_code']]):
#        comune['zip'] = istat2zip[comune['istat_code']][0] 

#    lvl = comune['local_value'].lower()
    if prov_loc_value in name2zip and name2zip[prov_loc_value]:
        comune['zip'] = name2zip[prov_loc_value][0]

print("REMOVE",remove_dupl)

print(len(italy['municipalities']))
italy['municipalities'] = [x for x in italy['municipalities'] if x['id'] not in remove_dupl]
print(len(italy['municipalities']))


with open('result.json','wt') as f:
    json.dump(italy,f,indent=1,ensure_ascii=False)