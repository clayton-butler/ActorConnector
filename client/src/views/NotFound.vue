<template>
  <div class="notfound fill-height">
    <ac-header></ac-header>
    <b-container fluid>
      <b-row class="justify-content-center">
        <b-col>
          <h1>404</h1>
          <h2>Page Not Found</h2>
          <div class="fixed-bottom">
            <img src="img/confused_travolta.jpg" alt=""/>
          </div>
        </b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>
import Header from '@/components/Header.vue';

export default {
  name: 'NotFound',
  title: 'Page Not Found',
  components: {
    'ac-header': Header,
  },
};
</script>

<style scoped>
  .fill-height {
    min-height: 95%;
    height: 95%;
  }
</style>
