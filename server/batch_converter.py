import os
import re
import csv

class BatchConverter:
    def __init__(self, input_dir, output_dir):
        self.input_dir = os.path.abspath(input_dir)+'/'
        self.output_dir = os.path.abspath(output_dir)+'/'

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __remove_duplicate_rows(self, filename):
        os.system(f'sort -u -o {filename} {filename}')

    def __get_title_type(self, t_type):
        if t_type in ['movie', 'tvMovie']:
            return 'movie'
        elif t_type in ['tvSeries', 'tvMiniSeries']:
            return 'series'
        elif t_type == 'tvEpisode':
            return 'episode'
        else:
            return None

    def __genre_is_excluded(self, genres):
        excluded_genres = ['Documentary', 'News', 'Game-Show', 'Talk-Show', 'Reality-TV', 'Adult']
        if genres is not None:
            for genre in genres.split(','):
                if genre in excluded_genres:
                    return True
        return False

    def __required_property_is_null(self, prop):
        if prop is None or prop == '' or prop == '\\N':
            return True
        return False

    def __convert_null_property(self, prop):
        if prop == '\\N':
            return None
        return prop

    def convert_title_basics(self, tsv_file):
        tsv_file = self.input_dir+tsv_file
        self.__remove_duplicate_rows(tsv_file)
        movie_file = self.output_dir+'movie_batch.tsv'
        series_file = self.output_dir+'series_batch.tsv'
        episode_file = self.output_dir+'episode_batch.tsv'
        with open(tsv_file, newline='') as input_fh,\
             open(movie_file, 'w', newline='') as movie_fh,\
             open(series_file, 'w', newline='') as series_fh,\
             open(episode_file, 'w', newline='') as episode_fh:

            reader = csv.DictReader(input_fh, delimiter='\t')
            movie_writer = csv.DictWriter(movie_fh, fieldnames=['title_id', 'title', 'year'], delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='"')
            movie_writer.writeheader()
            series_writer = csv.DictWriter(series_fh, fieldnames=['title_id', 'title', 'start_year', 'end_year'], delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='"')
            series_writer.writeheader()
            episode_writer = csv.DictWriter(episode_fh, fieldnames=['title_id', 'title', 'year'], delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='"')
            episode_writer.writeheader()

            for row in reader:
                if not self.__genre_is_excluded(row['genres']):
                    title_type = self.__get_title_type(row['titleType'])
                    if title_type == 'movie':
                        if not self.__required_property_is_null(row['tconst']) and not self.__required_property_is_null(row['primaryTitle']):
                            movie_props = {'title_id': row['tconst'],
                                           'title': row['primaryTitle'],
                                           'year': self.__convert_null_property(row['startYear'])}
                            movie_writer.writerow(movie_props)
                    if title_type == 'series':
                        if not self.__required_property_is_null(row['tconst']) and not self.__required_property_is_null(row['primaryTitle']):
                            series_props = {'title_id': row['tconst'],
                                            'title': row['primaryTitle'],
                                            'start_year': self.__convert_null_property(row['startYear']),
                                            'end_year': self.__convert_null_property(row['endYear'])}
                            series_writer.writerow(series_props)
                    if title_type == 'episode':
                        if not self.__required_property_is_null(row['tconst']) and not self.__required_property_is_null(row['primaryTitle']):
                            episode_props = {'title_id': row['tconst'],
                                             'title': row['primaryTitle'],
                                             'year': self.__convert_null_property(row['startYear'])}
                            episode_writer.writerow(episode_props)

    def convert_title_episode(self, tsv_file):
        tsv_file = self.input_dir + tsv_file
        self.__remove_duplicate_rows(tsv_file)
        episode_file = self.output_dir + 'episode_relation_batch.tsv'
        with open(tsv_file, newline='') as input_fh, open(episode_file, 'w', newline='') as episode_fh:
            reader = csv.DictReader(input_fh, delimiter='\t')
            episode_writer = csv.DictWriter(episode_fh, fieldnames=['episode_id', 'series_id', 'season_num', 'episode_num'], delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='"')
            episode_writer.writeheader()

            for row in reader:
                if not self.__required_property_is_null(row['tconst']) and not self.__required_property_is_null(row['parentTconst']):
                    episode_props = {'episode_id': row['tconst'],
                                     'series_id': row['parentTconst'],
                                     'season_num': self.__convert_null_property(row['seasonNumber']),
                                     'episode_num': self.__convert_null_property(row['episodeNumber'])}
                    episode_writer.writerow(episode_props)

    def convert_name_basics(self, tsv_file):
        tsv_file = self.input_dir + tsv_file
        self.__remove_duplicate_rows(tsv_file)
        actor_file = self.output_dir + 'actor_batch.tsv'
        with open(tsv_file, newline='') as input_fh, open(actor_file, 'w', newline='') as actor_fh:
            reader = csv.DictReader(input_fh, delimiter='\t')
            actor_writer = csv.DictWriter(actor_fh, ['name_id', 'name', 'birth_year', 'death_year'], delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='"')
            actor_writer.writeheader()

            for row in reader:
                professions = row['primaryProfession'].split(',')
                if ('actor' in professions or 'actress' in professions) and \
                        (not self.__required_property_is_null(row['nconst']) and not self.__required_property_is_null(row['primaryName'])):
                    actor_props = {'name_id': row['nconst'],
                                   'name': row['primaryName'],
                                   'birth_year': self.__convert_null_property(row['birthYear']),
                                   'death_year': self.__convert_null_property(row['deathYear'])}
                    actor_writer.writerow(actor_props)

    def convert_title_principals(self, tsv_file):
        tsv_file = self.input_dir + tsv_file
        self.__remove_duplicate_rows(tsv_file)
        role_file = self.output_dir + 'actor_relation_batch.tsv'
        with open(tsv_file, newline='') as input_fh, open(role_file, 'w', newline='') as role_fh:
            reader = csv.DictReader(input_fh, delimiter='\t', quoting=csv.QUOTE_NONE)
            role_writer = csv.DictWriter(role_fh, ['title_id', 'name_id', 'roles'], delimiter='\t', quoting=csv.QUOTE_NONE, escapechar='"')
            role_writer.writeheader()

            for row in reader:
                if (row['category'] in ['actor', 'actress']) and \
                        (not self.__required_property_is_null(row['tconst']) and not self.__required_property_is_null(row['nconst'])):
                    roles = self.__convert_null_property(row['characters'])
                    if roles is not None:
                        roles = ','.join([r.strip('"') for r in re.split(r',(?<!\\)(?=")', roles.strip('[]').replace('\\"', '"'))])
                    role_props = {'title_id': row['tconst'],
                                  'name_id': row['nconst'],
                                  'roles': roles}
                    role_writer.writerow(role_props)
