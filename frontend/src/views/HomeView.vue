/**
 * CampusAssetManager/frontend/src/views/HomeView.vue
 * 首页
 * 
 * 功能说明：
 * - 显示系统概览信息
 * - 显示快捷操作入口
 * - 显示系统公告
 * - 支持数据刷新
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 * 更新日期：2026-01-09
 */

<template>
  <div class="home-container">
      <!-- 统计卡片区域 -->
      <el-card class="statistics-card">
        <template #header>
          <div class="card-header">
            <span>数据概览</span>
            <el-button
              type="primary"
              :icon="RefreshRight"
              @click="refreshData"
              :loading="loading"
              size="small"
              circle
            />
          </div>
        </template>
        
        <el-row :gutter="20" class="stat-row">
          <!-- 统计卡片 -->
          <el-col :xs="24" :sm="12" :md="12" :lg="6" :xl="6" v-for="stat in statistics" :key="stat.title">
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
        
        <!-- 数据更新时间 -->
        <div v-if="updateTime" class="update-time">
          数据更新时间：{{ updateTime }}
        </div>
      </el-card>
      
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
            class="action-button"
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
</template>

<script setup>
import { ref, onMounted, markRaw } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Box, ShoppingCart, DocumentChecked, WarningFilled, RefreshRight } from '@element-plus/icons-vue'
import { getDataOverview } from '@/api/statistics'

/**
 * 路由实例
 */
const router = useRouter()

/**
 * 统计数据
 */
const statistics = ref([
  {
    title: '物品总数',
    value: '0',
    icon: markRaw(Box),
    color: '#409eff'
  },
  {
    title: '库存总数',
    value: '0',
    icon: markRaw(ShoppingCart),
    color: '#67c23a'
  },
  {
    title: '今日入库',
    value: '0',
    icon: markRaw(DocumentChecked),
    color: '#e6a23c'
  },
  {
    title: '今日出库',
    value: '0',
    icon: markRaw(DocumentChecked),
    color: '#909399'
  },
  {
    title: '预警数量',
    value: '0',
    icon: markRaw(WarningFilled),
    color: '#f56c6c'
  }
])

/**
 * 数据更新时间
 */
const updateTime = ref('')

/**
 * 加载状态
 */
const loading = ref(false)

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
    icon: ShoppingCart,
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
    content: '系统新增了数据概览功能，支持实时统计物品总数、库存总数、今日入库出库量和预警数量。',
    date: '2026-01-09'
  },
  {
    title: '数据安全提醒',
    content: '请定期修改密码，确保账户安全。建议使用包含字母、数字和特殊字符的复杂密码。',
    date: '2026-01-03'
  }
]

/**
 * 获取统计数据
 */
const loadStatistics = async () => {
  try {
    loading.value = true
    const response = await getDataOverview()
    
    // request.js的响应拦截器已经提取了data字段，所以response就是数据对象本身
    if (response && response.total_goods !== undefined) {
      // 更新统计数据
      statistics.value[0].value = response.total_goods?.toLocaleString() || '0'
      statistics.value[1].value = response.total_stock?.toLocaleString() || '0'
      statistics.value[2].value = response.today_stock_in?.toLocaleString() || '0'
      statistics.value[3].value = response.today_stock_out?.toLocaleString() || '0'
      statistics.value[4].value = response.warning_count?.toLocaleString() || '0'
      
      // 更新时间
      updateTime.value = response.update_time || ''
      
      ElMessage.success('数据加载成功')
    } else {
      ElMessage.error('获取统计数据失败')
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
    ElMessage.error('获取统计数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

/**
 * 刷新数据
 */
const refreshData = () => {
  loadStatistics()
}

/**
 * 处理快捷操作
 * 
 * @param {string} path - 跳转路径
 */
const handleAction = (path) => {
  router.push(path)
}

/**
 * 组件挂载时加载统计数据
 */
onMounted(() => {
  loadStatistics()
})
</script>

<style scoped>
.home-container {
  width: 100%;
  /* 设置最大宽度限制，使内容居中且不过于分散 */
  max-width: 1600px;
  margin: 0 auto;
  padding: 20px;
  box-sizing: border-box;
}

.stat-row {
  margin-bottom: 20px;
}

/**
 * 统计卡片
 */
.statistics-card {
  margin-bottom: 20px;
}

.stat-card {
  width: 100%;
  margin-bottom: 20px;
  cursor: pointer;
  transition: all 0.3s;
  box-sizing: border-box;
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
 * 数据更新时间
 */
.update-time {
  text-align: right;
  font-size: 12px;
  color: #909399;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #ebeef5;
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
  gap: 16px;
}

.action-button {
  min-width: 140px;
  height: 80px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 8px;
  padding: 0 20px;
}

.action-button .action-icon {
  font-size: 28px;
  margin-bottom: 4px;
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