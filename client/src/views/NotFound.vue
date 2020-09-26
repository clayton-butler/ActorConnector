<template>
  <div class="notfound">
    <ac-header></ac-header>
    <b-container fluid>
      <b-row class="justify-content-center">
        <b-col></b-col>
        <b-col>
          <div style="bottom: 0; position: fixed">
            <h1>404</h1>
            <h2>Page Not Found</h2>
            <img src="img/confused_travolta.jpg" alt=""/>
          </div>
        </b-col>
        <b-col></b-col>
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

</style>
