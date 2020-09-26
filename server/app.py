import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from actor_graph import ActorGraph
import tmdbsimple as tmdb

#config
load_dotenv()
DEBUG = os.getenv('FLASK_DEBUG')
tmdb.API_KEY = os.getenv('TMDB_API_KEY')
db_user = os.getenv('NEO4J_USER')
db_pass = os.getenv('NEO4J_PASS')

app = Flask(__name__)
app.config.from_object(__name__)
CORS(app, resources={r'/*': {'origins': '*'}})


def get_poster(title, imdb_id, prod_type):
    search = tmdb.Search()
    results = search.movie(query=title) if prod_type == 'movie' else search.tv(query=title)
    if results['total_results'] == 0:
        return None
    for r in results['results']:
        cur_res = tmdb.Movies(r['id']).external_ids() if prod_type == 'movie' else tmdb.TV(r['id']).external_ids()
        if 'imdb_id' in cur_res and cur_res['imdb_id'] == imdb_id:
            prod = tmdb.Movies(r['id']).info() if prod_type == 'movie' else tmdb.TV(r['id']).info()
            if 'poster_path' not in prod or prod['poster_path'] is None or prod['poster_path'] == '':
                return None
            return 'https://image.tmdb.org/t/p/w185' + prod['poster_path']
    return None


def get_profile_pic(actor_name, imdb_id):
    path_prefix = 'https://image.tmdb.org/t/p/w185'
    search = tmdb.Search()
    results = search.person(query=actor_name)
    if results['total_results'] == 0:
        return None
    elif results['total_results'] == 1:
        single_res = results['results'][0]
        if 'profile_path' not in single_res or single_res['profile_path'] is None or single_res['profile_path'] == '':
            return None
        return 'https://image.tmdb.org/t/p/w185' + single_res['profile_path']
    else:
        for r in results['results']:
            actor = tmdb.People(r['id']).info()
            if 'imdb_id' in actor and actor['imdb_id'] == imdb_id:
                if 'profile_path' not in actor or actor['profile_path'] is None or actor['profile_path'] == '':
                    return None
                return path_prefix + actor['profile_path']
        # if imdb_ids don't match we just return the first profile pic we find from the name, it is usually correct
        for r in results['results']:
            if 'profile_path' in r and r['profile_path'] != '' and r['profile_path'] is not None:
                return path_prefix + r['profile_path']
    return None


@app.route('/actor/<tmdb_id>', methods={'GET'})
def get_actor_info(tmdb_id):
    response_obj = {'status': 'success'}
    if request.method == 'GET':
        profile = tmdb.People(tmdb_id).info()
        with ActorGraph(db_user, db_pass) as graph:
            if profile['imdb_id'] is None or profile['imdb_id'] == '' or not graph.actor_id_in_db(profile['imdb_id']):
                result = graph.guess_actor_imdb_id(profile['name'])
                response_obj['imdb_id'] = result['name_id']
            else:
                response_obj['imdb_id'] = profile['imdb_id']
            image_url = None
            if 'profile_path' in profile and profile['profile_path'] != '' and profile['profile_path'] is not None:
                image_url = 'https://image.tmdb.org/t/p/w185' + profile['profile_path']
            response_obj['img_url'] = image_url
            info = graph.get_actor_info(response_obj['imdb_id'])
            response_obj.update(info)

    return jsonify(response_obj)


