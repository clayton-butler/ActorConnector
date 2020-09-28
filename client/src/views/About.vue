<template>
  <div class="about">
    <ac-header></ac-header>
    <b-container fluid="">
      <b-row>
        <b-col></b-col>
        <b-col md="5">
          <div class="about-section">
            <h3 class="section-header">About</h3>
            <hr>
            <p class="text-left">
              Everyone has played the party game "Six Degrees of Kevin Bacon", but what about
              "Eight Degrees of Achim Schmidtchen"? Or "Four Degrees of Yoneko Sakai"? Or "Five
              Degrees of Brian Hatch"? The Actor Connector can connect almost any two film actors
              together, from anywhere in the world, and using films going back to the start of the
              20th century. This site is an exercise in graph theory, and utilizes a graph
              consisting of {{actor_count.toLocaleString()}} actors, playing
              {{role_count.toLocaleString()}} characters in {{movie_count.toLocaleString()}}
              movies and {{episode_count.toLocaleString()}} episodes of
              {{series_count.toLocaleString()}} TV shows.
            </p>
          </div>
          <div class="about-section">
          <h3 class="section-header">Credits</h3>
          <hr>
          Actor, movie, and television show information <br>courtesy of
          <div>
            <a href="https://www.imdb.com" target="_blank" rel="noopener noreferrer">
              <img src="img/IMDB_logo.png" alt="IMDB"/>
            </a>
          </div>
          Used with permission.
          <br>
          <br>

          Profile and poster images courtesy of
          <div>
            <a href="https://www.themoviedb.org/" target="_blank" rel="noopener noreferrer">
              <img src="img/TMDB_logo.png" alt="TMDB">
            </a>
          </div>
          This product uses the TMDb API but is <br>not endorsed or certified by TMDb.
          </div>
          <h3 class="section-header">Source</h3>
          <hr>
          The source for this site, as well as the source for <br>building the graph database
          can be found
          <a href="https://github.com/clayton-butler/ActorConnector" target="_blank" rel="noopener roreferrer">
            here
          </a>.
          <br>
          <br>
          <br>
        </b-col>
        <b-col></b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>
import axios from 'axios';
import Header from '@/components/Header.vue';

export default {
  name: 'About',
  title: 'About',
  components: {
    'ac-header': Header,
  },
  inject: ['global_api_url'],
  data() {
    return {
      actor_count: '',
      role_count: '',
      movie_count: '',
      episode_count: '',
      series_count: '',
    };
  },
  mounted() {
    const path = `${this.global_api_url}/graph/totals`;
    axios.get(path)
      .then((res) => {
        this.actor_count = res.data.totals.actor_count;
        this.role_count = res.data.totals.role_count;
        this.movie_count = res.data.totals.movie_count;
        this.episode_count = res.data.totals.episode_count;
        this.series_count = res.data.totals.series_count;
      })
      .catch((error) => {
        console.log(error);
      });
  },
};
</script>

<style scoped>
  .section-header {
    margin-top: 2em;
  }
  about-section {
  }
</style>
