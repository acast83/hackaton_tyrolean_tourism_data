import json
with open('countries.json') as f:
    countries=json.load(f)

euc = ['Austria','Belgium','Bulgaria','Croatia','Cyprus','Czech Republic','Denmark','Estonia','Finland','France','Germany','Greece','Hungary','Ireland','Italy','Latvia','Lithuania','Luxembourg','Malta','Netherlands','Poland','Portugal','Romania','Slovakia','Slovenia','Spain','Sweden']
euc = [e.lower() for e in euc]

#res = set(['austria','belgium','bulgaria','czech republic','germany','denmark','estonia','spain','finland','france','greece','croatia','hungary','ireland','italy','lithuania','luxembourg','latvia','malta','poland','portugal','romania','sweden','slovenia','slovakia'])
#
#print(set(euc)-res)


for c in countries:
    if c['value_en'].lower() in euc:
        c['eu_country'] = True
    else:
        if 'eu_country' in c:
            del c['eu_country']

with open('countries.json.updated', 'wt') as f:
    json.dump(countries,f,indent=1,ensure_ascii=False)