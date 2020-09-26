<template>
  <card :img_url="poster_img_url"
        :img_alt_text="image_alt_text"
        :title="title"
        :is_default_img="img_url ? false : true"

  >
    <div v-show="year">
      {{year}}
    </div>
    <br>
    <div v-show="season_num">
      Season {{season_num}}
    </div>
    <div v-show="episode_num">
      Episode {{episode_num}}
    </div>
  </card>
</template>

<script>
import Card from '@/components/Card.vue';

export default {
  name: 'StaticEpisodeCard',
  components: {
    card: Card,
  },
  inject: ['global_base_url'],
  props: [
    'title',
    'year',
    'img_url',
    'episode_num',
    'season_num',
  ],
  computed: {
    image_alt_text() {
      return `Series poster for ${this.title}`;
    },
    poster_img_url() {
      if (!this.img_url) {
        return `${this.global_base_url}/img/tv.png`;
      }
      return this.img_url;
    },
  },
};
</script>
