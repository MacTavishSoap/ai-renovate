import { createRouter, createWebHashHistory } from 'vue-router'
import Home from './views/Home.vue'
import LoginView from './views/admin/LoginView.vue'
import AdminLayout from './views/admin/AdminLayout.vue'
import { authed } from './admin/auth'
import AssetsView from './views/admin/AssetsView.vue'
import StaffView from './views/admin/StaffView.vue'
import PermissionsView from './views/admin/PermissionsView.vue'
import StudioView from './views/admin/StudioView.vue'

const HOME_TITLE = 'FORTUNE · 空间设计与整装'

// 哈希路由:打包后双击 index.html 也能直接打开,不依赖服务器配置
const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/login', component: LoginView, meta: { title: '登录' } },
    {
      path: '/admin',
      component: AdminLayout,
      redirect: '/admin/assets',
      children: [
        {
          path: 'assets', component: AssetsView,
          meta: { no: '01', en: 'ASSETS', title: '资产合集', desc: 'AI 生成的效果图,归谁、谁能看,一目了然' },
        },
        {
          path: 'staff', component: StaffView,
          meta: { no: '02', en: 'STAFF', title: '员工列表', desc: '谁能使用 AI 生图,在这里开关' },
        },
        {
          path: 'permissions', component: PermissionsView,
          meta: { no: '03', en: 'PERMISSIONS', title: '权限管理', desc: '每个角色能做什么,打开或关闭即可' },
        },
        {
          path: 'studio', component: StudioView,
          meta: { no: '04', en: 'AI STUDIO', title: 'AI 生图', desc: '从户型图到 3D 效果图,一站完成' },
        },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
  scrollBehavior: () => ({ top: 0, behavior: 'instant' }),
})

router.beforeEach((to) => {
  if (to.path.startsWith('/admin') && !authed.value) {
    return { path: '/login', query: { to: to.fullPath } }
  }
  if (to.path === '/login' && authed.value) return '/admin/assets'
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} · FORTUNE 工作台` : HOME_TITLE
})

export default router
