from actor_graph import ActorGraph
from dotenv import load_dotenv
import os

load_dotenv()

db_user = os.getenv('NEO4J_USER')
db_pass = os.getenv('NEO4J_PASS')

with ActorGraph(db_user, db_pass) as graph:
    graph.drop_indexes()
    graph.drop_all_nodes()
