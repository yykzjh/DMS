import Vue from 'vue'
import VueRouter from 'vue-router'
import VueMeta from 'vue-meta'

import store from '@/state/store'
import routes from './routes'

Vue.use(VueRouter)
Vue.use(VueMeta, {
  // The component option name that vue-meta looks for meta info on.
  keyName: 'page',
})

const router = new VueRouter({
  routes,
  // Use the HTML5 history API (i.e. normal-looking routes)
  // instead of routes with hashes (e.g. example.com/#/about).
  // This may require some server configuration in production:
  // https://router.vuejs.org/en/essentials/history-mode.html#example-server-configurations
  mode: 'history',
  // Simulate native-like scroll behavior when navigating to a new
  // route and using back/forward buttons.
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { x: 0, y: 0 }
    }
  },
})

// Before each route evaluates...
router.beforeEach((routeTo, routeFrom, next) => {
  
  const authRequired = routeTo.matched.some((route) => route.meta.authRequired)

  // console.log(1)
  // If auth isn't required for the route, just continue.
  if (!authRequired) return next()

  // console.log(2)
  if (store.getters['auth/loggedIn']) {
    // console.log(3)
    return store.dispatch('auth/validate').then((res) => {
      let data = res.data
      data.errcode == 0 ? next() : redirectToLogin()
    })
  }
  
  redirectToLogin()

  function redirectToLogin() {
    next({ name: 'login', query: { redirectFrom: routeTo.fullPath } })
  }
})

export default router
