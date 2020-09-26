<template>
  <div class="about">
    <ac-header></ac-header>
    <b-container fluid="">
      <b-row>
        <b-col></b-col>
        <b-col md="8">
          <h3 class="section-header">About</h3>
          <hr>
          {{actor_count.toLocaleString()}} actors, playing {{role_count.toLocaleString()}}
          characters in {{movie_count.toLocaleString()}} movies and
          {{episode_count.toLocaleString()}} episodes of {{series_count.toLocaleString()}} TV shows.
          <h3 class="section-header">Credits</h3>
          <hr>
          Actor, movie, and television show information courtesy of
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
          This product uses the TMDb API but is not endorsed or certified by TMDb.
          <h3 class="section-header">Source</h3>
          <hr>
          github link or something
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
    const path = 'http://localhost:5000/graph/totals';
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
</style>
