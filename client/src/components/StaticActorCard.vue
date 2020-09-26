<template>
  <card :img_url="profile_img_url"
        :img_alt_text="image_alt_text"
        :title="name"
        :is_default_img="img_url ? false : true"
  >
    <div v-show="birth_year">
      <span><span v-show="!death_year">b.</span>{{birth_year}}</span>
      <span v-show="death_year"> - {{death_year}}</span>
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
import Card from '@/components/Card.vue';

export default {
  name: 'StaticActorCard',
  components: {
    card: Card,
  },
  props: [
    'name',
    'img_url',
    'birth_year',
    'death_year',
    'movie_count',
    'episode_count',
    'series_count',
  ],
  computed: {
    movie_count_display() {
      const count = this.count_exists(this.movie_count);
      return `${count} ${this.pluarlize(this.movie_count, 'movie')}`;
    },
    episode_count_display() {
      const count = this.count_exists(this.episode_count);
      return `${count} ${this.pluarlize(this.episode_count, 'episode')}`;
    },
    series_count_display() {
      const count = this.count_exists(this.series_count);
      return `${count} ${this.pluarlize(this.series_count, 'TV show')}`;
    },
    image_alt_text() {
      return `Profile picture of ${this.name}`;
    },
    profile_img_url() {
      if (!this.img_url) {
        return 'http://localhost:8080/img/person-fill.png';
      }
      return this.img_url;
    },
  },
  methods: {
    count_exists(count) {
      if (!count) {
        return 0;
      }
      return count;
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
