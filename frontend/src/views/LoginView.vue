/**
 * CampusAssetManager/frontend/src/views/LoginView.vue
 * 登录页面
 * 
 * 功能说明：
 * - 用户登录表单
 * - 表单验证
 * - 登录成功后跳转
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 */

<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1>校物通</h1>
        <p>校园物品管理系统</p>
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
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
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
.login-container {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  width: 400px;
  padding: 40px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-header h1 {
  font-size: 32px;
  color: #303133;
  margin-bottom: 10px;
}

.login-header p {
  font-size: 14px;
  color: #909399;
}

.login-form {
  margin-top: 30px;
}

.login-button {
  width: 100%;
}
</style>