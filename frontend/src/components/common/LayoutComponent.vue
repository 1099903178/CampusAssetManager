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
  <el-container class="app-layout">
    <el-aside :width="isCollapse ? '64px' : '240px'" class="main-aside">
      <div class="aside-header" :class="{ 'collapsed': isCollapse }">
        <div class="logo-icon">
          <el-icon :size="22" color="white"><Odometer /></el-icon>
        </div>
        <transition name="fade">
          <span v-if="!isCollapse" class="app-title">校物通</span>
        </transition>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        class="aside-menu"
        :collapse="isCollapse"
        router
        unique-opened
        :collapse-transition="false"
      >
        <el-menu-item index="/home">
          <el-icon><DataBoard /></el-icon>
          <template #title>工作台</template>
        </el-menu-item>
        
        <el-menu-item index="/goods">
          <el-icon><Box /></el-icon>
          <template #title>物品管理</template>
        </el-menu-item>
        
        <el-menu-item index="/category">
          <el-icon><Folder /></el-icon>
          <template #title>分类管理</template>
        </el-menu-item>

        <el-sub-menu index="stock">
          <template #title>
            <el-icon><House /></el-icon>
            <span>库存管理</span>
          </template>
          <el-menu-item index="/stock">实时库存</el-menu-item>
          <el-menu-item index="/check">库存盘点</el-menu-item>
          <el-menu-item index="/ledger">库存台账</el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/statistics">
          <el-icon><TrendCharts /></el-icon>
          <template #title>数据分析</template>
        </el-menu-item>
        
        <el-sub-menu index="system" v-if="isAdmin">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统设置</span>
          </template>
          <el-menu-item index="/logs">操作日志</el-menu-item>
          <el-menu-item index="/database">数据维护</el-menu-item>
          <el-menu-item index="/settings">参数配置</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <el-container class="main-container">
      <el-header class="main-header">
        <div class="header-left">
          <div class="collapse-btn" @click="toggleCollapse">
            <el-icon :size="20" color="#64748b">
              <Fold v-if="!isCollapse" />
              <Expand v-else />
            </el-icon>
          </div>
          
          <el-breadcrumb separator="/" class="custom-breadcrumb">
            <el-breadcrumb-item :to="{ path: '/' }">
              <span class="breadcrumb-text">首页</span>
            </el-breadcrumb-item>
            <el-breadcrumb-item>
              <span class="breadcrumb-text active">{{ currentRouteName }}</span>
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <el-popover placement="bottom-end" :width="300" trigger="click">
            <template #reference>
              <div class="action-item">
                <el-badge is-dot class="notification-badge" type="danger">
                  <el-icon class="header-icon"><Bell /></el-icon>
                </el-badge>
              </div>
            </template>
            <div class="notify-box" style="padding: 10px;">
              <h4 style="margin: 0 0 10px 0; font-size: 14px; border-bottom: 1px solid #f1f5f9; padding-bottom: 8px;">系统通知</h4>
              <p style="font-size: 12px; color: #64748b;">暂无未读消息</p>
            </div>
          </el-popover>
          
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-profile">
              <el-avatar :size="32" class="user-avatar">
                {{ username.charAt(0).toUpperCase() }}
              </el-avatar>
              <span class="username">{{ username }}</span>
              <el-icon class="el-icon--right" color="#94a3b8"><CaretBottom /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu class="custom-dropdown">
                <el-dropdown-item command="profile"><el-icon><User /></el-icon>个人中心</el-dropdown-item>
                <el-dropdown-item divided command="logout" style="color: #ef4444;"><el-icon><SwitchButton /></el-icon>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
/**
 * 通用布局组件逻辑
 *
 * 导入模块：
 * - Vue Composition API：ref, computed
 * - Vue Router：useRouter, useRoute
 * - Pinia Store：useUserStore
 * - Element Plus 图标组件
 * - Element Plus 弹窗组件
 */
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores'
import {
  Odometer, DataBoard, Box, House, TrendCharts, Folder,
  Setting, Fold, Expand, Bell, CaretBottom, User, SwitchButton
} from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'

/**
 * Vue Router 实例
 */
const router = useRouter()
const route = useRoute()

/**
 * 用户状态管理 Store
 */
const userStore = useUserStore()

/**
 * 侧边栏折叠状态
 *
 * @type {Ref<boolean>}
 * - false: 展开状态（宽度 240px）
 * - true: 折叠状态（宽度 64px）
 */
const isCollapse = ref(false)

/**
 * 当前激活的菜单项
 *
 * 使用计算属性自动同步路由路径，确保菜单高亮状态正确
 *
 * @returns {string} 当前路由路径
 */
const activeMenu = computed(() => route.path)

/**
 * 用户名
 *
 * 从用户 Store 中获取当前登录用户的用户名
 * 如果未设置则显示默认值 'Admin'
 *
 * @returns {string} 用户名
 */
const username = computed(() => userStore.username || 'Admin')

/**
 * 是否为管理员
 *
 * 根据用户权限判断当前用户是否为管理员
 * 用于控制系统设置菜单的显示/隐藏
 *
 * @returns {boolean} true 表示管理员
 */
const isAdmin = computed(() => userStore.hasPermission('admin'))

/**
 * 当前路由名称
 *
 * 从路由元信息中获取页面标题，显示在面包屑导航中
 * 如果未设置则显示 '当前页面'
 *
 * @returns {string} 路由名称
 */
const currentRouteName = computed(() => route.meta.title || '当前页面')

/**
 * 切换侧边栏折叠状态
 *
 * 点击折叠按钮时触发，在展开和折叠状态之间切换
 *
 * 设计原则：
 * - 响应式：使用 ref 管理折叠状态
 * - 用户体验：平滑的过渡动画（CSS 中定义）
 */