@app.route('/actor/connection/<first_actor_id>/<second_actor_id>/<max_search_depth>', methods={'GET'})
def get_actor_connection(first_actor_id, second_actor_id, max_search_depth):
    response_obj = {'status': 'success'}
    if request.method == 'GET':
        with ActorGraph(db_user, db_pass) as graph:
            max_search_depth = int(max_search_depth)
            if not isinstance(max_search_depth, int) or max_search_depth < 1 or max_search_depth > 50:
                max_search_depth = 20
            connection = graph.get_actor_connection(first_actor_id, second_actor_id, max_search_depth=max_search_depth)
            response_obj['connection'] = []
            role_count = 0
            steps = -1
            for item in connection:
                type = list(item.keys())[0]
                if type == 'movie':
                    poster = get_poster(item['movie']['title'], item['movie']['title_id'], type)
                    d = {
                        'type': type,
                        'title': item['movie']['title'],
                        'img_url': poster,
                        'year': item['movie']['year'] if 'year' in item['movie'] else None
                    }
                    response_obj['connection'].append(d)
                elif type == 'episode':
                    poster = get_poster(item['episode']['parent_series'], item['episode']['parent_series_id'], type)
                    d = {
                        'type': type,
                        'parent_series': item['episode']['parent_series'],
                        'img_url': poster,
                        'episode_num': item['episode']['episode_num'] if 'episode_num' in item['episode'] else None,
                        'season_num': item['episode']['season_num'] if 'season_num' in item['episode'] else None,
                        'year': item['episode']['year']
                    }
                    response_obj['connection'].append(d)
                elif type == 'actor':
                    steps += 1
                    profile = get_profile_pic(item['actor']['name'], item['actor']['name_id'])
                    d = {
                        'type': type,
                        'name': item['actor']['name'],
                        'birth_year': item['actor']['birth_year'] if 'birth_year' in item['actor'] else None,
                        'death_year': item['actor']['death_year'] if 'death_year' in item['actor'] else None,
                        'img_url': profile,
                        'movie_count': item['actor']['movie_count'],
                        'episode_count': item['actor']['episode_count'],
                        'series_count': item['actor']['series_count']
                    }
                    response_obj['connection'].append(d)
                elif type == 'role':
                    role_str = ''
                    if 'role' in item and item['role'] != '' and item['role'] is not None:
                        roles = item['role'].split(',')
                        role_len = len(roles)
                        for i, r in enumerate(roles):
                            if i == (role_len-1) and role_len > 1:
                                role_str += ' and '
                            elif i > 0:
                                role_str += ', '
                            role_str += f'"{r}"'
                    else:
                        role_str = None
                    d = {
                        'type': type,
                        'roles': role_str,
                        'direction': 'down' if role_count % 2 == 0 else 'up'
                    }
                    role_count += 1
                    response_obj['connection'].append(d)
            response_obj['steps'] = steps

    return jsonify(response_obj)


@app.route('/actor/search/<search_term>', methods={'GET'})
def get_actor_list(search_term):
    response_obj = {'status': 'success'}
    if request.method == 'GET':
        search = tmdb.Search()
        results = search.person(query=search_term)
        actor_list = []
        if results['total_results'] > 0:
            with ActorGraph(db_user, db_pass) as graph:
                for res in results['results']:
                    person_res = tmdb.People(res['id']).info()
                    if 'imdb_id' in person_res and graph.actor_id_in_db(person_res['imdb_id']):
                        # if graph.actor_name_in_db(res['name']):
                        profile_path = ''
                        if 'profile_path' in person_res and person_res['profile_path'] != '' and person_res['profile_path'] is not None:
                            profile_path = 'https://image.tmdb.org/t/p/w45' + person_res['profile_path']
                        actor_list.append({'name': res['name'], 'tmdb_id': res['id'], 'imdb_id': person_res['imdb_id'], 'profile_path': profile_path})
        response_obj['actor_list'] = actor_list

    return jsonify(response_obj)


@app.route('/graph/totals', methods={'GET'})
def get_graph_totals():
    response_obj = {'status': 'success'}
    if request.method == 'GET':
        with ActorGraph(db_user, db_pass) as graph:
            totals = graph.graph_totals()
            response_obj['totals'] = totals

    return jsonify(response_obj)

@app.route('/actor/random', methods={'GET'})
def get_random_actor():
    response_obj = {'status': 'success'}
    if request.method == 'GET':
        with ActorGraph(db_user, db_pass) as graph:
            for i in range(10):
                rand = graph.get_random_actor()
                # response_obj['rand'] = rand
                search = tmdb.Search()
                results = search.person(query=rand['name'])
                if results['total_results'] == 0:
                    continue
                for r in results['results']:
                    actor = tmdb.People(r['id']).info()
                    if 'imdb_id' in actor and actor['imdb_id'] == rand['imdb_id']:
                        response_obj['rand'] = {
                            'name': rand['name'],
                            'imdb_id': rand['imdb_id'],
                            'tmdb_id': r['id']
                        }
                        break

    return jsonify(response_obj)

@app.route('/', methods={'GET'})
def default():
    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run()
