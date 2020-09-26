<template>
  <b-card border-variant="0">
    <b-card-body class="align-content-center" style="font-weight: bold">
      <div v-if="direction === 'down'">
        <span v-if="roles">
          ... who played
          <span style="white-space: nowrap;">{{roles}}</span>
          in ...
        </span>
        <span v-else>
          ... who acted in ...
        </span>
      </div>
      <div v-if="direction === 'up'">
        <span v-if="roles">
          ... which featured the character
          <span style="white-space: nowrap;">{{roles}},</span>
          played by ...
        </span>
        <span v-else>
          ... which also featured ...
        </span>
      </div>
    </b-card-body>
  </b-card>
</template>

<script>
export default {
  name: 'ActorRole',
  props: ['roles', 'direction'],
};
</script>
