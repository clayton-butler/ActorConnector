from neo4j import GraphDatabase
from dotenv import load_dotenv
import re
import os
import sys

class ActorGraph:
    def __init__(self, username, password):
        load_dotenv()
        self.driver = GraphDatabase.driver(os.getenv('NEO4J_HOST'), auth=(username, password))
        self.constraints = [
            {'label': 'Person', 'prop': 'name_id', 'constraint_name': 'person_name_id'},
            {'label': 'Actor', 'prop': 'name_id', 'constraint_name': 'actor_name_id'},
            {'label': 'Production', 'prop': 'title_id', 'constraint_name': 'production_title_id'},
            {'label': 'Movie', 'prop': 'title_id', 'constraint_name': 'movie_title_id'},
            {'label': 'Episode', 'prop': 'title_id', 'constraint_name': 'episode_title_id'},
            {'label': 'Series', 'prop': 'title_id', 'constraint_name': 'series_title_id'}
        ]
        self.indexes = [
            {'label': 'Person', 'prop': 'name', 'index_name': 'person_name'},
            {'label': 'Actor', 'prop': 'name', 'index_name': 'actor_name'},
            {'label': 'Production', 'prop': 'title', 'index_name': 'production_title'},
            {'label': 'Movie', 'prop': 'title', 'index_name': 'movie_title'},
            {'label': 'Episode', 'prop': 'title', 'index_name': 'episode_title'},
            {'label': 'Series', 'prop': 'title', 'index_name': 'series_title'}
        ]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.close()

    def __del__(self):
        self.driver.close()

    def __required_property_is_null(self, prop):
        if prop is None or prop == '' or prop == '\\N':
            return True
        return False

    def __convert_optional_property(self, prop, number=False):
        if prop == '\\N':
            return None
        if number:
            return int(prop)
        return prop

    def __get_series_of_episode(self, session, episode_id):
        query = """MATCH (e:Episode {title_id: $episode_id})-[:EPISODE_OF]->(s:Series)
                   RETURN s.title AS title, s.title_id AS imdb_id
                   LIMIT 1
                """
        result = session.run(query, {'episode_id': episode_id})
        return result.single().data()

    def __get_appearance_totals_of_actor(self, session, actor_id):
        query = """MATCH (a:Actor {name_id: $actor_id})
                   OPTIONAL MATCH (a)-[:ACTED_IN]->(m:Movie)
                   OPTIONAL MATCH (a)-[:ACTED_IN]->(e:Episode)
                   OPTIONAL MATCH (e)-[:EPISODE_OF]->(s:Series)
                   WITH COUNT(DISTINCT m) AS movie_count, 
                        COUNT(DISTINCT e) AS episode_count,
                        COUNT(DISTINCT s) AS series_count
                   WHERE (movie_count + episode_count) > 0
                   RETURN movie_count, 
                          episode_count,
                          series_count
                """
        result = session.run(query, {'actor_id': actor_id})
        return result.single().data()

    def __os_convert_file_path(self, filename):
        if sys.platform == 'linux':
            return filename.lstrip('/')
        return filename

    def drop_all_nodes(self):
        with self.driver.session() as session:
            query = 'CALL apoc.periodic.iterate("MATCH (n) RETURN n", "DETACH DELETE n", {batchSize:100000})'
            session.run(query)

    def init_indexes(self):
        with self.driver.session() as session:
            for params in self.constraints:
                constraint_query = f"CREATE CONSTRAINT {params['constraint_name']} ON (l:{params['label']}) ASSERT l.{params['prop']} IS UNIQUE"
                session.run(constraint_query)
            for params in self.indexes:
                index_query = f"CREATE INDEX {params['index_name']} FOR (l:{params['label']}) ON (l.{params['prop']})"
                session.run(index_query)

    def drop_indexes(self):
        with self.driver.session() as session:
            for index in self.indexes:
                query = f"DROP INDEX {index.index_name}"
                session.run(query)
            for constraint in self.constraints:
                query = f"DROP CONSTRAINT {constraint.constraint_name}"
                session.run(query)

    def delete_orphans(self):
        query = 'MATCH (n) WHERE NOT (n)--() DELETE n'
        with self.driver.session() as session:
            session.run(query)

    def add_actors_from_batch_file(self, filename):
        filename = self.__os_convert_file_path(os.path.abspath(filename))
        query = f"""
                USING PERIODIC COMMIT 100000
                LOAD CSV WITH HEADERS FROM 'file:///{filename}' as line FIELDTERMINATOR '\t'
                CREATE (:Actor:Person {{name_id: toString(line.name_id), name: toString(line.name),
                        birth_year: toInteger(line.birth_year), death_year: toInteger(line.death_year)}})
                """
        with self.driver.session() as session:
            session.run(query)

    def add_actor(self, name_id, name, birth_year, death_year):
        if self.__required_property_is_null(name_id) or self.__required_property_is_null(name):
            return False
        birth_year = self.__convert_optional_property(birth_year, number=True)
        death_year = self.__convert_optional_property(death_year, number=True)

        with self.driver.session() as session:
            query = """MERGE (a:Actor:Person{name_id: $name_id})
                       ON CREATE SET a.name = $name, a.birth_year = $birth_year, a.death_year = $death_year
                       ON MATCH SET a.death_year = $death_year
                    """
            session.run(query, {'name_id': name_id, 'name': name, 'birth_year': birth_year, 'death_year': death_year})

    def add_movies_from_batch_file(self, filename):
        filename = self.__os_convert_file_path(os.path.abspath(filename))
        query = f"""
                USING PERIODIC COMMIT 100000
                LOAD CSV WITH HEADERS FROM 'file:///{filename}' as line FIELDTERMINATOR '\t'
                CREATE (:Movie:Production {{title_id: toString(line.title_id), title: toString(line.title),
                        year: toInteger(line.year)}})
                """
        with self.driver.session() as session:
            session.run(query)

    def add_movie(self, title_id, title, year):
        if self.__required_property_is_null(title_id) or self.__required_property_is_null(title):
            return False
        year = self.__convert_optional_property(year, number=True)

        with self.driver.session() as session:
            query = """MERGE (m:Movie:Production{title_id: $title_id})
                       ON CREATE SET m.title = $title, m.year = $year
                    """
            session.run(query, {'title_id': title_id, 'title': title, 'year': year})

    def add_series_from_batch_file(self, filename):
        filename = self.__os_convert_file_path(os.path.abspath(filename))
        query = f"""
                USING PERIODIC COMMIT 100000
                LOAD CSV WITH HEADERS FROM 'file:///{filename}' as line FIELDTERMINATOR '\t'
                CREATE (:Series {{title_id: toString(line.title_id), title: toString(line.title),
                        start_year: toInteger(line.start_year), end_year: toInteger(line.end_year)}})
                """
        with self.driver.session() as session:
            session.run(query)

    def add_series(self, title_id, title, start_year, end_year):
        if self.__required_property_is_null(title_id) or self.__required_property_is_null(title):
            return False
        start_year = self.__convert_optional_property(start_year, number=True)
        end_year = self.__convert_optional_property(end_year, number=True)

        with self.driver.session() as session:
            query = """MERGE (s:Series{title_id: $title_id})
                       ON CREATE SET s.title = $title, s.start_year = $start_year, s.end_year = $end_year
                    """
            session.run(query, {'title_id': title_id, 'title': title, 'start_year': start_year, 'end_year': end_year})

    def add_episodes_from_batch_file(self, filename):
        filename = self.__os_convert_file_path(os.path.abspath(filename))
        query = f"""
                USING PERIODIC COMMIT 100000
                LOAD CSV WITH HEADERS FROM 'file:///{filename}' as line FIELDTERMINATOR '\t'
                CREATE (:Episode:Production {{title_id: toString(line.title_id), title: toString(line.title),
                        year: toInteger(line.year)}})
                """
        with self.driver.session() as session:
            session.run(query)

    def add_episode(self, title_id, title, year):
        if self.__required_property_is_null(title_id) or self.__required_property_is_null(title):
            return False
        year = self.__convert_optional_property(year, number=True)

        with self.driver.session() as session:
            query = """MERGE(e:Episode:Production{title_id: $title_id})
                       ON CREATE SET e.title = $title, e.year = $year
                    """
            session.run(query, {'title_id': title_id, 'title': title, 'year': year})

    def add_actor_relations_from_batch_file(self, filename):
        filename = self.__os_convert_file_path(os.path.abspath(filename))
        query = f"""
                USING PERIODIC COMMIT 100000
                LOAD CSV WITH HEADERS FROM 'file:///{filename}' as line FIELDTERMINATOR '\t'
                MATCH (a:Actor{{name_id: line.name_id}})
                MATCH (p:Production{{title_id: line.title_id}})
                CREATE (a)-[r:ACTED_IN{{roles: toString(line.roles)}}]->(p)
                """
        with self.driver.session() as session:
            session.run(query)

    def add_role(self, title_id, actor_id, roles):
        if self.__required_property_is_null(title_id) or self.__required_property_is_null(actor_id):
            return False
        roles = self.__convert_optional_property(roles)
        if roles is not None:
            roles = ', '.join([r.strip('"') for r in re.split(r',(?=")', roles.strip('[]'))])

        with self.driver.session() as session:
            query = """MATCH (a:Actor{name_id: $actor_id})
                       MATCH (p:Production{title_id: $title_id})
                       MERGE (a)-[r:ACTED_IN]->(p)
                       SET r.roles = $roles
                    """
            session.run(query, {'title_id': title_id, 'actor_id': actor_id, 'roles': roles})

    def add_episode_relations_from_batch_file(self, filename):
        filename = self.__os_convert_file_path(os.path.abspath(filename))
        query = f"""
                USING PERIODIC COMMIT 100000
                LOAD CSV WITH HEADERS FROM 'file:///{filename}' as line FIELDTERMINATOR '\t'
                MATCH (e:Episode{{title_id: line.episode_id}})
                MATCH (s:Series{{title_id: line.series_id}})
                CREATE (e)-[:EPISODE_OF]->(s)
                SET e.episode_num = toInteger(line.episode_num), e.season_num = toInteger(line.season_num)
                """
        with self.driver.session() as session:
            session.run(query)

    def connect_episode(self, episode_id, series_id, season_num, episode_num):
        if self.__required_property_is_null(episode_id) or self.__required_property_is_null(series_id):
            return False
        season_num = self.__convert_optional_property(season_num, number=True)
        episode_num = self.__convert_optional_property(episode_num, number=True)

        with self.driver.session() as session:
            query = """MATCH (e:Episode{title_id: $episode_id})
                       MATCH (s:Series{title_id: $series_id})
                       SET e.season_num = $season_num, e.episode_num = $episode_num
                       MERGE (e)-[:EPISODE_OF]->(s)
                    """
            session.run(query, {'episode_id': episode_id, 'series_id': series_id, 'season_num': season_num, 'episode_num': episode_num})

    def get_actor_connection(self, actor_id_1, actor_id_2, max_search_depth=20):
        if actor_id_1 is None or actor_id_1 == '' or actor_id_2 is None or actor_id_2 == '':
            return False
        if max_search_depth < 1 or max_search_depth > 50 or not isinstance(max_search_depth, int):
            max_search_depth = 20
        with self.driver.session() as session:
            query = f"""MATCH (a:Actor {{name_id: '{actor_id_1}'}})
                        MATCH (b:Actor {{name_id: '{actor_id_2}'}})
                        MATCH path = shortestPath((a)-[r:ACTED_IN*0..{max_search_depth}]-(b))
                        RETURN path, 
                              [x IN RELATIONSHIPS(path) | x.roles] AS roles,
                              [x in NODES(path) | LABELS(x)] AS node_type
                    """
            result = session.run(query)
            result_row = result.single()
            if result_row is None:
                return []
            result_data = result_row.data()
            path = result_data['path']
            roles = result_data['roles']
            node_types = result_data['node_type']
            return_data = []
            for p in path:
                if p == 'ACTED_IN':
                    return_data.append({'role': roles.pop(0)})
                elif 'name_id' in p:
                    a_totals = self.__get_appearance_totals_of_actor(session, p['name_id'])
                    a = p.copy()
                    a.update(a_totals)
                    return_data.append({'actor': a})
                    node_types.pop(0)
                elif 'title_id' in p:
                    types = node_types.pop(0)
                    if 'Movie' in types:
                        return_data.append({'movie': p})
                    elif 'Episode' in types:
                        series_details = self.__get_series_of_episode(session, p['title_id'])
                        e = {
                            'episode_num': p['episode_num'] if 'episode_num' in p else None,
                            'season_num': p['season_num'] if 'season_num' in p else None,
                            'episode_title': p['title'],
                            'episode_id': p['title_id'],
                            'year': p['year'] if 'year' in p else None,
                            'parent_series': series_details['title'],
                            'parent_series_id': series_details['imdb_id']
                        }
                        return_data.append({'episode': e})

        return return_data

    def get_actor_info(self, actor_id):
        if actor_id is None or actor_id == '':
            return False
        with self.driver.session() as session:
            query = """MATCH (a:Actor {name_id: $actor_id})
                       OPTIONAL MATCH (a)-[:ACTED_IN]->(m:Movie)
                       OPTIONAL MATCH (a)-[:ACTED_IN]->(e:Episode)
                       OPTIONAL MATCH (e)-[:EPISODE_OF]->(s:Series)
                       WITH a.name AS name,
                            a.birth_year AS birth_year,
                            a.death_year AS death_year,
                            COUNT(DISTINCT m) AS movie_count, 
                            COUNT(DISTINCT e) AS episode_count,
                            COUNT(DISTINCT s) AS series_count
                       WHERE (movie_count + episode_count) > 0
                       RETURN name,
                              birth_year,
                              death_year,
                              movie_count, 
                              episode_count,
                              series_count
                    """
            result = session.run(query, {'actor_id': actor_id})
            return result.single().data()

    def guess_actor_imdb_id(self, actor_name):
        if actor_name is None or actor_name == '':
            return False
        with self.driver.session() as session:
            query = """MATCH (a:Actor {name: $actor_name})
                       MATCH (a)-[r:ACTED_IN]->()
                       WITH a.name_id AS name_id,
                            a.name AS name,
                            COUNT(DISTINCT r) AS role_count
                       RETURN name_id
                       ORDER BY role_count DESC
                       LIMIT 1
                    """
            result = session.run(query, {'actor_name': actor_name})
            return result.single().data()

    def actor_name_in_db(self, actor_name):
        if not actor_name:
            return False
        with self.driver.session() as session:
            query = """OPTIONAL MATCH (a:Actor {name: $actor_name})-[:ACTED_IN]-(:Production)
                       RETURN DISTINCT CASE WHEN EXISTS(a.name) THEN true ELSE false END AS exists
                    """
            result = session.run(query, {'actor_name': actor_name})
            return result.single().data()['exists']

    def actor_id_in_db(self, actor_id):
        if not actor_id:
            return False
        with self.driver.session() as session:
            query = """OPTIONAL MATCH (a:Actor {name_id: $actor_id})-[:ACTED_IN]-(:Production)
                       RETURN DISTINCT CASE WHEN EXISTS(a.name) THEN true ELSE false END AS exists
                    """
            result = session.run(query, {'actor_id': actor_id})
            return result.single().data()['exists']

    def graph_totals(self):
        with self.driver.session() as session:
            query = """MATCH (a:Actor)
                       WITH COUNT(a) AS count
                       RETURN 'actor' AS label, count
                       UNION ALL
                       MATCH (m:Movie)
                       WITH COUNT(m) AS count
                       RETURN 'movie' AS label, count
                       UNION ALL
                       MATCH (e:Episode)
                       WITH COUNT(e) AS count
                       RETURN 'episode' AS label, count
                       UNION ALL
                       MATCH (s:Series)
                       WITH COUNT(s) AS count
                       RETURN 'series' AS label, count
                       UNION ALL
                       MATCH ()-[r:ACTED_IN]->()
                       WITH COUNT(r) AS count
                       RETURN 'role' AS label, count
                    """
            result = session.run(query)
            return_data = {}
            for r in result:
                return_data[f"{r['label']}_count"] = r['count']
            return return_data

    def get_random_actor(self):
        with self.driver.session() as session:
            query = """MATCH ()-[roles:ACTED_IN]->()
                       WITH COUNT(roles) AS role_count
                       MATCH (a:Actor)-[r:ACTED_IN]->()
                       WHERE id(r) = toInteger(rand() * role_count)
                       RETURN a.name AS name, a.name_id AS imdb_id
                    """
            result = session.run(query)
            return result.single().data()