import uuid
import psycopg2
import json
import os
import sys


connection_coverage = psycopg2.connect(
    user="impresaone",
    password="123",
    host="localhost",
    port="5432",
    database="coverage_full"
)


curr = connection_coverage.cursor()

curr.execute(f"select id, name from addresses_italy_provinces")

a_provinces = []
a_cities = []

for t in curr.fetchall():    
    a_provinces.append(str({"id":t[0], 'local_value':t[1], 'translations': {'it':t[1]} } ).replace("'",'"'))

curr.execute(f"select id, province_id, name, istat_code from addresses_italy_commune")
for t in curr.fetchall():
    a_cities.append(str({"id":t[0], 'province': t[1], 'local_value': t[2]}))

print("{")
print('  "provinces": [')
for p in range(len(a_provinces)):
    print('    '+a_provinces[p]+(',' if p<len(a_provinces)-1 else ''))

print("  ],")
print('  "municipalities": [')
for p in range(len(a_cities)):
    print('    '+a_cities[p])
    
