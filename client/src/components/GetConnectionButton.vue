<template>
  <div class="justify-content-center">
    <p class="h3 top-arrow">
      <b-icon-arrow-up shift-v="-5"></b-icon-arrow-up>
    </p>
    <b-button variant="outline-secondary"
              class="connect-button"
              @click="$emit('get-connection-button-clicked')"
              :disabled="loading"
    >
      <span v-if="!loading">Connect Actors</span>
      <span v-if="loading">Finding Connection ...</span>
      <b-img v-if="loading" src="/img/loading-connection.gif" width="100px" height="75px"></b-img>
    </b-button>
    <p class="h3 bottom-arrow">
      <b-icon-arrow-down shift-v="4"></b-icon-arrow-down>
    </p>
  </div>
</template>

<script>
export default {
  name: 'GetConnectionButton',
  props: ['loading'],
};
</script>

<style scoped>
  .connect-button {
    margin: 0;
    background-color: white;
    opacity: 100 !important;
    color: inherit;
  }
  .top-arrow {
    margin-bottom: 0;
  }
  .bottom-arrow {
    margin: 0;
    position: relative;
    z-index: -9999;
  }
</style>
