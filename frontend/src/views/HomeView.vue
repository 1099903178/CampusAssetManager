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
 */

<template>
  <div class="home-container">
    <div class="header-banner">
      <div class="banner-left">
        <h2 class="welcome-text">
          {{ timeState.greeting }}，<span class="user-highlight">{{ username }}</span>
        </h2>
        <p class="day-tips">
          <el-icon class="icon-spin"><Sunny /></el-icon>
          {{ timeState.tips }}
        </p>
      </div>
      <div class="banner-right">
        <div class="clock-wrapper">
          <div class="clock-time num-font">{{ timeState.time }}</div>
          <div class="clock-date">{{ timeState.date }} · {{ timeState.week }}</div>
        </div>
      </div>
    </div>

    <div class="metrics-grid">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="12" :md="6" v-for="item in metricConfigs" :key="item.label">
          <div class="metric-card" :class="item.type">
            <div class="metric-icon">
              <el-icon><component :is="item.icon" /></el-icon>
            </div>
            <div class="metric-body">
              <span class="metric-label">{{ item.label }}</span>
              <div class="metric-value num-font">
                <count-up :end-val="item.value" :duration="1.5" />
              </div>
            </div>
            <div class="metric-bg-icon">
              <el-icon><component :is="item.icon" /></el-icon>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <el-row :gutter="20" class="action-section">
      <el-col :lg="16" :md="24">
        <div class="glass-panel">
          <div class="panel-head">
            <span class="title">快捷导航</span>
            <span class="desc">常用业务一键直达</span>
          </div>
          <div class="nav-tiles">
            <div class="tile-item" @click="$router.push('/goods')">
              <div class="tile-icon b-blue"><el-icon><Box /></el-icon></div>
              <span>物品管理</span>
            </div>
            <div class="tile-item" @click="$router.push('/stock')">
              <div class="tile-icon b-indigo"><el-icon><House /></el-icon></div>
              <span>库存管理</span>
            </div>
            <div class="tile-item" @click="$router.push('/check')">
              <div class="tile-icon b-orange"><el-icon><Aim /></el-icon></div>
              <span>库存盘点</span>
            </div>
            <div class="tile-item" @click="$router.push('/statistics')">
              <div class="tile-icon b-purple"><el-icon><TrendCharts /></el-icon></div>
              <span>数据报表</span>
            </div>
            <div class="tile-item" @click="$router.push('/ledger')">
              <div class="tile-icon b-teal"><el-icon><Files /></el-icon></div>
              <span>库存台账</span>
            </div>
          </div>
        </div>
      </el-col>

      <el-col :lg="8" :md="24">
        <div class="glass-panel">
          <div class="panel-head">
            <span class="title">系统公告</span>
            <el-link type="primary" :underline="false">更多</el-link>
          </div>
          <div class="notice-timeline">
            <div class="notice-card" v-for="(n, i) in notices" :key="i">
              <div class="n-date num-font">{{ n.date }}</div>
              <div class="n-content">
                <div class="n-title">{{ n.title }}</div>
                <p>{{ n.desc }}</p>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
/**
 * 首页仪表板逻辑
 *
 * 导入模块：
 * - Vue Composition API：ref, reactive, computed, onMounted, onUnmounted
 * - Pinia Store：useUserStore
 * - 数字动画组件：CountUp
 * - Element Plus 图标组件
 * - 统计数据 API
 */
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { useUserStore } from '@/stores'
import CountUp from 'vue-countup-v3'
import {
  Sunny, Odometer, Box, House, Aim, TrendCharts, Files,
  WarningFilled, ShoppingCart
} from '@element-plus/icons-vue'
import { getDataOverview } from '@/api/statistics'

/* ==================== 用户信息管理 ==================== */

/**
 * 用户状态管理 Store
 */
const userStore = useUserStore()

/**
 * 用户名
 *
 * 从用户 Store 中获取当前登录用户的用户名
 * 用于欢迎横幅中显示个性化问候
 * 如果未设置则显示默认值 '管理员'
 *
 * @returns {string} 用户名
 */
const username = computed(() => userStore.username || '管理员')

/* ==================== 时间报告系统 ==================== */

/**
 * 时间状态
 *
 * 声明式定义时间、日期、问候语和提示信息
 * 用于首页欢迎横幅的动态展示
 *
 * @type {reactive} 包含以下字段：
 *   - time: 当前时间（HH:mm:ss 格式）
 *   - date: 当前日期（月日格式）
 *   - week: 星期几
 *   - greeting: 问候语（早上好/上午好/中午好/下午好/晚上好）
 *   - tips: 根据时间段推荐的系统提示
 */
const timeState = reactive({
  time: '',
  date: '',
  week: '',
  greeting: '',
  tips: ''
})

/**
 * 计时器引用
 *
 * 用于每秒更新时间，组件卸载时清除定时器
 *
 * @type {number|null}
 */
let timer = null

