/**
 * CampusAssetManager/frontend/src/views/HomeView.vue
 * 首页
 * 
 * 功能说明：
 * - 显示系统概览信息
 * - 显示快捷操作入口
 * - 显示系统公告
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 */

<template>
  <LayoutComponent>
    <div class="home-container">
      <el-row :gutter="20">
        <!-- 统计卡片 -->
        <el-col :span="6" v-for="stat in statistics" :key="stat.title">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" :style="{ background: stat.color }">
                <el-icon :size="32">
                  <component :is="stat.icon" />
                </el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stat.value }}</div>
                <div class="stat-label">{{ stat.title }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 快捷操作 -->
      <el-card class="quick-actions" style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <span>快捷操作</span>
          </div>
        </template>
        <div class="action-buttons">
          <el-button
            v-for="action in actions"
            :key="action.name"
            :type="action.type"
            @click="handleAction(action.path)"
          >
            <el-icon class="action-icon">
              <component :is="action.icon" />
            </el-icon>
            {{ action.name }}
          </el-button>
        </div>
      </el-card>
      
      <!-- 系统公告 -->
      <el-card class="system-notice" style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <span>系统公告</span>
          </div>
        </template>
        <el-timeline>
          <el-timeline-item
            v-for="(notice, index) in notices"
            :key="index"
            :timestamp="notice.date"
            placement="top"
          >
            <el-card>
              <h4>{{ notice.title }}</h4>
              <p>{{ notice.content }}</p>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </div>
  </LayoutComponent>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores'
import LayoutComponent from '@/components/common/LayoutComponent.vue'
import {
  Box,
  ShoppingCart,
  DocumentChecked,
  DataLine
} from '@element-plus/icons-vue'

/**
 * 路由实例
 */
const router = useRouter()

/**
 * 用户Store
 */
const userStore = useUserStore()

/**
 * 统计数据
 */
const statistics = [
  {
    title: '物品总数',
    value: '1,234',
    icon: Box,
    color: '#409eff'
  },
  {
    title: '今日入库',
    value: '56',
    icon: ShoppingCart,
    color: '#67c23a'
  },
  {
    title: '今日出库',
    value: '23',
    icon: DocumentChecked,
    color: '#e6a23c'
  },
  {
    title: '盘点次数',
    value: '8',
    icon: DataLine,
    color: '#f56c6c'
  }
]

/**
 * 快捷操作
 */
const actions = [
  {
    name: '物品管理',
    path: '/goods',
    icon: Box,
    type: 'primary'
  },
  {
    name: '库存管理',
    path: '/stock',
    icon: ShoppingCart,
    type: 'success'
  },
  {
    name: '盘点管理',
    path: '/check',
    icon: DocumentChecked,
    type: 'warning'
  },
  {
    name: '统计报表',
    path: '/statistics',
    icon: DataLine,
    type: 'danger'
  }
]

/**
 * 系统公告
 */
const notices = [
  {
    title: '系统升级通知',
    content: '系统将于本周六凌晨2:00进行升级维护，预计持续2小时，请提前做好数据备份。',
    date: '2026-01-05'
  },
  {
    title: '新功能发布',
    content: '系统新增了移动端适配功能，支持手机访问。欢迎大家使用并提出宝贵意见。',
    date: '2026-01-04'
  },
  {
    title: '数据安全提醒',
    content: '请定期修改密码，确保账户安全。建议使用包含字母、数字和特殊字符的复杂密码。',
    date: '2026-01-03'
  }
]

/**
 * 处理快捷操作
 * 
 * @param {string} path - 跳转路径
 */
const handleAction = (path) => {
  router.push(path)
}
</script>

<style scoped>
.home-container {
  padding: 20px;
}

/**
 * 统计卡片
 */
.stat-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #fff;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

/**
 * 卡片头部
 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
}

/**
 * 快捷操作按钮
 */
.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.action-button {
  width: 120px;
  height: 80px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 8px;
}

.action-icon {
  font-size: 24px;
}

/**
 * 系统公告
 */
.system-notice h4 {
  margin-bottom: 8px;
  color: #303133;
}

.system-notice p {
  color: #606266;
  line-height: 1.6;
}
</style>