const toggleCollapse = () => { isCollapse.value = !isCollapse.value }

/**
 * 处理用户下拉菜单命令
 *
 * 处理用户头像下拉菜单中的操作命令
 *
 * @param {string} command - 命令类型
 *   - 'logout': 退出登录
 *   - 'profile': 个人中心（暂未实现）
 *
 * 业务逻辑：
 * - logout: 显示确认对话框，用户确认后清除登录状态并跳转到登录页
 * - 使用 ElMessageBox confirm 确保用户意图，提供更清晰的提示信息
 * - 调用 userStore.logout() 清除登录状态
 * - 使用 router.push('/login') 跳转到登录页
 */
const handleCommand = (command) => {
  if (command === 'logout') {
    ElMessageBox.confirm(
      '退出登录后，您需要重新输入用户名和密码才能访问系统。',
      '确定退出登录吗?',
      {
        confirmButtonText: '确定退出',
        cancelButtonText: '取消',
        type: 'warning',
        customClass: 'logout-confirm-dialog'
      }
    )
      .then(() => {
        // 清除登录状态
        userStore.logout()
        // 跳转到登录页
        router.push('/login')
      })
      .catch(() => {
        // 用户取消退出
      })
  }
}
</script>

<style scoped>
.app-layout { height: 100vh; background-color: #f8fafc; }

/* 侧边栏样式 */
.main-aside {
  background-color: #ffffff;
  border-right: 1px solid #f1f5f9;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  z-index: 20;
  box-shadow: 4px 0 24px rgba(0,0,0,0.02);
}

.aside-header { height: 64px; display: flex; align-items: center; padding: 0 24px; }
.aside-header.collapsed { padding: 0; justify-content: center; }

.logo-icon {
  width: 36px; height: 36px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
}

.app-title {
  font-size: 18px; font-weight: 800; color: #1e293b;
  margin-left: 12px; letter-spacing: 0.5px; white-space: nowrap;
}

.aside-menu { border-right: none; flex: 1; padding: 0 12px; overflow-y: auto; }

/* 菜单项深度优化 */
:deep(.el-menu-item), :deep(.el-sub-menu__title) {
  height: 48px; line-height: 48px; margin-bottom: 4px;
  border-radius: 10px; color: #64748b; font-weight: 500;
}

:deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, #eff6ff 0%, #f8fafc 100%);
  color: #2563eb; font-weight: 600; position: relative;
}

:deep(.el-menu-item.is-active::before) {
  content: ''; position: absolute; left: 0; top: 12px; bottom: 12px;
  width: 4px; background: #2563eb; border-radius: 0 4px 4px 0;
}

/* 顶部导航 */
.main-header {
  background-color: rgba(255, 255, 255, 0.85); backdrop-filter: blur(12px);
  height: 64px; display: flex; align-items: center; justify-content: space-between;
  padding: 0 24px; box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03);
  position: sticky; top: 0; z-index: 10;
}

.header-left { display: flex; align-items: center; gap: 20px; }
.collapse-btn { cursor: pointer; color: #64748b; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; border-radius: 10px; transition: 0.2s; }
.collapse-btn:hover { background: #f1f5f9; }

.header-right { display: flex; align-items: center; gap: 20px; }
.action-item { cursor: pointer; color: #64748b; width: 38px; height: 38px; display: flex; align-items: center; justify-content: center; border-radius: 12px; transition: 0.2s; }
.action-item:hover { background: #eff6ff; color: #2563eb; }

.user-profile { display: flex; align-items: center; gap: 12px; cursor: pointer; padding: 6px 12px; border-radius: 30px; transition: 0.2s; border: 1px solid transparent; }
.user-profile:hover { background: white; border-color: #e2e8f0; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.user-avatar { background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; font-weight: 600; font-size: 14px; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.username { font-size: 14px; font-weight: 600; color: #1e293b; }

/* 动画效果 */
.fade-slide-enter-active, .fade-slide-leave-active { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.fade-slide-enter-from { opacity: 0; transform: translateY(10px); }
.fade-slide-leave-to { opacity: 0; transform: translateY(-10px); }
</style>

<!-- 退出登录确认对话框自定义样式 -->
<style>
/* 确认对话框 - 强制圆角 */
.logout-confirm-dialog.el-message-box,
.el-overlay-message-box .el-message-box.logout-confirm-dialog {
  border-radius: 20px !important;
  overflow: hidden !important;
  border: 1px solid #e5e7eb !important;
}

/* 确认对话框标题 */
.logout-confirm-dialog .el-message-box__title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

/* 确认对话框内容 */
.logout-confirm-dialog .el-message-box__message {
  font-size: 14px;
  color: #64748b;
  line-height: 1.6;
}

/* 按钮区域 */
.logout-confirm-dialog .el-message-box__btns {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 所有按钮统一样式 - 更大的圆角 */
.logout-confirm-dialog .el-button {
  padding: 9px 20px;
  border-radius: 12px;
  font-weight: 500;
  font-size: 14px;
  transition: all 0.2s;
}

/* 取消按钮悬停效果 */
.logout-confirm-dialog .el-button--default:not(.is-primary):hover {
  background-color: #f1f5f9;
  border-color: #cbd5e1;
  color: #475569;
}

/* 确认退出按钮 - 红色（强制覆盖） */
.logout-confirm-dialog .el-button--primary,
.el-overlay-message-box .logout-confirm-dialog .el-button--primary {
  background: #ef4444 !important;
  border-color: #ef4444 !important;
  color: white !important;
}

.logout-confirm-dialog .el-button--primary:hover,
.el-overlay-message-box .logout-confirm-dialog .el-button--primary:hover {
  background: #dc2626 !important;
  border-color: #dc2626 !important;
}
</style>