/**
 * 更新时间状态
 *
 * 每秒执行一次，更新时间、日期、问候语和提示信息
 *
 * 时间格式：
 * - 24小时制（hour12: false）
 * - 中文日期格式（月日）
 *
 * 问候语逻辑：
 * - 0-8时: 早上好 - 清晨时光，适合整理资产清单
 * - 9-11时: 上午好 - 专注高效，处理入库事务
 * - 12-13时: 中午好 - 吃顿好的，休息一下
 * - 14-17时: 下午好 - 喝杯咖啡，检查库存预警
 * - 18-23时: 晚上好 - 辛苦了，别忘了核对今日流水
 *
 * 用户体验：
 * - 实时更新时间显示
 * - 个性化问候语提升用户好感度
 * - 根据时间段提供业务建议
 */
const updateTime = () => {
  const now = new Date()
  const hour = now.getHours()
  
  // 更新时间（24小时制）
  timeState.time = now.toLocaleTimeString('zh-CN', { hour12: false })
  
  // 更新日期和星期
  timeState.date = `${now.getMonth() + 1}月${now.getDate()}日`
  timeState.week = [
    '周日', '周一', '周二', '周三', '周四', '周五', '周六'
  ][now.getDay()]
  
  // 根据时间段设置问候语和提示
  if (hour < 9) {
    timeState.greeting = '早上好'
    timeState.tips = '清晨时光，适合整理资产清单'
  }
  else if (hour < 12) {
    timeState.greeting = '上午好'
    timeState.tips = '专注高效，处理入库事务'
  }
  else if (hour < 14) {
    timeState.greeting = '中午好'
    timeState.tips = '吃顿好的，休息一下'
  }
  else if (hour < 18) {
    timeState.greeting = '下午好'
    timeState.tips = '喝杯咖啡，检查库存预警'
  }
  else {
    timeState.greeting = '晚上好'
    timeState.tips = '辛苦了，别忘了核对今日流水'
  }
}

/* ==================== 数据统计系统 ==================== */

/**
 * 统计数据
 *
 * 声明式定义从后端获取的统计数据
 * 用于首页指标卡片的展示
 *
 * @type {reactive} 包含以下字段：
 *   - total_goods: 物品总数
 *   - total_stock: 当前库存总量
 *   - today_stock_in: 今日入库数量
 *   - warning_count: 库存预警数量
 */
const stats = reactive({
  total_goods: 0,
  total_stock: 0,
  today_stock_in: 0,
  warning_count: 0
})

/**
 * 指标卡片配置
 *
 * 使用计算属性动态生成指标卡片的配置
 * 每个卡片包含标签、数值、图标和样式类型
 *
 * @returns {Array<Object>} 指标配置数组
 *   - label: 卡片标签
 *   - value: 数值（使用 CountUp 组件动画显示）
 *   - icon: Element Plus 图标组件
 *   - type: 样式类型（对应 CSS 类名）
 *     - m-blue: 蓝色样式（物品总数）
 *     - m-green: 绿色样式（当前库存）
 *     - m-purple: 紫色样式（今日入库）
 *     - m-orange: 橙色样式（库存预警）
 */
const metricConfigs = computed(() => [
  {
    label: '物品总数',
    value: stats.total_goods,
    icon: Box,
    type: 'm-blue'
  },
  {
    label: '当前库存',
    value: stats.total_stock,
    icon: ShoppingCart,
    type: 'm-green'
  },
  {
    label: '今日入库',
    value: stats.today_stock_in,
    icon: Files,
    type: 'm-purple'
  },
  {
    label: '库存预警',
    value: stats.warning_count,
    icon: WarningFilled,
    type: 'm-orange'
  }
])

/**
 * 获取统计数据
 *
 * 从后端 API 获取数据概览，更新统计数值
 *
 * API 端点：
 * - GET /v1/statistics/overview
 *
 * 返回数据结构（Pydantic 模式）：
 * - total_goods: 物品总数
 * - total_stock: 当前库存总量
 * - today_stock_in: 今日入库数量
 * - warning_count: 库存预警数量
 *
 * 业务逻辑：
 * 1. 调用 getDataOverview API 获取数据
 * 2. 直接解包响应数据到响应式对象
 * 3. 使用 || 运算符设置默认值，防止 undefined
 *
 * 错误处理：
 * - 捕获异常并输出到控制台
 * - 静默处理错误，不显示错误提示（避免页面加载时弹出错误）
 *
 * @async
 */
const fetchStats = async () => {
  try {
    const res = await getDataOverview()
    if (res) {
      // 直接解包后端返回的 Pydantic 模型数据
      stats.total_goods = res.total_goods || 0
      stats.total_stock = res.total_stock || 0
      stats.today_stock_in = res.today_stock_in || 0
      stats.warning_count = res.warning_count || 0
    }
  } catch (e) {
    console.error('Home Statistics Fetch Error', e)
  }
}

/* ==================== 系统公告系统 ==================== */

/**
 * 系统公告列表
 *
 * 静态公告数据，实际项目中应从后端 API 获取
 *
 * @type {Array<Object>} 公告数组
 *   - date: 公告日期（MM/DD 格式）
 *   - title: 公告标题
 *   - desc: 公告描述
 */
