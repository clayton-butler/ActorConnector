from actor_graph import ActorGraph
from dotenv import load_dotenv
import os


load_dotenv()
db_user = os.getenv('NEO4J_USER')
db_pass = os.getenv('NEO4J_PASS')
imdb_dir = 'imdb_files'
batch_dir = 'batch_files'

with ActorGraph(db_user, db_pass) as graph:
    print('db insert start')
    print('creating indexes ...')
    graph.init_indexes()
    print('creating movies ...')
    graph.add_movies_from_batch_file(os.path.join(batch_dir, 'movie_batch.tsv'))
    print('creating episodes ...')
    graph.add_episodes_from_batch_file(os.path.join(batch_dir, 'episode_batch.tsv'))
    print('creating series ...')
    graph.add_series_from_batch_file(os.path.join(batch_dir, 'series_batch.tsv'))
    print('creating actors ...')
    graph.add_actors_from_batch_file(os.path.join(batch_dir, 'actor_batch.tsv'))
    print('creating actor relations ...')
    graph.add_actor_relations_from_batch_file(os.path.join(batch_dir, 'actor_relation_batch.tsv'))
    print('creating episode relations ...')
    graph.add_episode_relations_from_batch_file(os.path.join(batch_dir, 'episode_relation_batch.tsv'))
    print('db insert end')
    # print('deleting orphan nodes ...')
    # graph.delete_orphans()

print('graph database load complete')