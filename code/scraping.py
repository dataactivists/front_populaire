import json
from time import sleep

import pandas as pd
import requests

# fichier avec les codes des circonscriptions
df = pd.read_json('./data/codes_circos.json')

results = {}

for i, code_circo in df['code'].items():
    print(f'Downloading {code_circo} ({i + 1} out of 577)')

    # itérer sur les urls en modifiant le code circo
    url = f'https://apps.contexte.com/data/ctx-legislatives-2024/legislatives_2024/{code_circo}/results.json'
    res = requests.get(url)

    print(f'\tResults for {code_circo} downloaded\n\n')

    # sauver le résultat dans le dict
    result_circo = json.loads(res.content)
    results[code_circo] = result_circo

    # pour éviter le blocage
    sleep(5)

with open('./data/results.json', "w") as fp:
    json.dump(results, fp=fp)
