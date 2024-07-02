import json
from time import sleep

import pandas as pd
import requests

# fichier avec les codes des circonscriptions
url_codes_circos = 'https://apps.contexte.com/data/ctx-legislatives-2024/europeennes_2024/fe.json'
res = requests.get(url_codes_circos)
data = res.json()

codes_circos = pd.DataFrame(data)['code']

results = {}

for i, code_circo in codes_circos.items():
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
