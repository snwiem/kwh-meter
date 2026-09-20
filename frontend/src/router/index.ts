import { createRouter, createWebHistory } from 'vue-router'
import MainScreen from '../views/MainScreen.vue'
import AddReadingView from '../views/AddReadingView.vue'
import ExportView from '../views/ExportView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: MainScreen },
    { path: '/add', component: AddReadingView },
    { path: '/export', component: ExportView },
  ],
})

export default router
