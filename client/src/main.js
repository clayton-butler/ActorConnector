import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-vue/dist/bootstrap-vue.css';
import { BootstrapVue, BootstrapVueIcons } from 'bootstrap-vue';
import Vue2SmoothScroll from 'vue2-smooth-scroll';
import VuePageTitle from 'vue-page-title';
import Vue from 'vue';
import App from './App.vue';
import router from './router';

Vue.use(BootstrapVue);
Vue.use(BootstrapVueIcons);
Vue.use(Vue2SmoothScroll);
Vue.use(VuePageTitle, {
  prefix: 'Actor Connector - ',
});

Vue.config.productionTip = false;

new Vue({
  router,
  render: (h) => h(App),
  provide: {
    global_base_url: process.env.VUE_APP_BASEURL,
    global_api_url: process.env.VUE_APP_APIURL,
  },
}).$mount('#app');
