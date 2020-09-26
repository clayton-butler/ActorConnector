<template>
  <card :img_url="profile_img_url"
        :img_alt_text="image_alt_text"
        :title="actor.name"
        :is_default_img="actor.img_url ? false : true"
  >
    <div v-show="actor.birth_year">
      <span><span v-show="!actor.death_year">b.</span>{{actor.birth_year}}</span>
      <span v-show="actor.death_year"> - {{actor.death_year}}</span>
    </div>
    <br>
    <div>
      Appears in:
      <br>
      {{ movie_count_display }} and
      <br>
      {{ episode_count_display }}
      <br>
      of {{ series_count_display }}
    </div>
  </card>
</template>

<script>
import axios from 'axios';
import Card from '@/components/Card.vue';

export default {
  name: 'DynamicActorCard',
  props: ['name', 'tmdb_id', 'imdb_id'],
  components: {
    card: Card,
  },
  data() {
    return {
      actor: {
        name: '',
        tmdb_id: '',
        imdb_id: '',
        img_url: '',
        birth_year: '',
        death_year: '',
        movie_count: '',
        series_count: '',
        episode_count: '',
      },
    };
  },
  computed: {
    // watching this computed var so that watch will catch an update to either prop
    propChange() {
      return `${this.name}|${this.tmdb_id}`;
    },
    image_alt_text() {
      return `Profile picture of ${this.actor.name}`;
    },
    movie_count_display() {
      return `${this.actor.movie_count} ${this.pluarlize(this.actor.movie_count, 'movie')}`;
    },
    episode_count_display() {
      return `${this.actor.episode_count} ${this.pluarlize(this.actor.episode_count, 'episode')}`;
    },
    series_count_display() {
      return `${this.actor.series_count} ${this.pluarlize(this.actor.series_count, 'TV show')}`;
    },
    profile_img_url() {
      if (!this.actor.img_url) {
        return 'http://localhost:8080/img/person-fill.png';
      }
      return this.actor.img_url;
    },
  },
  watch: {
    propChange() {
      console.log('updating actor card');
      if (this.name !== '' && this.tmdb_id !== '') {
        this.getActorInfo();
      }
    },
  },
  methods: {
    getActorInfo() {
      const path = `http://localhost:5000/actor/${this.tmdb_id}`;
      axios.get(path)
        .then((res) => {
          this.actor.name = this.name;
          this.actor.tmdb_id = this.tmdb_id;
          this.actor.imdb_id = res.data.imdb_id;
          this.actor.img_url = res.data.img_url;
          this.actor.birth_year = res.data.birth_year;
          this.actor.death_year = res.data.death_year;
          this.actor.movie_count = res.data.movie_count;
          this.actor.series_count = res.data.series_count;
          this.actor.episode_count = res.data.episode_count;
          this.$emit('update:imdb_id', this.actor.imdb_id);
        })
        .catch((error) => {
          console.log(error);
        });
    },
    pluarlize(count, word) {
      if (count === 1) {
        return word;
      }
      return `${word}s`;
    },
  },
};
</script>
