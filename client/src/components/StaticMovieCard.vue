<template>
  <card :img_url="poster_img_url"
        :img_alt_text="image_alt_text"
        :title="title"
        :is_default_img="img_url ? false : true"
  >
    <div v-show="year">
      {{year}}
    </div>
  </card>
</template>

<script>
import Card from '@/components/Card.vue';

export default {
  name: 'StaticMovieCard',
  components: {
    card: Card,
  },
  inject: ['global_base_url'],
  props: [
    'title',
    'year',
    'img_url',
  ],
  computed: {
    image_alt_text() {
      return `Movie poster for ${this.title}`;
    },
    poster_img_url() {
      if (!this.img_url) {
        return `${this.global_base_url}/img/film.png`;
      }
      return this.img_url;
    },
  },
};
</script>
