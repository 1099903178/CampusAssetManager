/**
 * CampusAssetManager/frontend/src/main.js
 * 应用主入口文件
 *
 * 功能说明：
 * - 创建Vue应用实例
 * - 集成Element Plus和Vant组件库
 * - 配置Vue Router路由
 * - 配置Pinia状态管理
 * - 注册全局组件和指令
 *
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 */

import { createApp } from 'vue'
import App from './App.vue'
import './style.css'

/**
 * 引入路由配置
 */
import router from './router'

/**
 * 引入状态管理
 */
import { createPinia } from 'pinia'

/**
 * 引入Element Plus
 */
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

/**
 * 引入Vant（移动端组件库）
 */
import Vant from 'vant'
import 'vant/lib/index.css'

/**
 * 创建应用实例
 */
const app = createApp(App)

/**
 * 注册Element Plus
 */
app.use(ElementPlus)

/**
 * 注册Element Plus图标
 */
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

/**
 * 注册Vant（移动端）
 */
app.use(Vant)

/**
 * 注册路由
 */
app.use(router)

/**
 * 注册Pinia状态管理
 */
const pinia = createPinia()
app.use(pinia)

/**
 * 挂载应用
 */
app.mount('#app')
