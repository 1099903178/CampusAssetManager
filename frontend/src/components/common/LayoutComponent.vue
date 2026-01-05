/**
 * CampusAssetManager/frontend/src/components/common/LayoutComponent.vue
 * 通用布局组件（PC端）
 * 
 * 功能说明：
 * - 提供通用的页面布局结构
 * - 包含顶部导航栏、侧边栏、内容区域
 * - 支持侧边栏折叠/展开
 * - 响应式布局适配
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 */

<template>
  <div class="layout-container">
    <!-- 顶部导航栏 -->
    <header class="layout-header">
      <div class="header-left">
        <el-icon
          class="collapse-icon"
          @click="toggleSidebar"
          :class="{ 'is-collapsed': sidebarCollapsed }"
        >
          <Fold v-if="!sidebarCollapsed" />
          <Expand v-else />
        </el-icon>
        <div class="header-title">校物通 - 校园物品管理系统</div>
      </div>
      
      <div class="header-right">
        <!-- 用户信息下拉菜单 -->
        <el-dropdown @command="handleCommand">
          <div class="user-info">
            <el-avatar :size="32" :icon="UserFilled" />
            <span class="username">{{ username }}</span>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon>
                个人信息
              </el-dropdown-item>
              <el-dropdown-item command="settings">
                <el-icon><Setting /></el-icon>
                系统设置
              </el-dropdown-item>
              <el-dropdown-item divided command="logout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>
    
    <div class="layout-body">
      <!-- 侧边栏 -->
      <aside class="layout-aside" :class="{ 'is-collapsed': sidebarCollapsed }">
        <el-menu
          :default-active="activeMenu"
          :collapse="sidebarCollapsed"
          :collapse-transition="false"
          router
          background-color="#545c64"
          text-color="#fff"
          active-text-color="#ffd04b"
        >
          <el-menu-item index="/">
            <el-icon><Odometer /></el-icon>
            <span>首页</span>
          </el-menu-item>
          
          <el-menu-item index="/goods">
            <el-icon><Goods /></el-icon>
            <span>物品管理</span>
          </el-menu-item>
          
          <el-menu-item index="/stock">
            <el-icon><Box /></el-icon>
            <span>库存管理</span>
          </el-menu-item>
          
          <el-menu-item index="/check">
            <el-icon><DocumentChecked /></el-icon>
            <span>盘点管理</span>
          </el-menu-item>
          
          <el-menu-item index="/statistics">
            <el-icon><DataLine /></el-icon>
            <span>统计报表</span>
          </el-menu-item>
          
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <span>系统设置</span>
          </el-menu-item>
        </el-menu>
      </aside>
      
      <!-- 主内容区域 -->
      <main class="layout-main">
        <el-scrollbar>
          <router-view v-slot="{ Component }">
            <transition name="fade-transform" mode="out-in">
              <component :is="Component" :key="$route.path" />
            </transition>
          </router-view>
        </el-scrollbar>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores'
import {
  Fold,
  Expand,
  UserFilled,
  User,
  Setting,
  SwitchButton,
  Odometer,
  Goods,
  Box,
  DocumentChecked,
  DataLine
} from '@element-plus/icons-vue'

/**
 * 路由实例
 */
const router = useRouter()
const route = useRoute()

/**
 * 用户Store
 */
const userStore = useUserStore()

/**
 * 侧边栏是否折叠
 */
const sidebarCollapsed = ref(false)

/**
 * 当前激活的菜单
 */
const activeMenu = computed(() => route.path)

/**
 * 用户名
 */
const username = computed(() => userStore.username || '未登录')

/**
 * 切换侧边栏状态
 */
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

/**
 * 处理下拉菜单命令
 * 
 * @param {string} command - 命令
 */
const handleCommand = (command) => {
  switch (command) {
    case 'profile':
      // 跳转到个人信息页面
      break
    case 'settings':
      router.push('/settings')
      break
    case 'logout':
      logout()
      break
  }
}

/**
 * 退出登录
 */
const logout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style scoped>
/**
 * 布局容器
 */
.layout-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

/**
 * 顶部导航栏
 */
.layout-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
  padding: 0 20px;
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

/**
 * 头部左侧
 */
.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

/**
 * 折叠图标
 */
.collapse-icon {
  font-size: 20px;
  cursor: pointer;
  transition: transform 0.3s;
}

.collapse-icon:hover {
  color: #409eff;
}

.collapse-icon.is-collapsed {
  transform: rotate(180deg);
}

/**
 * 头部标题
 */
.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

/**
 * 头部右侧
 */
.header-right {
  display: flex;
  align-items: center;
}

/**
 * 用户信息
 */
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  font-size: 14px;
  color: #606266;
}

/**
 * 布局主体
 */
.layout-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/**
 * 侧边栏
 */
.layout-aside {
  width: 200px;
  overflow-x: hidden;
  overflow-y: auto;
  background-color: #545c64;
  transition: width 0.3s;
}

.layout-aside.is-collapsed {
  width: 64px;
}

/**
 * 主内容区域
 */
.layout-main {
  flex: 1;
  padding: 20px;
  background-color: #f5f7fa;
}

/**
 * 页面切换动画
 */
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>