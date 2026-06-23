<template>
  <div class="admin-container">
    <el-container>
      <el-aside width="220px" class="admin-aside">
        <div class="aside-logo">
          <h3>灵山胜境</h3>
          <span>管理后台</span>
        </div>
        <el-menu
          :default-active="activeMenu"
          router
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
        >
          <el-menu-item index="/admin/dashboard">
            <el-icon><DataAnalysis /></el-icon>
            <span>数据大屏</span>
          </el-menu-item>
          <el-menu-item index="/admin/interactions">
            <el-icon><ChatDotRound /></el-icon>
            <span>交互记录</span>
          </el-menu-item>
          <el-menu-item index="/admin/knowledge">
            <el-icon><FolderOpened /></el-icon>
            <span>知识库管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/report">
            <el-icon><DocumentChecked /></el-icon>
            <span>游客报告</span>
          </el-menu-item>
          <el-menu-item index="/admin/digital-human">
            <el-icon><UserFilled /></el-icon>
            <span>数字人配置</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-container>
        <el-header class="admin-header">
          <span class="header-title">{{ headerTitle }}</span>
          <el-button text @click="$router.push('/visitor')">
            <el-icon><View /></el-icon>
            返回游客端
          </el-button>
        </el-header>
        <el-main class="admin-main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  DataAnalysis, ChatDotRound, FolderOpened,
  DocumentChecked, View, UserFilled
} from '@element-plus/icons-vue'

const route = useRoute()
const activeMenu = computed(() => route.path)

const headerTitle = computed(() => {
  const map = {
    '/admin/dashboard': '数据大屏',
    '/admin/interactions': '交互记录',
    '/admin/knowledge': '知识库管理',
    '/admin/report': '游客报告',
  }
  return map[route.path] || '管理后台'
})
</script>

<style scoped>
.admin-container {
  height: 100vh;
}

.admin-aside {
  background: #304156;
  overflow-y: auto;
}

.aside-logo {
  padding: 20px 16px;
  text-align: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.aside-logo h3 {
  color: #fff;
  font-size: 18px;
  margin: 0 0 4px 0;
}

.aside-logo span {
  color: #bfcbd9;
  font-size: 12px;
}

.admin-header {
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 56px;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.admin-main {
  background: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}
</style>
