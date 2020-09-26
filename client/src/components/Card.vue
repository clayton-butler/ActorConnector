<template>
  <b-card no-body
          class="overflow-hidden"
          border-variant="dark">
    <b-row no-gutters class="align-items-center flex-nowrap">
      <b-col md="6" class="mx-auto">
        <b-card-img :src="img_url"
                    :alt="img_alt_text"
                    class="rounded-0"
                    :style="is_default_img ? 'padding: 5px;' : ''">
        </b-card-img>
      </b-col>
      <b-col md="6">
        <b-card-body :title="title">
          <b-card-text>
            <slot></slot>
          </b-card-text>
        </b-card-body>
      </b-col>
    </b-row>
  </b-card>
</template>

<script>
export default {
  name: 'Card',
  props: [
    'img_url',
    'img_alt_text',
    'title',
    'is_default_img',
  ],
};
</script>

<style scoped>
  .card-img-left {
    max-width: 185px;
  }
</style>
