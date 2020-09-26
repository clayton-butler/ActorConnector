<template>
  <div>
    <vue-typeahead-bootstrap
      v-model="query"
      :data="actors"
      :serializer="item => item.name"
      @hit="onSelectActor($event)"
      :disabledValues="(selected_actor ? [selected_actor.name] : [])"
      placeholder="Search Actors"
      @input="actorSearch"
    >
      <template slot="append">
          <b-button v-if="button_state === 'random'"
                    @click="selectRandom"
                    v-b-tooltip.hover
                    title="Select a random actor">
            <b-icon-dice6></b-icon-dice6>
          </b-button>
          <b-button v-else-if="button_state === 'loading'" disabled>
            <b-spinner class="loading_spinner my-auto" small></b-spinner>
          </b-button>
          <b-button v-else-if="button_state === 'clear'" @click="clearInput">
            <b-icon-x></b-icon-x>
          </b-button>
      </template>
      <template slot="suggestion" slot-scope="{ data, htmlText }">
        <div class="d-flex align-items-center">
          <img v-if="data.profile_path" :src="data.profile_path"/>
          <img v-else src="http://localhost:8080/img/person-fill-small.png">
          <span class="ml-4" v-html="htmlText"></span>
        </div>
      </template>
    </vue-typeahead-bootstrap>
  </div>
</template>

<script>
import axios from 'axios';
import debounce from 'lodash.debounce';
import VueTypeaheadBootstrap from 'vue-typeahead-bootstrap';

export default {
  name: 'ActorSelect',
  components: {
    'vue-typeahead-bootstrap': VueTypeaheadBootstrap,
  },
  data() {
    return {
      query: '',
      selected_actor: {
        name: '',
        tmdb_id: '',
        imdb_id: '',
      },
      actors: [],
      button_state: 'random',
    };
  },
  methods: {
    actorSearch: debounce(function () {
      const oldButtonState = this.button_state;
      if (!this.selected_actor.name) {
        // this.show_loading_animation = true;
        this.button_state = 'loading';
      }
      const path = `http://localhost:5000/actor/search/${this.query}`;
      axios.get(path)
        .then((res) => {
          this.actors = res.data.actor_list;
        })
        .catch((error) => {
          console.log(error);
        })
        .finally(() => {
          this.button_state = oldButtonState;
        });
    }, 500),
    onSelectActor($event) {
      this.selected_actor.name = $event.name;
      this.selected_actor.tmdb_id = $event.tmdb_id;
      this.$emit('update:selected_actor', this.selected_actor);
    },
    clearInput() {
      this.query = '';
      this.selected_actor.name = '';
      this.selected_actor.tmdb_id = '';
      this.actors = [];
      this.$emit('update:selected_actor', this.selected_actor);
    },
    selectRandom() {
      this.button_state = 'loading';
      const path = 'http://localhost:5000/actor/random';
      axios.get(path)
        .then((res) => {
          this.selected_actor.tmdb_id = res.data.rand.tmdb_id;
          this.selected_actor.name = res.data.rand.name;
          this.selected_actor.imdb_id = res.data.rand.imdb_id;
          this.query = this.selected_actor.name;
          this.$emit('update:selected_actor', this.selected_actor);
          this.button_state = 'clear';
        })
        .catch((error) => {
          console.log(error);
        });
    },
  },
  watch: {
    selected_actor: {
      handler(newVal) {
        if (newVal.name === '' && newVal.tmdb_id === '') {
          this.query = '';
          this.button_state = 'random';
        } else {
          this.button_state = 'clear';
        }
      },
      deep: true,
    },
  },
};
</script>

<style scoped>
  .loading_spinner {
    /*width: 1em;*/
    /*height: 1em;*/
  }
</style>
