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
  <div class="dashboard-container">
    <div class="welcome-banner">
      <div class="welcome-text">
        <h2>{{ timeGreeting }}，管理员</h2>
        <p>今天是 {{ currentDate }}，准备好处理今天的校园资产事务了吗？</p>
      </div>
      <div class="welcome-decoration">
        <el-icon :size="120" color="rgba(255,255,255,0.15)"><Odometer /></el-icon>
      </div>
    </div>

    <div class="section-container">
      <div class="section-header">
        <h3>核心指标</h3>
        <el-button 
          :icon="RefreshRight" 
          circle 
          size="small"
          @click="refreshData" 
          :loading="loading" 
        />
      </div>

      <el-row :gutter="20" class="stat-row">
        <el-col :xs="24" :sm="12" :md="6" v-for="stat in statistics" :key="stat.title">
          <div class="stat-card">
            <div class="stat-icon-box" :style="{ background: `linear-gradient(135deg, ${stat.color} 0%, ${adjustColor(stat.color, -20)} 100%)` }">
              <el-icon><component :is="stat.icon" /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-label">{{ stat.title }}</div>
              <div class="stat-num">{{ stat.value }}</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
      
    <el-row :gutter="20" style="margin-top: 10px;">
      <el-col :lg="16" :md="24">
        <div class="content-panel">
          <div class="panel-header">
            <h4>快捷导航</h4>
          </div>
          <div class="quick-actions-grid">
            <div 
              class="action-item" 
              v-for="action in actions"
              :key="action.name"
              @click="handleAction(action.path)"
            >
              <div class="action-icon" :class="action.type">
                <el-icon><component :is="action.icon" /></el-icon>
              </div>
              <span class="action-name">{{ action.name }}</span>
            </div>
          </div>
        </div>
      </el-col>
      
      <el-col :lg="8" :md="24">
        <div class="content-panel">
          <div class="panel-header">
            <h4>最新公告</h4>
            <el-link type="primary" :underline="false" style="font-size: 12px;">查看全部</el-link>
          </div>
          <div class="notice-list">
            <div class="notice-item" v-for="(notice, index) in notices" :key="index">
              <div class="notice-date-badge">
                <span class="day">{{ getDay(notice.date) }}</span>
                <span class="month">{{ getMonth(notice.date) }}月</span>
              </div>
              <div class="notice-content">
                <div class="notice-title">{{ notice.title }}</div>
                <div class="notice-desc">{{ notice.content }}</div>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, markRaw, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Box, ShoppingCart, DocumentChecked, WarningFilled, RefreshRight, DataLine, Odometer } from '@element-plus/icons-vue'
import { getDataOverview } from '@/api/statistics'

const router = useRouter()
const loading = ref(false)

// 动态问候语
const timeGreeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 9) return '早上好'
  if (hour < 12) return '上午好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

