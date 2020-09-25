from actor_graph import ActorGraph
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()
db_user = os.getenv('NEO4J_USER')
db_pass = os.getenv('NEO4J_PASS')
imdb_directory = 'imdb_files'
batch_directory = 'batch_files'
import_directory = '/var/lib/neo4j/import/'

def move_to_import(import_dir, batch_dir, filename):
    full_path = os.path.abspath(os.path.join(batch_dir, filename))
    os.system(f'sudo mv {full_path} {import_dir}')
    os.system(f'sudo chown neo4j:adm {import_dir}{filename}')

def split_batch_file(batch_dir, filename):
    basename = Path(filename).stem
    file_count = 0
    max_lines = 500000
    out_file = None
    header_line = ''
    created_files = []
    with open(os.path.join(batch_dir, filename), 'rt') as in_file:
        for i, line in enumerate(in_file):
            if i == 0:
                header_line = line
            if i % max_lines == 0:
                if out_file:
                    out_file.close()
                file_count += 1
                new_file = os.path.join(batch_dir, f'{basename}_{file_count}.tsv')
                out_file = open(new_file, 'wt')
                created_files.append(new_file)
                out_file.write(header_line)
            if i > 0:
                out_file.write(line)
        if out_file:
            out_file.close()
    return created_files

with ActorGraph(db_user, db_pass) as graph:
    print('db insert start')
    print('clearing import dir')
    os.system(f'sudo rm {import_directory}*')
    print('creating indexes ...')
    graph.init_indexes()
    print('creating movies ...')
    movie_files = split_batch_file(batch_directory, 'movie_batch.tsv')
    for file in movie_files:
        move_to_import(import_directory, batch_directory, os.path.basename(file))
        graph.add_movies_from_batch_file(os.path.basename(file))
    print('creating episodes ...')
    episode_files = split_batch_file(batch_directory, 'episode_batch.tsv')
    for file in episode_files:
        move_to_import(import_directory, batch_directory, os.path.basename(file))
        graph.add_episodes_from_batch_file(os.path.basename(file))
    print('creating series ...')
    series_files = split_batch_file(batch_directory, 'series_batch.tsv')
    for file in series_files:
        move_to_import(import_directory, batch_directory, os.path.basename(file))
        graph.add_series_from_batch_file(os.path.basename(file))
    print('creating actors ...')
    actor_files = split_batch_file(batch_directory, 'actor_batch.tsv')
    for file in actor_files:
        move_to_import(import_directory, batch_directory, os.path.basename(file))
        graph.add_actors_from_batch_file(os.path.basename(file))
    print('creating actor relations ...')
    actor_relation_files = split_batch_file(batch_directory, 'actor_relation_batch.tsv')
    for file in actor_relation_files:
        move_to_import(import_directory, batch_directory, os.path.basename(file))
        graph.add_actor_relations_from_batch_file(os.path.basename(file))
    print('creating episode relations ...')
    episode_relation_files = split_batch_file(batch_directory, 'episode_relations_batch.tsv')
    for file in episode_relation_files:
        move_to_import(import_directory, batch_directory, os.path.basename(file))
        graph.add_episode_relations_from_batch_file(os.path.basename(file))
    print('db insert end')