const notices = [
  {
    date: '01/14',
    title: '系统安全维护',
    desc: '本周末凌晨将进行数据库例行备份与性能优化。'
  },
  {
    date: '01/10',
    title: '资产清查通知',
    desc: '请各部门在15日前提交本月度盘点报告。'
  }
]

/* ==================== 生命周期钩子 ==================== */

/**
 * 组件挂载时执行
 *
 * 页面加载完成后自动执行：
 * 1. 立即更新一次时间状态
 * 2. 启动定时器，每秒更新时间
 * 3. 获取统计数据，填充指标卡片
 *
 * 定时器管理：
 * - 使用 setInterval 每秒执行 updateTime
 * - 将定时器 ID 保存到 timer 变量
 *
 * @async
 */
onMounted(() => {
  // 立即更新时间
  updateTime()
  // 启动定时器（每1秒更新一次）
  timer = setInterval(updateTime, 1000)
  // 获取统计数据
  fetchStats()
})

/**
 * 组件卸载时执行
 *
 * 清理定时器，防止内存泄漏
 *
 * 内存管理：
 * - 组件卸载时必须清除定时器
 * - 避免组件销毁后定时器仍在运行
 *
 * @async
 */
onUnmounted(() => {
  clearInterval(timer)
})
</script>

<style scoped>
.home-container {
  max-width: 1440px;
  margin: 0 auto;
  animation: pageFadeIn 0.5s ease;
}

/* 1. 欢迎栏 */
.header-banner {
  background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
  border-radius: 12px;
  padding: 24px 32px;
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.2);
}

.welcome-text {
  font-size: 24px;
  font-weight: 700;
  margin: 0 0 6px 0;
}

.user-highlight {
  color: white;
  font-weight: 700;
}

.day-tips {
  font-size: 14px;
  opacity: 0.9;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.clock-wrapper { text-align: right; }
.clock-time { font-size: 32px; font-weight: 700; line-height: 1; margin-bottom: 4px; }
.clock-date { font-size: 13px; opacity: 0.8; letter-spacing: 0.5px; }

/* 2. 指标卡片 */
.metrics-grid { margin-bottom: 24px; }

.metric-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
  overflow: hidden;
  border: 1px solid #f1f5f9;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.metric-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 20px -5px rgba(0,0,0,0.05);
}

.metric-icon {
  width: 54px;
  height: 54px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  z-index: 2;
}

.m-blue .metric-icon { background: #eff6ff; color: #2563eb; }
.m-green .metric-icon { background: #f0fdf4; color: #16a34a; }
.m-purple .metric-icon { background: #faf5ff; color: #9333ea; }
.m-orange .metric-icon { background: #fff7ed; color: #ea580c; }

.metric-body { z-index: 2; }
.metric-label { font-size: 13px; color: #64748b; display: block; margin-bottom: 4px; }
.metric-value { font-size: 28px; font-weight: 700; color: #1e293b; line-height: 1; }

.metric-bg-icon {
  position: absolute;
  right: -10px;
  bottom: -15px;
  font-size: 72px;
  opacity: 0.04;
  transform: rotate(-15deg);
}

/* 3. 功能面板 */
.glass-panel {
  background: white;
  border-radius: 16px;
  padding: 24px;
  border: 1px solid #f1f5f9;
  height: 100%;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 20px;
  border-bottom: 1px solid #f8fafc;
  padding-bottom: 12px;
}

.panel-head .title { font-size: 16px; font-weight: 700; color: #1e293b; }
.panel-head .desc { font-size: 12px; color: #94a3b8; margin-left: 10px; }

.nav-tiles {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: 16px;
}

.tile-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  background: #f8fafc;
}

.tile-item:hover { background: #fff; box-shadow: 0 4px 12px rgba(0,0,0,0.05); transform: translateY(-2px); }

.tile-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  color: white;
  margin-bottom: 10px;
}

.b-blue { background: #3b82f6; }
.b-indigo { background: #6366f1; }
.b-orange { background: #f97316; }
.b-purple { background: #a855f7; }
.b-teal { background: #14b8a6; }

.tile-item span { font-size: 13px; color: #475569; font-weight: 500; }

/* 公告时间轴 */
.notice-timeline { display: flex; flex-direction: column; gap: 12px; }
.notice-card {
  display: flex;
  gap: 16px;
  padding: 12px;
  border-radius: 8px;
  background: #f8fafc;
}
.n-date { font-size: 14px; font-weight: 700; color: #3b82f6; background: #fff; padding: 4px 8px; border-radius: 6px; height: fit-content; }
.n-title { font-size: 14px; font-weight: 600; color: #1e293b; margin-bottom: 4px; }
.n-content p { font-size: 12px; color: #64748b; margin: 0; line-height: 1.5; }

/* 数字字体类 */
.num-font { font-family: 'Oswald', sans-serif !important; letter-spacing: -0.5px; }

@keyframes pageFadeIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }

.icon-spin { animation: spin 8s linear infinite; }
@keyframes spin { from { transform: rotate(0); } to { transform: rotate(360deg); } }
</style>