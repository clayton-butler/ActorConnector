<template>
  <div>
    <b-card v-show="show_single_actor_message" border-variant="0">
      <b-card-body v-if="connections.length"
                   class="align-content-center"
                   style="font-weight: bold;">
        {{connections[0].name}} is ... {{connections[0].name}}
      </b-card-body>
    </b-card>
    <b-card v-show="show_no_connection_message" border-variant="0">
      <b-card-body>
        Could not find a connection. Try increasing the max search depth.
      </b-card-body>
    </b-card>
    <div v-if="!is_small_connection">
      <b-collapse v-for="(item, index) in connections"
                  :key="index"
                  :id="`connection-${index}`"
                  v-model="item.show"
      >
        <static-actor-card v-if="item.type === 'actor'"
                           :name="item.name"
                           :img_url="item.img_url"
                           :birth_year="item.birth_year"
                           :death_year="item.death_year"
                           :movie_count="item.movie_count"
                           :episode_count="item.episode_count"
                           :series_count="item.series_count"
        />
        <static-movie-card v-else-if="item.type === 'movie'"
                           :title="item.title"
                           :img_url="item.img_url"
                           :year="item.year"
        />
        <static-episode-card v-else-if="item.type === 'episode'"
                             :title="item.parent_series"
                             :img_url="item.img_url"
                             :year="item.year"
                             :episode_num="item.episode_num"
                             :season_num="item.season_num"
        />
        <actor-role v-else-if="item.type === 'role'"
                    :roles="item.roles"
                    :direction="item.direction"
        />
      </b-collapse>
    </div>
    <div v-if="is_small_connection">
      <b-collapse v-for="(item, index) in connections"
                  :key="index"
                  :id="`connection-${index}}`"
                  v-model="item.show"
      >
        <small-card v-if="item.type === 'actor'" :card_type="item.type">
          {{item.name}}
        </small-card>
        <div v-else-if="item.type === 'role'">
          <span v-if="item.direction === 'up'">
            <b-icon-arrow-up></b-icon-arrow-up>
          </span>
          <span v-else-if="item.direction === 'down'">
            <b-icon-arrow-down></b-icon-arrow-down>
          </span>
        </div>
        <small-card v-else-if="item.type === 'movie'" :card_type="item.type">
          {{item.title}}
        </small-card>
        <small-card v-else-if="item.type === 'episode'" :card_type="item.type">
          {{item.parent_series}}
          <div v-if="item.episode_num && item.season_num">
            S{{item.season_num}}E{{item.episode_num}}
          </div>
        </small-card>
      </b-collapse>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import StaticActorCard from '@/components/StaticActorCard.vue';
import StaticMovieCard from '@/components/StaticMovieCard.vue';
import StaticEpisodeCard from '@/components/StaticEpisodeCard.vue';
import ActorRole from '@/components/ActorRole.vue';
import SmallCard from '@/components/SmallCard.vue';

export default {
  name: 'Connection',
  components: {
    'static-actor-card': StaticActorCard,
    'static-movie-card': StaticMovieCard,
    'static-episode-card': StaticEpisodeCard,
    'actor-role': ActorRole,
    'small-card': SmallCard,
  },
  inject: ['global_api_url'],
  props: [
    'show_connection',
    'first_actor_id',
    'second_actor_id',
    'max_search_depth',
    'is_small_connection',
    'enable_animations',
  ],
  data() {
    return {
      connections: [],
      steps: 0,
      show_single_actor_message: false,
      show_no_connection_message: false,
    };
  },
  watch: {
    show_connection() {
      this.show_single_actor_message = false;
      this.show_no_connection_message = false;
      if (this.show_connection && this.first_actor_id && this.second_actor_id) {
        this.create_connection(this.first_actor_id, this.second_actor_id);
      } else {
        this.destroy_connection();
      }
    },
  },
  methods: {
    create_connection() {
      const path = `${this.global_api_url}/actor/connection/${this.first_actor_id}/${this.second_actor_id}/${this.max_search_depth}`;
      axios.get(path)
        .then((res) => {
          this.connections = res.data.connection;
          this.steps = res.data.steps;
          this.$emit('update:connections', this.connections);
        })
        .catch((error) => {
          console.log(error);
        })
        .then(() => {
          if (this.connections.length === 0) {
            this.show_no_connection_message = true;
            this.$emit('connection-load-complete');
            this.$emit('connection-animation-complete');
          } else if (this.is_small_connection) {
            this.connections.forEach((el, idx) => {
              this.connections[idx].show = true;
              this.$emit('connection-load-complete');
              this.$emit('connection-animation-complete');
            });
          } else {
            this.display_connection();
          }
        });
    },
    destroy_connection() {
      this.connections = [];
    },
    animate_timeout(time) {
      return new Promise((res) => setTimeout(res, time * (this.enable_animations ? 1 : 0)));
    },
    async display_connection() {
      this.$emit('connection-load-complete');
      await this.animate_timeout(1000);
      if (this.connections.length === 1) {
        this.show_single_actor_message = true;
        this.connections[0].show = true;
        this.$emit('connection-animation-complete');
        return;
      }
      for (let i = 0; i < this.connections.length; i += 1) {
        await this.animate_timeout(1000); // eslint-disable-line no-await-in-loop
        this.connections[i].show = true;
        await this.animate_timeout(500); // eslint-disable-line no-await-in-loop
        if (this.enable_animations) {
          this.$smoothScroll({
            scrollTo: document.getElementById(`connection-${i}`),
            offset: 100,
          });
        }
      }
      this.$router.replace('');
      this.$emit('connection-animation-complete');
    },
  },
};
</script>
