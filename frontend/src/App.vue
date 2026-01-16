/**
 * CampusAssetManager/frontend/src/App.vue
 * 应用根组件
 *
 * 功能说明：
 * - 集成通用布局组件
 * - 提供路由视图
 * - 处理全局样式
 *
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 */

<script setup>
import { onMounted } from 'vue'
import { useAppStore } from '@/stores'

/**
 * 应用状态管理
 */
const appStore = useAppStore()

/**
 * 组件挂载时初始化设备类型
 */
onMounted(() => {
  appStore.initDevice()
  
  /**
   * 监听窗口大小变化
   * 自动切换设备类型
   */
  window.addEventListener('resize', appStore.initDevice)
})
</script>

<template>
  <router-view />
</template>

<style>
/**
 * 全局样式重置与优化
 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  outline: none;
}

html,
body,
#app {
  width: 100%;
  height: 100%;
}

/**
 * 现代化的滚动条样式
 * 更加纤细，颜色更淡，减少视觉干扰
 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.15);
  border-radius: 3px;
  transition: background-color 0.3s;
}

::-webkit-scrollbar-thumb:hover {
  background-color: rgba(0, 0, 0, 0.3);
}

::-webkit-scrollbar-track {
  background-color: transparent;
}

/* 页面切换动画 - GPU加速优化 */
.router-view {
  /* 强制使用GPU渲染 */
  transform: translateZ(0);
  backface-visibility: hidden;
  perspective: 1000px;
  /* 预留动画资源 */
  will-change: opacity, transform;
}

.page-enter-active,
.page-leave-active {
  transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.page-enter-from {
  opacity: 0;
  transform: scale(0.95) translateY(20px);
}

.page-leave-to {
  opacity: 0;
  transform: scale(1.05);
}

/* 离开动画时绝对定位，避免布局抖动 */
.page-leave-active {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
}
</style>