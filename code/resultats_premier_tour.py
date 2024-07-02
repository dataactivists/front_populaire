# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.16.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Résultats premier tour

# %% editable=true slideshow={"slide_type": ""}
import json

import altair as alt
import pandas as pd
import requests

# %% [markdown]
# ## Load data

# %% editable=true slideshow={"slide_type": ""}
with open('../data/raw_data/results.json', 'r') as file:
    data = json.load(file)

# %%
list(data.items())[:2]

# %%
df = pd.DataFrame.from_dict(data, orient='index').reset_index()

df.head()

# %% [markdown]
# ## Clean data

# %%
df.describe()

# %%
# dropper les colonnes inutiles
df = df.drop(columns=['blocs', 'code', 'estimation'])

# %%
# renommer les colonnes
df.columns = ['code_circo', 'premier_tour']

# %%
# extraire les infos utiles sur le premier tour
df['premier_tour'] = df['premier_tour'].apply(lambda x: x[0]['linesGroups'])

# %%
# vérifier que le premier élément est toujours 'participation'
set(j[0]['code'] for i, j in df['premier_tour'].items())

# %%
# vérifier que 'participation' a seulement 1 element
set(len(j[0]['lines']) for i, j in df['premier_tour'].items())

# %% editable=true slideshow={"slide_type": ""}
# exemple de données de 'participation'
df['premier_tour'][0][0]['lines'][0]

# %% editable=true slideshow={"slide_type": ""}
# populer colonne 'participation'
df['participation'] = df['premier_tour'].apply(lambda x: x[0]['lines'][0]['score'])

# %%
df['participation']

# %%
# exemple de données 'qualified'
df['premier_tour'][4][1:]

# %%
# exemple de données 'elected'
df['premier_tour'][5][1:]

# %%
# extraire les données candidat 1
for i, row in df.iterrows():
    df.loc[i, 'candidat_1'] = row['premier_tour'][1]['lines'][0]['label']
    df.loc[i, 'candidat_1_parti'] = row['premier_tour'][1]['lines'][0]['pole_code']
    df.loc[i, 'candidat_1_score'] = row['premier_tour'][1]['lines'][0]['score']

# %%
# extraire les données candidat 2
for i, row in df.iterrows():
    if row['premier_tour'][1]['code'] != 'elected':
        df.loc[i, 'candidat_2'] = row['premier_tour'][1]['lines'][1]['label']
        df.loc[i, 'candidat_2_parti'] = row['premier_tour'][1]['lines'][1]['pole_code']
        df.loc[i, 'candidat_2_score'] = row['premier_tour'][1]['lines'][1]['score']

# %%
# extraire les données candidat 3
for i, row in df.iterrows():
    if (
        row['premier_tour'][1]['code'] != 'elected'
        and len(row['premier_tour'][1]['lines']) == 3
    ):
        df.loc[i, 'candidat_3'] = row['premier_tour'][1]['lines'][2]['label']
        df.loc[i, 'candidat_3_parti'] = row['premier_tour'][1]['lines'][2]['pole_code']
        df.loc[i, 'candidat_3_score'] = row['premier_tour'][1]['lines'][2]['score']

# %%
# indiquer si second tour
df['second_tour'] = df['premier_tour'].apply(
    lambda x: False if x[1]['code'] == 'elected' else True
)

# %%
# indiquer si second tour entre NFP et RN
for i, row in df.iterrows():
    df.loc[i, 'NFP_vs_RN'] = (
        row['candidat_1_parti'] in ['NFP', 'EXD'] 
        and row['candidat_2_parti'] in ['NFP', 'EXD']
)

# %%
# indiquer difference de voix et si la différence est grande
for i, row in df.iterrows():
    if row['candidat_2'] is not None:
        df.loc[i, 'diff_vote'] = row['candidat_1_score'] - row['candidat_2_score']

        diff = df.loc[i, 'diff_vote']

        if diff < 0.5:
            df.loc[i, 'swing_circo'] = '<0.5'
        elif diff < 1:
            df.loc[i, 'swing_circo'] = '<1'
        elif diff < 2:
            df.loc[i, 'swing_circo'] = '<2'
        elif diff < 5:
            df.loc[i, 'swing_circo'] = '<5'

# %%
df.head(10)

# %%
# dropper colonne 'premier_tour'
df = df.drop(columns=['premier_tour'])

# %%
# convertir les dtypes
df = df.convert_dtypes()

df.info()

# %% editable=true slideshow={"slide_type": ""}
url_circos = 'https://apps.contexte.com/data/ctx-dzc/2024-06-legislatives.json'

res = requests.get(url_circos)

data_circos = res.json()

# %%
df_circos = pd.DataFrame.from_records(data_circos['districts'])[['code', 'name_full']]

df_circos.columns = ['code_circo', 'circo']

df_circos.head()

# %%
df = df.merge(
    right=df_circos,
    on='code_circo'
)

df.head()

# %%
# déplacer les colonnes
df = df.reindex(
    columns=[
        'circo',
        'code_circo',
        'second_tour',
        'swing_circo',
        'candidat_1',
        'candidat_1_parti',
        'candidat_1_score',
        'candidat_2',
        'candidat_2_parti',
        'candidat_2_score',
        'candidat_3',
        'candidat_3_parti',
        'candidat_3_score',
        'diff_vote',
    ]
)

# %% [markdown]
# ## Export data

# %%
# exporter en csv
df.to_csv('../data/resultats.csv', index=False)

# %%
# exporter en xlsx
df.to_excel('../data/resultats.xlsx')
