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
  <div class="login-wrapper">
    <div class="login-container">
      <div class="brand-section">
        <div class="brand-content">
          <div class="brand-header">
            <div class="logo-circle">
              <el-icon :size="32" color="#1677ff"><Odometer /></el-icon>
            </div>
            <span class="brand-name">校物通</span>
          </div>
          <div class="brand-slogan">
            <h2>智慧校园<br>资产管理专家</h2>
            <p>高效 · 精准 · 可视化</p>
          </div>
          <div class="brand-footer">
            <span>Enterprise Edition</span>
          </div>
        </div>
        <div class="brand-bg-decoration"></div>
      </div>

      <div class="form-section">
        <div class="form-content">
          <div class="form-header">
            <h3>欢迎登录</h3>
            <p>请输入您的账号和密码以继续</p>
          </div>
          
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            class="login-form"
            @submit.prevent="handleLogin"
            size="large"
          >
            <el-form-item prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="请输入用户名"
                :prefix-icon="User"
                class="custom-input"
              />
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                :prefix-icon="Lock"
                show-password
                class="custom-input"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                :loading="loading"
                native-type="submit"
                class="submit-btn"
              >
                {{ loading ? '登录中...' : '立即登录' }}
              </el-button>
            </el-form-item>
          </el-form>

          <div class="form-footer">
            <p>© 2026 Campus Asset Manager. All Rights Reserved.</p>
          </div>
        </div>
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
    const valid = await loginFormRef.value.validate()
    if (!valid) return
    
    loading.value = true
    
    const response = await login({
      username: loginForm.username,
      password: loginForm.password
    })
    
    userStore.setToken(response.access_token)
    userStore.setUser(response.user)
    
    ElMessage.success('登录成功')
    
    // 获取重定向路径
    const redirect = route.query.redirect || '/'
    
    // 如果重定向路径是/database、/home或根路径/，则跳转到首页/home
    // 这样可以避免数据恢复后又回到database页
    if (redirect === '/database' || redirect === '/home' || redirect === '/') {
      router.push('/home')
    } else {
      router.push(redirect)
    }
  } catch (error) {
    console.error('登录失败:', error)
    ElMessage.error(error.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrapper {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f0f2f5;
  background-image: 
    radial-gradient(#e3e8ee 1px, transparent 1px),
    radial-gradient(#e3e8ee 1px, transparent 1px);
  background-position: 0 0, 20px 20px;
  background-size: 40px 40px;
}

.login-container {
  width: 1000px;
  height: 600px;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.05);
  display: flex;
  overflow: hidden;
}

/* 左侧品牌区 */
.brand-section {
  flex: 0.8;
  background: linear-gradient(135deg, #e6f4ff 0%, #f0f7ff 100%);
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 60px;
  overflow: hidden;
}

.brand-bg-decoration {
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(22, 119, 255, 0.05) 0%, transparent 60%);
  z-index: 0;
}

.brand-content {
  position: relative;
  z-index: 1;
}

.brand-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 40px;
}

.logo-circle {
  width: 48px;
  height: 48px;
  background: #fff;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(22, 119, 255, 0.1);
}

.brand-name {
  font-size: 24px;
  font-weight: 700;
  color: #1f1f1f;
  letter-spacing: 1px;
}

.brand-slogan h2 {
  font-size: 36px;
  line-height: 1.2;
  color: #1f1f1f;
  margin-bottom: 16px;
}

.brand-slogan p {
  font-size: 16px;
  color: #697b8c;
  letter-spacing: 2px;
}

.brand-footer {
  margin-top: 60px;
  font-size: 12px;
  color: #909399;
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* 右侧表单区 */
.form-section {
  flex: 1;
  padding: 60px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: #fff;
}

.form-content {
  width: 100%;
  max-width: 360px;
  margin: 0 auto;
}

.form-header {
  margin-bottom: 40px;
}

.form-header h3 {
  font-size: 28px;
  color: #1f1f1f;
  margin-bottom: 8px;
  font-weight: 600;
}

.form-header p {
  color: #8c8c8c;
  font-size: 14px;
}

.custom-input :deep(.el-input__wrapper) {
  background-color: #f5f7fa;
  border: 1px solid transparent;
  box-shadow: none;
  border-radius: 8px;
  transition: all 0.3s;
}

.custom-input :deep(.el-input__wrapper:hover),
.custom-input :deep(.el-input__wrapper.is-focus) {
  background-color: #fff;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 1px var(--primary-color);
}

.submit-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  border-radius: 8px;
  margin-top: 12px;
  font-weight: 600;
  letter-spacing: 1px;
}

.form-footer {
  margin-top: 40px;
  text-align: center;
}

.form-footer p {
  font-size: 12px;
  color: #bfbfbf;
}

/* 响应式适配 */
@media (max-width: 992px) {
  .login-container {
    width: 90%;
    height: auto;
    flex-direction: column;
    max-width: 450px;
  }
  
  .brand-section {
    display: none;
  }

  .form-section {
    padding: 40px;
  }
}
</style>