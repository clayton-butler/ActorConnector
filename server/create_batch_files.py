import os
import gzip
import shutil
import requests
import sys
from dotenv import load_dotenv
from batch_converter import BatchConverter
from actor_graph import ActorGraph

#   for neo4j config:
#   unset dbms.directories.import=import
#   set dbms.memory.heap.initial_size=2G
#   set dbms.memory.heap.max_size=4G
#   set dbms.memory.pagecache.size=4G
#   set dbms.security.procedures.unrestricted=apoc.*
#
# this script assumes a fresh db

load_dotenv()
db_user = os.getenv('NEO4J_USER')
db_pass = os.getenv('NEO4J_PASS')
imdb_dir = 'imdb_files'
batch_dir = 'batch_files'

# download imdb tsv files
# -------------------------------------

# clean up old files
if os.path.isdir(imdb_dir):
    print('deleting old imdb files ...')
    for file in [f for f in os.listdir(imdb_dir) if f.endswith('tsv')]:
        os.remove(os.path.join(imdb_dir, file))
else:
    print('creating imdb dir ...')
    os.mkdir(imdb_dir)

# download required dataset gzip files
print('downloading imdb dataset ...')
base_url = 'https://datasets.imdbws.com/'
files = ['title.basics.tsv', 'name.basics.tsv', 'title.episode.tsv', 'title.principals.tsv']
for file in files:
    with requests.get(f'{base_url}{file}.gz', stream=True) as r:
        r.raise_for_status()
        with open(os.path.join(imdb_dir, f'{file}.gz'), 'wb') as f:
            for chunk in r.iter_content(chunk_size=1048576):
                f.write(chunk)

# unzip files
print('decompressing dataset ...')
for file in files:
    with gzip.open(os.path.join(imdb_dir, f'{file}.gz'), 'rb') as g:
        with open(os.path.join(imdb_dir, file), 'wb') as f:
            shutil.copyfileobj(g, f)
print('cleaning up zip files ...')
for file in [f for f in os.listdir(imdb_dir) if f.endswith('gz')]:
    os.remove(os.path.join(imdb_dir, file))

# convert imdb tsv files to compatible format
# -------------------------------------
with BatchConverter(imdb_dir, batch_dir) as converter:
    print('batch convert start')
    if os.path.isdir(converter.output_dir):
        print('deleting old batch files ...')
        for file in [f for f in os.listdir(converter.output_dir) if f.endswith('tsv')]:
            os.remove(os.path.join(converter.output_dir, file))
    else:
        print('creating batch dir ...')
        os.mkdir(converter.output_dir)
    print('converting titles ...')
    converter.convert_title_basics('title.basics.tsv')
    print('converting actors ...')
    converter.convert_name_basics('name.basics.tsv')
    print('converting episodes ...')
    converter.convert_title_episode('title.episode.tsv')
    print('converting roles ...')
    converter.convert_title_principals('title.principals.tsv')
    print('batch convert end')