const currentDate = computed(() => {
  const date = new Date()
  return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`
})

const statistics = ref([
  { title: '物品总数', value: '0', icon: markRaw(Box), color: '#1677ff' },
  { title: '当前库存', value: '0', icon: markRaw(ShoppingCart), color: '#52c41a' },
  { title: '今日入库', value: '0', icon: markRaw(DocumentChecked), color: '#faad14' },
  { title: '库存预警', value: '0', icon: markRaw(WarningFilled), color: '#ff4d4f' }
])

const actions = [
  { name: '物品管理', path: '/goods', icon: Box, type: 'primary' },
  { name: '库存管理', path: '/stock', icon: ShoppingCart, type: 'success' },
  { name: '库存盘点', path: '/check', icon: DocumentChecked, type: 'warning' },
  { name: '数据报表', path: '/statistics', icon: DataLine, type: 'danger' }
]

const notices = [
  { title: '系统升级维护通知', content: '系统将于本周六凌晨2:00进行维护，预计2小时。', date: '2026-01-05' },
  { title: '新功能发布', content: '新增数据驾驶舱，支持多维度分析库存数据。', date: '2026-01-09' },
  { title: '安全提醒', content: '请定期修改密码，确保账户安全。', date: '2026-01-03' }
]

const loadStatistics = async () => {
  try {
    loading.value = true
    const res = await getDataOverview()
    if (res) {
      statistics.value[0].value = res.total_goods || '0'
      statistics.value[1].value = res.total_stock || '0'
      statistics.value[2].value = res.today_stock_in || '0'
      statistics.value[3].value = res.warning_count || '0'
    }
  } catch (e) {
    // 失败静默处理或轻提示
  } finally {
    loading.value = false
  }
}

const refreshData = () => loadStatistics()
const handleAction = (path) => router.push(path)

// 日期解析辅助
const getDay = (dateStr) => dateStr.split('-')[2]
const getMonth = (dateStr) => dateStr.split('-')[1]

// 颜色变暗辅助函数 (简易版)
const adjustColor = (color, amount) => color // 实际可用 tinycolor 库，这里暂不做处理

onMounted(() => loadStatistics())
</script>

<style scoped>
.dashboard-container {
  max-width: 1600px;
  margin: 0 auto;
}

/* 欢迎 Banner */
.welcome-banner {
  background: linear-gradient(135deg, #1677ff 0%, #3594ff 100%);
  border-radius: 12px;
  padding: 32px 40px;
  color: #fff;
  margin-bottom: 24px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 20px -5px rgba(22, 119, 255, 0.3);
}

.welcome-text h2 {
  font-size: 24px;
  margin-bottom: 8px;
  font-weight: 600;
}

.welcome-text p {
  opacity: 0.9;
  font-size: 14px;
}

.welcome-decoration {
  position: absolute;
  right: -20px;
  top: -20px;
  transform: rotate(15deg);
}

/* 章节标题 */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.section-header h3 {
  font-size: 16px;
  color: #1f1f1f;
  font-weight: 600;
}

/* 统计卡片 */
.stat-card {
  background: #fff;
  border-radius: 10px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
  border: 1px solid #f0f0f0;
  margin-bottom: 20px;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06);
  border-color: transparent;
}

.stat-icon-box {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 22px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 13px;
  color: #8c8c8c;
  margin-bottom: 4px;
}

.stat-num {
  font-size: 26px;
  font-weight: 700;
  color: #1f1f1f;
  line-height: 1;
}

/* 面板通用 */
.content-panel {
  background: #fff;
  border-radius: 10px;
  padding: 24px;
  height: 100%;
  border: 1px solid #f0f0f0;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f5f5f5;
}

.panel-header h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1f1f1f;
}

/* 快捷操作 */
.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 16px;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: #f9fafb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.action-item:hover {
  background: #fff;
  border-color: #1677ff;
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.1);
}

.action-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  margin-bottom: 10px;
  color: #fff;
}

.action-icon.primary { background: linear-gradient(135deg, #4096ff, #1677ff); }
.action-icon.success { background: linear-gradient(135deg, #95de64, #52c41a); }
.action-icon.warning { background: linear-gradient(135deg, #ffd666, #faad14); }
.action-icon.danger { background: linear-gradient(135deg, #ff7875, #ff4d4f); }

.action-name {
  font-size: 13px;
  color: #595959;
}

/* 公告列表 */
.notice-item {
  display: flex;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px dashed #f0f0f0;
}

.notice-item:last-child {
  border-bottom: none;
}

.notice-date-badge {
  background: #f0f7ff;
  color: #1677ff;
  border-radius: 6px;
  padding: 6px 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 50px;
  height: 50px;
}

.notice-date-badge .day {
  font-size: 18px;
  font-weight: 700;
  line-height: 1;
}

.notice-date-badge .month {
  font-size: 10px;
  margin-top: 2px;
}

.notice-content {
  flex: 1;
}

.notice-title {
  font-size: 14px;
  font-weight: 500;
  color: #1f1f1f;
  margin-bottom: 4px;
}

.notice-desc {
  font-size: 12px;
  color: #8c8c8c;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>