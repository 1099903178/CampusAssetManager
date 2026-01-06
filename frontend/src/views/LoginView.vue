/**
 * CampusAssetManager/frontend/src/views/LoginView.vue
 * 登录页面
 *
 * 功能说明：
 * - 用户登录表单
 * - 表单验证
 * - 登录成功后跳转
 * - 蓝色科技风格界面设计
 *
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 */

<template>
  <div class="login-container">
    <!-- 背景装饰元素 -->
    <div class="bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="grid-lines"></div>
    </div>

    <div class="login-box">
      <!-- Logo区域 -->
      <div class="login-header">
        <div class="logo-icon">
          <el-icon :size="48"><Odometer /></el-icon>
        </div>
        <h1>校物通</h1>
        <p>校园物品量化管理系统</p>
      </div>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            :prefix-icon="User"
            size="large"
            class="tech-input"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            size="large"
            show-password
            class="tech-input"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            native-type="submit"
            class="login-button"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 底部信息 -->
      <div class="login-footer">
        <p>© 2026 校物通 Campus Asset Manager</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, Odometer } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores'
import { login } from '@/api'

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
 * 登录表单引用
 */
const loginFormRef = ref(null)

/**
 * 加载状态
 */
const loading = ref(false)

/**
 * 登录表单数据
 */
const loginForm = reactive({
  username: '',
  password: ''
})

/**
 * 表单验证规则
 */
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
  ]
}

/**
 * 处理登录
 */
const handleLogin = async () => {
  try {
    /**
     * 验证表单
     */
    const valid = await loginFormRef.value.validate()
    if (!valid) return
    
    /**
     * 设置加载状态
     */
    loading.value = true
    
    /**
     * 调用登录API
     */
    const response = await login({
      username: loginForm.username,
      password: loginForm.password
    })
    
    /**
     * 保存Token和用户信息
     * 响应拦截器已解包，response 直接是 {access_token, token_type, user}
     */
    userStore.setToken(response.access_token)
    userStore.setUser(response.user)
    
    /**
     * 显示成功提示
     */
    ElMessage.success('登录成功')
    
    /**
     * 跳转到首页或重定向页面
     */
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (error) {
    console.error('登录失败:', error)
    ElMessage.error(error.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 登录容器 - 浅色科技背景 */
.login-container {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #e3f2fd 0%, #f5f5f5 50%, #fafafa 100%);
  position: relative;
  overflow: hidden;
}

/* 背景装饰 */
.bg-decoration {
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

/* 网格线条 - 移除动画以提高性能 */
.grid-lines {
  width: 100%;
  height: 100%;
  background-image:
    linear-gradient(rgba(13, 71, 161, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(13, 71, 161, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
}

/* 装饰圆形 - 简化动画 */
.circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.3;
  will-change: transform;
}

.circle-1 {
  width: 500px;
  height: 500px;
  background: linear-gradient(135deg, rgba(25, 118, 210, 0.12), rgba(13, 71, 161, 0.08));
  top: -250px;
  right: -150px;
  animation: float 10s ease-in-out infinite;
}

.circle-2 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, rgba(33, 150, 243, 0.1), rgba(25, 118, 210, 0.12));
  bottom: -200px;
  left: -150px;
  animation: float 12s ease-in-out infinite reverse;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-15px);
  }
}

/* 登录框 - 白色卡片 - 优化性能 */
.login-box {
  width: 420px;
  padding: 50px 45px;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.9);
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.06);
  position: relative;
  z-index: 1;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Logo图标 */
.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-icon {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  width: 80px;
  height: 80px;
  margin-bottom: 20px;
  background: linear-gradient(135deg, #1976d2 0%, #0d47a1 100%);
  border-radius: 50%;
  color: #ffffff;
  box-shadow: 0 8px 20px rgba(25, 118, 210, 0.25);
  will-change: transform;
}

.logo-icon:hover {
  transform: scale(1.05);
  transition: transform 0.3s ease;
}

.login-header h1 {
  font-size: 32px;
  font-weight: 700;
  color: #1a1f3a;
  margin-bottom: 12px;
  letter-spacing: 2px;
  background: linear-gradient(135deg, #0d47a1 0%, #1565c0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-header p {
  font-size: 14px;
  color: #8890a5;
  font-weight: 400;
  letter-spacing: 1px;
}

/* 表单样式 */
.login-form {
  margin-top: 30px;
}

/* 科技风格输入框 */
.login-form :deep(.el-form-item) {
  margin-bottom: 24px;
}

.login-form :deep(.el-input__wrapper) {
  background: #fafafa;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  transition: border-color 0.2s ease, background-color 0.2s ease;
  padding: 0 16px;
}

.login-form :deep(.el-input__wrapper:hover) {
  border-color: #1976d2;
  background: #f5f5f5;
}

.login-form :deep(.el-input__wrapper.is-focus) {
  border-color: #1976d2;
  background: #ffffff;
}

.login-form :deep(.el-input__inner) {
  color: #1a1f3a;
  font-size: 15px;
  height: 48px;
  line-height: 48px;
  font-weight: 500;
}

.login-form :deep(.el-input__inner::placeholder) {
  color: #94a3b8;
}

.login-form :deep(.el-input__prefix) {
  color: #64748b;
}

/* 登录按钮 */
.login-button {
  width: 100%;
  height: 50px;
  margin-top: 10px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 2px;
  background: linear-gradient(135deg, #1976d2 0%, #0d47a1 100%);
  border: none;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(25, 118, 210, 0.25);
  transition: background-color 0.2s ease, transform 0.15s ease, box-shadow 0.2s ease;
  will-change: transform;
}

.login-button:hover {
  background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%);
  box-shadow: 0 6px 16px rgba(25, 118, 210, 0.3);
}

.login-button:active {
  transform: translateY(1px);
  box-shadow: 0 2px 8px rgba(25, 118, 210, 0.2);
}

/* 底部信息 */
.login-footer {
  text-align: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.login-footer p {
  font-size: 12px;
  color: #94a3b8;
  font-weight: 400;
  letter-spacing: 0.5px;
}
</style>