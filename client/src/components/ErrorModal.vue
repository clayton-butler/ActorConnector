<template>
  <b-modal id="error-modal"
           centered
           title="Error"
           ok-only>
    <b-container fluid>
      <b-row>
        <b-col>
          <p>
            {{message}}
          </p>
        </b-col>
      </b-row>
    </b-container>
  </b-modal>
</template>

<script>
export default {
  name: 'ErrorModal',
  props: ['message'],
};
</script>

<style scoped>

</style>
