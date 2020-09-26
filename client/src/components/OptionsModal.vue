<template>
  <div>
    <b-button v-b-modal.options-modal>
      <b-icon-gear scale="0.9"></b-icon-gear> Options
    </b-button>
    <b-modal id="options-modal"
             centered
             title="Options"
             ok-only
             @hide="checkMaxDepth"
    >
      <b-container fluid>
        <b-row no-gutters>
          <b-col cols="2" align="center">
            <b-form-checkbox v-model="is_small_connection"
                             id="small-connection-switch"
                             switch
                             size="lg">
            </b-form-checkbox>
          </b-col>
          <b-col>
            <label for="small-connection-switch" class="input-label">
              Text Only Display
            </label>
          </b-col>
        </b-row>
        <b-row no-gutters>
          <b-col cols="2" align="center">
            <b-form-checkbox v-model="enable_animations"
                             id="animations-switch"
                             switch
                             size="lg">
            </b-form-checkbox>
          </b-col>
          <b-col>
            <label for="animations-switch" class="input-label">
              Animated Connection Reveal
            </label>
          </b-col>
        </b-row>
        <b-row no-gutters>
          <b-col cols="2">
            <ValidationProvider ref="max_depth_validator"
                                rules="required|numeric|min_value:1|max_value:50"
                                v-slot="{ errors }">
              <b-form-input v-model="max_search_depth"
                            id="search-depth-input"
                            size="sm"
              ></b-form-input>
              <span class="input-error">{{ errors[0] }}</span>
            </ValidationProvider>
          </b-col>
          <b-col>
            <label for="search-depth-input" class="input-label">
             Max Search Depth
            </label>
          </b-col>
        </b-row>
      </b-container>
    </b-modal>
  </div>
</template>

<script>
import { ValidationProvider, extend } from 'vee-validate';
import { required, numeric, min_value, max_value } from 'vee-validate/dist/rules' // eslint-disable-line

extend('required', {
  ...required,
  message: 'Field cannot be blank',
});
extend('numeric', {
  ...numeric,
  message: 'Must be a positive number',
});
extend('min_value', {
  ...min_value, // eslint-disable-line
  message: 'Must be at least 1',
});
extend('max_value', {
  ...max_value, // eslint-disable-line
  message: 'Cannot be greater than 50',
});

export default {
  name: 'OptionsModal',
  components: {
    ValidationProvider,
  },
  data() {
    return {
      is_small_connection: false,
      enable_animations: true,
      max_search_depth: 20,
    };
  },
  methods: {
    checkMaxDepth() {
      if (this.$refs.max_depth_validator.flags.valid) {
        this.$emit('update:max_search_depth', this.max_search_depth);
      } else {
        this.max_search_depth = 20;
      }
    },
  },
  watch: {
    is_small_connection() {
      this.$emit('update:is_small_connection', this.is_small_connection);
    },
    enable_animations() {
      this.$emit('update:enable_animations', this.enable_animations);
    },
  },
};
</script>

<style scoped>
  .input-error {
    color: red;
  }
  .input-label {
    /*style="margin-left: 0.25em; font-size: 1.25em; line-height: 1.5"*/
    margin-left: 0.25em;
    font-size: 1.25em;
    line-height: 1.5;
  }
</style>
