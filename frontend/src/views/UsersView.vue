/**
 * CampusAssetManager/frontend/src/views/UsersView.vue
 * 用户管理页面
 * 
 * 功能说明：
 * - 用户列表展示
 * - 用户搜索和筛选
 * - 用户增删改查
 * - 修改密码
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-06
 */

<template>
  <div class="users-container">
    <!-- 工具栏 -->
    <el-card class="toolbar-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="搜索关键词">
          <el-input
            v-model="searchForm.search"
            placeholder="用户名/姓名/手机号"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        
        <el-form-item label="角色">
          <el-select
            v-model="searchForm.role"
            placeholder="请选择角色"
            clearable
            style="width: 150px"
          >
            <el-option label="普通用户" value="user" />
            <el-option label="管理员" value="admin" />
            <el-option label="超级管理员" value="super_admin" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-select
            v-model="searchForm.is_active"
            placeholder="请选择状态"
            clearable
            style="width: 120px"
          >
            <el-option label="激活" :value="true" />
            <el-option label="未激活" :value="false" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="loadUserList">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-button type="primary" @click="handleAdd">新增用户</el-button>
    </el-card>
    
    <!-- 用户列表 -->
    <el-card class="table-card">
      <TableComponent
        :data="userList"
        :loading="loading"
        :show-selection="false"
        :page="pagination.page"
        :limit="pagination.limit"
        :total="pagination.total"
        @update:page="handlePageChange"
        @update:limit="handleSizeChange"
      >
        <template #columns>
          <el-table-column prop="user_id" label="ID" width="80" align="center" />
          <el-table-column prop="username" label="用户名" width="150" />
          <el-table-column prop="real_name" label="真实姓名" width="120" />
          <el-table-column prop="phone" label="联系电话" width="130" />
          <el-table-column prop="email" label="电子邮箱" min-width="180" />
          <el-table-column prop="role" label="角色" width="120" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.role === 'super_admin'" type="danger">超级管理员</el-tag>
              <el-tag v-else-if="row.role === 'admin'" type="warning">管理员</el-tag>
              <el-tag v-else type="info">普通用户</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'">
                {{ row.is_active ? '激活' : '未激活' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="create_time" label="创建时间" width="180" align="center">
            <template #default="{ row }">
              {{ formatDate(row.create_time) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="280" align="center" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
              <el-button type="warning" link @click="handleChangePassword(row)">修改密码</el-button>
              <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </template>
      </TableComponent>
    </el-card>
    
    <!-- 新增/编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userFormRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="userForm.username"
            placeholder="请输入用户名"
            :disabled="isEditMode"
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password" v-if="!isEditMode">
          <el-input
            v-model="userForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="真实姓名" prop="real_name">
          <el-input
            v-model="userForm.real_name"
            placeholder="请输入真实姓名"
          />
        </el-form-item>
        
        <el-form-item label="联系电话" prop="phone">
          <el-input
            v-model="userForm.phone"
            placeholder="请输入联系电话"
          />
        </el-form-item>
        
        <el-form-item label="电子邮箱" prop="email">
          <el-input
            v-model="userForm.email"
            placeholder="请输入电子邮箱"
          />
        </el-form-item>
        
        <el-form-item label="角色" prop="role">
          <el-select
            v-model="userForm.role"
            placeholder="请选择角色"
            style="width: 100%"
          >
            <el-option label="普通用户" value="user" />
            <el-option label="管理员" value="admin" />
            <el-option label="超级管理员" value="super_admin" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态" prop="is_active" v-if="isEditMode">
          <el-switch v-model="userForm.is_active" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
    
    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="passwordDialogVisible"
      title="修改密码"
      width="500px"
      @close="handlePasswordDialogClose"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordFormRules"
        label-width="100px"
      >
        <el-form-item label="旧密码" prop="old_password">
          <el-input
            v-model="passwordForm.old_password"
            type="password"
            placeholder="请输入旧密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="passwordForm.new_password"
            type="password"
            placeholder="请输入新密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input
            v-model="passwordForm.confirm_password"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handlePasswordSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import TableComponent from '@/components/common/TableComponent.vue'
import {
  getUserList,
  createUser,
  updateUser,
  deleteUser,
  updateUserPassword
} from '@/api'

/**
 * 加载状态
 */
const loading = ref(false)

/**
 * 用户列表
 */
const userList = ref([])

/**
 * 搜索表单
 */
const searchForm = reactive({
  search: '',
  role: null,
  is_active: null
})

/**
 * 分页数据
 */
const pagination = reactive({
  page: 1,
  limit: 20,
  total: 0
})

/**
 * 对话框可见性
 */
const dialogVisible = ref(false)

/**
 * 对话框标题
 */
const dialogTitle = computed(() => {
  return isEditMode.value ? '编辑用户' : '新增用户'
})

/**
 * 是否为编辑模式
 */
const isEditMode = computed(() => {
  return !!userForm.user_id
})

/**
 * 用户表单引用
 */
const userFormRef = ref(null)

/**
 * 用户表单数据
 */
const userForm = reactive({
  user_id: null,
  username: '',
  password: '',
  real_name: '',
  phone: '',
  email: '',
  role: 'user',
  is_active: true
})

/**
 * 用户表单验证规则
 */
const userFormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在3-50个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在6-20个字符', trigger: 'blur' }
  ],
  real_name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' },
    { min: 2, max: 50, message: '真实姓名长度在2-50个字符', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

/**
 * 密码对话框可见性
 */
const passwordDialogVisible = ref(false)

/**
 * 密码表单引用
 */
const passwordFormRef = ref(null)

/**
 * 密码表单数据
 */
const passwordForm = reactive({
  user_id: null,
  old_password: '',
  new_password: '',
  confirm_password: ''
})

/**
 * 密码表单验证规则
 */
const passwordFormRules = {
  old_password: [
    { required: true, message: '请输入旧密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在6-20个字符', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

/**
 * 加载用户列表
 */
const loadUserList = async () => {
  try {
    loading.value = true
    const response = await getUserList({
      page: pagination.page,
      page_size: pagination.limit,
      ...searchForm
    })
    userList.value = response.items
    pagination.total = response.total
  } catch (error) {
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 处理页码变化
 * 
 * @param {number} page - 页码
 */
const handlePageChange = (page) => {
  pagination.page = page
  loadUserList()
}

/**
 * 处理每页数量变化
 * 
 * @param {number} limit - 每页数量
 */
const handleSizeChange = (limit) => {
  pagination.limit = limit
  pagination.page = 1
  loadUserList()
}

/**
 * 处理重置
 */
const handleReset = () => {
  searchForm.search = ''
  searchForm.role = null
  searchForm.is_active = null
  loadUserList()
}

/**
 * 处理新增
 */
const handleAdd = () => {
  Object.assign(userForm, {
    user_id: null,
    username: '',
    password: '',
    real_name: '',
    phone: '',
    email: '',
    role: 'user',
    is_active: true
  })
  dialogVisible.value = true
}

/**
 * 处理编辑
 * 
 * @param {Object} row - 行数据
 */
const handleEdit = (row) => {
  Object.assign(userForm, {
    user_id: row.user_id,
    username: row.username,
    password: '',
    real_name: row.real_name,
    phone: row.phone,
    email: row.email,
    role: row.role,
    is_active: row.is_active
  })
  dialogVisible.value = true
}

/**
 * 处理删除
 * 
 * @param {Object} row - 行数据
 */
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除用户"${row.real_name}"吗？删除后该用户将无法使用系统。`,
    '删除确认',
    {
      type: 'warning',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    }
  ).then(async () => {
    try {
      await deleteUser(row.user_id)
      ElMessage.success('删除成功')
      loadUserList()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  })
}

/**
 * 处理修改密码
 * 
 * @param {Object} row - 行数据
 */
const handleChangePassword = (row) => {
  Object.assign(passwordForm, {
    user_id: row.user_id,
    old_password: '',
    new_password: '',
    confirm_password: ''
  })
  passwordDialogVisible.value = true
}

/**
 * 提交用户表单
 */
const handleSubmit = async () => {
  if (!userFormRef.value) return
  
  await userFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    try {
      if (isEditMode.value) {
        // 更新用户
        await updateUser(userForm.user_id, userForm)
        ElMessage.success('更新成功')
      } else {
        // 创建用户
        await createUser(userForm)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      loadUserList()
    } catch (error) {
      ElMessage.error(isEditMode.value ? '更新失败' : '创建失败')
    }
  })
}

/**
 * 关闭用户对话框
 */
const handleDialogClose = () => {
  if (userFormRef.value) {
    userFormRef.value.resetFields()
  }
}

/**
 * 提交密码表单
 */
const handlePasswordSubmit = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    try {
      await updateUserPassword(passwordForm.user_id, {
        old_password: passwordForm.old_password,
        new_password: passwordForm.new_password
      })
      ElMessage.success('密码修改成功')
      passwordDialogVisible.value = false
    } catch (error) {
      ElMessage.error('密码修改失败')
    }
  })
}

/**
 * 关闭密码对话框
 */
const handlePasswordDialogClose = () => {
  if (passwordFormRef.value) {
    passwordFormRef.value.resetFields()
  }
}

/**
 * 格式化日期
 * 
 * @param {string} dateStr - 日期字符串
 * @returns {string} 格式化后的日期
 */
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

/**
 * 组件挂载时加载数据
 */
onMounted(() => {
  loadUserList()
})
</script>

<style scoped>
.users-container {
  padding: 20px;
}

.toolbar-card {
  margin-bottom: 20px;
}

.table-card {
  height: calc(100vh - 250px);
}
</style>