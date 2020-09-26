<template>
  <div class="justify-content-center">
    <p class="h3" style="margin-bottom: 0">
      <b-icon-arrow-up shift-v="-5"></b-icon-arrow-up>
    </p>
    <b-button variant="outline-secondary"
              style="margin: 0;"
              @click="$emit('get-connection-button-clicked')"
              :disabled="loading"
    >
      <span v-if="!loading">Connect Actors</span>
      <span v-if="loading">Finding Connection ...</span>
      <b-img v-if="loading" src="/img/loading-connection.gif" width="100px" height="75px"></b-img>
    </b-button>
    <p class="h3" style="margin: 0">
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

</style>
