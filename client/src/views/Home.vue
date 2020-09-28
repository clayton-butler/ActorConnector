<template>
  <div class="home fill-height">
    <ac-header id="top"></ac-header>
    <b-container fluid class="fill-height">
      <b-row class="justify-content-center fill-height">
        <b-col></b-col>
        <b-col lg="3" class="v-center">
          <b-button variant="danger"
                    v-show="show_reset_button"
                    @click="resetInputs"
                    class="util-button mx-auto">
            <b-icon-arrow-clockwise></b-icon-arrow-clockwise>
            Reset
          </b-button>
          <b-collapse v-model="showInstructions">
            <instructions></instructions>
          </b-collapse>
          <b-collapse id="first-actor-collapse" v-model="first_actor_show">
            <dynamic-actor-card :name="first_actor.name"
                                :tmdb_id="first_actor.tmdb_id"
                                :imdb_id.sync="first_actor.imdb_id"
            />
          </b-collapse>
          <b-collapse id="first-input-collapse" v-model="first_input_show">
            <actor-select :selected_actor.sync="first_actor"/>
          </b-collapse>
          <b-collapse v-model="show_connection_button">
            <get-connection-button @get-connection-button-clicked="createConnection"
                                   :loading="connection_loading"
            />
          </b-collapse>
          <actor-connection v-show="show_connection"
                            :show_connection="show_connection"
                            :first_actor_id="first_actor.imdb_id"
                            :second_actor_id="second_actor.imdb_id"
                            :connections.sync="connections"
                            :max_search_depth="max_search_depth"
                            :is_small_connection="is_small_connection"
                            :enable_animations="enable_animations"
                            @connection-load-complete="hideInputElements"
                            @connection-animation-complete="showPostConnectionButtons"
          />
          <b-collapse id="second-input-collapse" v-model="second_input_show">
            <actor-select :selected_actor.sync="second_actor"/>
          </b-collapse>
          <b-collapse id="second-actor-collapse" v-model="second_actor_show">
            <dynamic-actor-card :name="second_actor.name"
                                :tmdb_id="second_actor.tmdb_id"
                                :imdb_id.sync="second_actor.imdb_id"
            />
          </b-collapse>
          <b-button variant="info"
                    v-show="show_top_button"
                    @click="scrollToTop"
                    class="util-button mx-auto">
            <b-icon-arrow-bar-up></b-icon-arrow-bar-up>Top
          </b-button>
          <options-modal :is_small_connection.sync="is_small_connection"
                         :enable_animations.sync="enable_animations"
                         :max_search_depth.sync="max_search_depth"
                         class="options-modal"
                         v-show="show_options_button">
          </options-modal>
        </b-col>
        <b-col></b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>
import Header from '@/components/Header.vue';
import ActorSelect from '@/components/ActorSelect.vue';
import DynamicActorCard from '@/components/DynamicActorCard.vue';
import Connection from '@/components/Connection.vue';
import GetConnectionButton from '@/components/GetConnectionButton.vue';
import OptionsModal from '@/components/OptionsModal.vue';
import Instructions from '@/components/Instructions.vue';

export default {
  name: 'Home',
  title: 'Home',
  data() {
    return {
      first_actor: {
        name: '',
        tmdb_id: '',
        imdb_id: '',
      },
      second_actor: {
        name: '',
        tmdb_id: '',
        imdb_id: '',
      },
      connections: [],
      first_actor_show: false,
      second_actor_show: false,
      first_input_show: true,
      second_input_show: true,
      show_connection: false,
      show_connection_button: true,
      connection_loading: false,
      show_top_button: false,
      show_reset_button: false,
      is_small_connection: false,
      enable_animations: true,
      max_search_depth: 20,
      show_options_button: true,
    };
  },
  components: {
    'ac-header': Header,
    'actor-select': ActorSelect,
    'dynamic-actor-card': DynamicActorCard,
    'actor-connection': Connection,
    'get-connection-button': GetConnectionButton,
    'options-modal': OptionsModal,
    instructions: Instructions,
  },
  methods: {
    createConnection() {
      this.connection_loading = true;
      this.show_connection = true;
      this.first_input_show = false;
      this.second_input_show = false;
    },
    hideInputElements() {
      this.show_connection_button = false;
      this.connection_loading = false;
      this.first_actor_show = false;
      this.second_actor_show = false;
      this.first_input_show = false;
      this.second_input_show = false;
      this.show_options_button = false;
    },
    resetInputs() {
      this.connection_loading = false;
      this.show_connection = false;
      this.show_connection_button = true;
      this.first_actor.name = '';
      this.first_actor.tmdb_id = '';
      this.first_actor.imdb_id = '';
      this.second_actor.name = '';
      this.second_actor.tmdb_id = '';
      this.second_actor.imdb_id = '';
      this.first_actor_show = false;
      this.second_actor_show = false;
      this.first_input_show = true;
      this.second_input_show = true;
      this.show_reset_button = false;
      this.show_top_button = false;
      this.show_options_button = true;
    },
    showPostConnectionButtons() {
      this.show_top_button = true;
      this.show_reset_button = true;
    },
    scrollToTop() {
      this.$smoothScroll({
        scrollTo: document.getElementById('top'),
      });
    },
  },
  computed: {
    showInstructions() {
      if (this.first_actor.name || this.second_actor.name) {
        return false;
      }
      return true;
    },
  },
  watch: {
    first_actor: {
      handler(newVal, oldVal) {
        if (oldVal.name === '' && newVal.name !== '') {
          setTimeout(() => {
            this.first_actor_show = true;
          }, 500);
          return;
        }
        if (oldVal.name !== '' && newVal.name === '') {
          setTimeout(() => {
            this.first_actor_show = false;
          }, 500);
          return;
        }
        if (oldVal.name !== '' && newVal.name !== '') {
          this.first_actor_show = false;
          setTimeout(() => {
            this.first_actor_show = true;
          }, 500);
          return;
        }
        this.first_actor_show = false;
      },
      // looking for changes within object
      deep: true,
    },
    second_actor: {
      handler(newVal, oldVal) {
        if (oldVal.name === '' && newVal.name !== '') {
          setTimeout(() => {
            this.second_actor_show = true;
          }, 500);
          return;
        }
        if (oldVal.name !== '' && newVal.name === '') {
          setTimeout(() => {
            this.second_actor_show = false;
          }, 500);
          return;
        }
        if (oldVal.name !== '' && newVal.name !== '') {
          this.second_actor_show = false;
          setTimeout(() => {
            this.second_actor_show = true;
          }, 500);
          return;
        }
        this.second_actor_show = false;
      },
      // looking for changes within object
      deep: true,
    },
  },
};
</script>

<style scoped>
  .fill-height {
    min-height: 95%;
    height: 95%;
  }
  .navbar-column {
    padding-left: 0;
    padding-right: 0;
  }
  .v-center {
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  .util-button {
    margin: 20px;
    width: 30%;
  }
  .options-modal {
    margin: 2em;
  }
</style>
