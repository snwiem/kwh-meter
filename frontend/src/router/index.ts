import { createRouter, createWebHistory } from 'vue-router'
import MainScreen from '../views/MainScreen.vue'
import AddReadingView from '../views/AddReadingView.vue'
import ExportView from '../views/ExportView.vue'
import ReadingDetailView from '../views/ReadingDetailView.vue'
import EditReadingView from '../views/EditReadingView.vue'
import AnalyticsView from '../views/AnalyticsView.vue'
import NotificationsView from '../views/NotificationsView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: MainScreen },
    { path: '/add', component: AddReadingView },
    { path: '/export', component: ExportView },
    { path: '/analytics', component: AnalyticsView },
    { path: '/notifications', component: NotificationsView },
    { path: '/readings/:id', component: ReadingDetailView },
    { path: '/readings/:id/edit', component: EditReadingView },
  ],
})

export default router
