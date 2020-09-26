<template>
  <header>
    <b-navbar variant="dark" type="dark" toggleable="lg" class="header-margin">
      <b-navbar-brand class="navbar-icon">
        Actor<b-icon-arrow-left-right></b-icon-arrow-left-right>Connector
      </b-navbar-brand>
      <b-navbar-toggle target="navbar-toggle-collapse">
      </b-navbar-toggle>
      <b-collapse id="navbar-toggle-collapse" is-nav>
        <b-navbar-nav align="start">
          <b-nav-item class="navbar-link" href="/">Home</b-nav-item>
          <b-nav-item class="navbar-link" href="/about">About</b-nav-item>
        </b-navbar-nav>
      </b-collapse>
    </b-navbar>
  </header>
</template>

<script>
export default {
  name: 'Header',
};
</script>

<style scoped>
  .navbar-icon {
    font-weight: bold;
    font-size: x-large;
  }
  .navbar-link {
    /*font-weight: bold;*/
    font-size: large;
  }
  .header-margin {
    margin-bottom: 10px;
  }
</style>
