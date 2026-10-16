import { createRouter, createWebHashHistory } from 'vue-router'
import Home from './views/Home.vue'
import AdminLayout from './views/admin/AdminLayout.vue'
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
    {
      path: '/admin',
      component: AdminLayout,
      redirect: '/admin/assets',
      children: [
        {
          path: 'assets', component: AssetsView,
          meta: { no: '01', en: 'ASSETS', title: '资产合集', desc: '私人客户资产与公共演示资产统一管理。每件资产都可以多次编辑,并回溯到任意历史版本。' },
        },
        {
          path: 'staff', component: StaffView,
          meta: { no: '02', en: 'STAFF', title: '员工列表', desc: '员工账号、角色,以及单独开通的功能页面入口。' },
        },
        {
          path: 'permissions', component: PermissionsView,
          meta: { no: '03', en: 'PERMISSIONS', title: '权限管理', desc: '按角色配置功能页面、资产与客户的使用范围,业务人员的权限在这里统一管理。' },
        },
        {
          path: 'studio', component: StudioView,
          meta: { no: '04', en: 'STUDIO', title: '生图工坊', desc: '基于生图的功能页面入口,目前为占位。' },
        },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
  scrollBehavior: () => ({ top: 0, behavior: 'instant' }),
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} · FORTUNE 工作台` : HOME_TITLE
})

export default router
