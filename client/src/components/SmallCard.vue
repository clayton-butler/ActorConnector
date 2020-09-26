<template>
  <b-card :border-variant="color_variant" align="center">
    <b-card-text>
      <slot></slot>
    </b-card-text>
  </b-card>
</template>

<script>
export default {
  name: 'SmallCard',
  props: ['card_type'],
  computed: {
    color_variant() {
      if (this.card_type === 'actor') {
        return 'info';
      }
      return 'success';
    },
  },
};
</script>

<style scoped>

</style>
