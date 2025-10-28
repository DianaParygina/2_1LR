import { createRouter, createWebHistory } from 'vue-router'
import DogsView from '../views/DogsView.vue'
import BreedsView from '../views/BreedsView.vue'
import OwnersView from '../views/OwnersView.vue'
import CountriesView from '../views/CountriesView.vue'
import HobbyView from '../views/HobbyView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [{
    path: "/",
    name: "DogsView",
    component: DogsView
  },
  {
    path: "/breeds",
    name: "BreedsView",
    component: BreedsView
  },
  {
    path: "/owners",
    name: "OwnersView",
    component: OwnersView
  },
  {
    path: "/countries",
    name: "CountriesView",
    component: CountriesView
  },
  {
    path: "/hobby",
    name: "HobbyView",
    component: HobbyView
  }
  ]
})

export default router
