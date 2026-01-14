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
    <aside class="layout-aside" :class="{ 'is-collapsed': sidebarCollapsed }">
      <div class="aside-header">
        <div class="logo-icon">
          <el-icon :size="20" color="#fff"><Odometer /></el-icon>
        </div>
        <span class="app-title" v-show="!sidebarCollapsed">校物通</span>
      </div>
      
      <div class="menu-wrapper">
        <el-menu
          :default-active="activeMenu"
          :collapse="sidebarCollapsed"
          :collapse-transition="false"
          router
          background-color="#001529"
          text-color="rgba(255, 255, 255, 0.65)"
          active-text-color="#ffffff"
          class="custom-menu"
        >
          <el-menu-item index="/home">
            <el-icon><Odometer /></el-icon>
            <template #title>工作台</template>
          </el-menu-item>
          
          <el-menu-item index="/goods">
            <el-icon><Goods /></el-icon>
            <template #title>物品管理</template>
          </el-menu-item>
          
          <el-menu-item index="/stock">
            <el-icon><Box /></el-icon>
            <template #title>库存管理</template>
          </el-menu-item>
          
          <el-menu-item index="/ledger">
            <el-icon><Document /></el-icon>
            <template #title>库存台账</template>
          </el-menu-item>
          
          <el-menu-item index="/check">
            <el-icon><DocumentChecked /></el-icon>
            <template #title>盘点管理</template>
          </el-menu-item>
          
          <el-menu-item index="/statistics">
            <el-icon><DataLine /></el-icon>
            <template #title>数据分析</template>
          </el-menu-item>
          
          <el-menu-item index="/logs">
            <el-icon><Clock /></el-icon>
            <template #title>操作日志</template>
          </el-menu-item>
          
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <template #title>系统设置</template>
          </el-menu-item>
        </el-menu>
      </div>
    </aside>

    <div class="layout-body">
      <header class="layout-header">
        <div class="header-left">
          <div class="trigger-btn" @click="toggleSidebar">
            <el-icon :size="20" color="#595959">
              <Fold v-if="!sidebarCollapsed" />
              <Expand v-else />
            </el-icon>
          </div>
          </div>
        
        <div class="header-right">
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-info-trigger">
              <el-avatar :size="32" :icon="UserFilled" class="user-avatar" />
              <div class="user-text">
                <span class="username">{{ username }}</span>
                <span class="role-badge">管理员</span>
              </div>
              <el-icon class="arrow-icon"><CaretBottom /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu class="user-dropdown">
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>个人中心
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>偏好设置
                </el-dropdown-item>
                <el-dropdown-item divided command="logout" style="color: #ff4d4f;">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>
      
      <main class="layout-main">
        <router-view v-slot="{ Component }">
          <transition name="fade-transform" mode="out-in">
            <component :is="Component" :key="$route.path" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores'
import {
  Fold, Expand, UserFilled, User, Setting, SwitchButton,
  Odometer, Goods, Box, DocumentChecked, DataLine, CaretBottom,
  Document, Clock
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const sidebarCollapsed = ref(false)
const activeMenu = computed(() => route.path)
const username = computed(() => userStore.username || 'Admin')

const toggleSidebar = () => { sidebarCollapsed.value = !sidebarCollapsed.value }

const handleCommand = (command) => {
  if (command === 'logout') {
    userStore.logout()
    router.push('/login')
  } else if (command === 'settings') {
    router.push('/settings')
  }
}
</script>

<style scoped>
.layout-container {
  display: flex;
  height: 100vh;
  width: 100%;
}

/* 侧边栏 */
.layout-aside {
  width: 240px; /* 稍微加宽，更大气 */
  background-color: #001529;
  display: flex;
  flex-direction: column;
  transition: width 0.3s cubic-bezier(0.2, 0, 0, 1);
  box-shadow: 2px 0 8px 0 rgba(29, 35, 41, 0.05);
  z-index: 20;
}

.layout-aside.is-collapsed {
  width: 64px;
}

.aside-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #002140; /* 略浅于侧边栏背景 */
  overflow: hidden;
  flex-shrink: 0;
}

.logo-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1677ff;
  border-radius: 6px;
  margin-right: 12px;
  transition: margin 0.3s;
}

.layout-aside.is-collapsed .logo-icon {
  margin-right: 0;
}

.app-title {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
  letter-spacing: 0.5px;
}

.menu-wrapper {
  flex: 1;
  padding: 16px 0;
  overflow-y: auto;
}

/* 菜单项优化 */
.custom-menu {
  border-right: none;
}

.custom-menu :deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
  margin: 4px 8px; /* 增加四周间距 */
  border-radius: 6px; /* 圆角菜单项 */
  width: auto;
}

.custom-menu :deep(.el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.08) !important;
}

/* 选中状态高亮 */
.custom-menu :deep(.el-menu-item.is-active) {
  background-color: #1677ff !important;
  color: #fff !important;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(22, 119, 255, 0.4);
}

.layout-aside.is-collapsed .custom-menu :deep(.el-menu-item) {
  margin: 4px 0; /* 折叠时去除左右间距 */
  border-radius: 0;
  display: flex;
  justify-content: center;
  padding: 0 !important;
}

/* 顶部 Header */
.layout-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
  min-width: 0;
}

.layout-header {
  height: 64px;
  background-color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02); /* 极简阴影 */
  z-index: 10;
}

.trigger-btn {
  padding: 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
  display: flex;
}

.trigger-btn:hover {
  background: rgba(0, 0, 0, 0.03);
}

.user-info-trigger {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: all 0.3s;
}

.user-info-trigger:hover {
  background: rgba(0, 0, 0, 0.03);
}

.user-avatar {
  background-color: #1677ff;
  border: 2px solid rgba(22, 119, 255, 0.1);
}

.user-text {
  display: flex;
  flex-direction: column;
  margin: 0 8px;
  line-height: 1.2;
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: #262626;
}

.role-badge {
  font-size: 11px;
  color: #8c8c8c;
}

.arrow-icon {
  font-size: 12px;
  color: #bfbfbf;
}

.layout-main {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  overflow-x: hidden;
}
</style>