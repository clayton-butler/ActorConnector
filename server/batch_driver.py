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

# load graph db
# -------------------------------------

# some bug in the ubuntu neo4j distribution disallows
# loading files from arbitrary file system locations
def move_to_import(filename):
    full_path = os.path.abspath(os.path.join(batch_dir, filename))
    os.system(f'sudo cp {full_path} /var/lib/neo4j/import/')
    os.system((f'sudo chown neo4j:adm /var/lib/neo4j/import/{filename}'))


with ActorGraph(db_user, db_pass) as graph:
    print('db insert start')
    print('creating indexes ...')
    graph.init_indexes()
    print('creating movies ...')
    movie_file = 'movie_batch.tsv'
    if sys.platform == 'linux':
        move_to_import(movie_file)
    else:
        movie_file = os.path.join(batch_dir, movie_file)
    graph.add_movies_from_batch_file(movie_file)
    print('creating episodes ...')
    episode_file = 'episode_batch.tsv'
    if sys.platform == 'linux':
        move_to_import(episode_file)
    else:
        episode_file = os.path.join(batch_dir, episode_file)
    graph.add_episodes_from_batch_file(episode_file)
    print('creating series ...')
    series_file = 'series_batch.tsv'
    if sys.platform == 'linux':
        move_to_import(series_file)
    else:
        series_file = os.path.join(batch_dir, series_file)
    graph.add_series_from_batch_file(series_file)
    print('creating actors ...')
    actor_file = 'actor_batch.tsv'
    if sys.platform == 'linux':
        move_to_import(actor_file)
    else:
        actor_file = os.path.join(batch_dir, actor_file)
    graph.add_actors_from_batch_file(actor_file)
    print('creating actor relations ...')
    actor_relation_file = 'actor_relation_batch.tsv'
    if sys.platform == 'linux':
        move_to_import(actor_relation_file)
    else:
        actor_relation_file = os.path.join(batch_dir, actor_relation_file)
    graph.add_actor_relations_from_batch_file(actor_relation_file)
    print('creating episode relations ...')
    episode_relation_file = 'episode_relation_batch.tsv'
    if sys.platform == 'linux':
        move_to_import(episode_relation_file)
    else:
        episode_relation_file = os.path.join(batch_dir, episode_relation_file)
    graph.add_episode_relations_from_batch_file(episode_relation_file)
    print('db insert end')
    # print('deleting orphan nodes ...')
    # graph.delete_orphans()

print('graph database load complete')
