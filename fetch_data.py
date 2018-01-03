import os
import requests
import time
import json

from multiprocessing.pool import ThreadPool

pool_size = 9
clients_url = 'http://default-cr.cs300ohie.net/patient'
encounter_ids_url = 'http://source-shr.cs300ohie.net/encounters/patient/{}'
encounters_url = 'http://source-shr.cs300ohie.net/encounters/{}'
encounters_dir = 'encounters'

client_ids = requests.get(clients_url).json()

pool = ThreadPool(pool_size)

encounter_ids = []
def fetch_encounter_ids(client_id):
    patient_encounter_ids = requests.get(encounter_ids_url.format(client_id)).json()
    encounter_ids.extend(patient_encounter_ids)

for client_id in client_ids:
    pool.apply_async(fetch_encounter_ids, (client_id,))

pool.close()
pool.join()

print('Total number of encounters: {}'.format(len(encounter_ids)))
encounter_ids.sort()

pool = ThreadPool(pool_size)

encounters = []
def fetch_encounter(encounter_id):
    encounter = requests.get(encounters_url.format(encounter_id)).json()
    encounters.append(encounter)

start_time = time.time()
for encounter_id in encounter_ids:
    pool.apply_async(fetch_encounter, (encounter_id,))

pool.close()
pool.join()

end_time = time.time()
total_time = end_time - start_time
print('Total time:', total_time)
print('Transactions per second', len(encounter_ids)/total_time)
print('Transactions per second per thread', (len(encounter_ids)/total_time)/pool_size)

encounter_by_obs = {}
for encounter in encounters:
    num_obs = len(encounter.get('observations', []))
    if num_obs not in encounter_by_obs:
        encounter_by_obs[num_obs] = []
    encounter_by_obs[num_obs].append(encounter)

if not os.path.exists(encounters_dir):
    os.mkdir(encounters_dir)
for num_obs, encounters in sorted(encounter_by_obs.items()):
    
    num_obs_dir = os.path.join(encounters_dir, str(num_obs))
    if not os.path.exists(num_obs_dir):
        os.mkdir(num_obs_dir)
    
    print(num_obs, len(encounters))

    encounters.sort(key=lambda x: x['encounter_id'])    
    num_obs_file = open(os.path.join(num_obs_dir, "all.json"),'w')
    json.dump(encounters, num_obs_file)
    num_obs_file.close()

    for encounter in encounters:
        encounter_file = open(os.path.join(num_obs_dir, str(encounter['encounter_id']) + '.json'), 'w')
        json.dump(encounter, encounter_file)
        encounter_file.close()



    