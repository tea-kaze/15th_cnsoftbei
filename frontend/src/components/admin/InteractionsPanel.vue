<template>
  <div class="interactions-panel">
    <!-- 搜索筛选 -->
    <el-card shadow="hover" class="filter-card">
      <el-row :gutter="16" align="middle">
        <el-col :xs="24" :sm="8">
          <el-input v-model="searchKeyword" placeholder="搜索问题或回答..." clearable
            @clear="search" @keyup.enter="search">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-col>
        <el-col :xs="12" :sm="5">
          <el-date-picker v-model="dateRange" type="daterange"
            range-separator="至" start-placeholder="开始日期" end-placeholder="结束日期"
            value-format="YYYY-MM-DD" style="width: 100%" />
        </el-col>
        <el-col :xs="12" :sm="3">
          <el-button type="primary" @click="search">
            <el-icon><Search /></el-icon> 查询
          </el-button>
        </el-col>
        <el-col :xs="24" :sm="8" class="total-info">
          <span>共 {{ total }} 条记录</span>
        </el-col>
      </el-row>
    </el-card>

    <!-- 数据表格 -->
    <el-card shadow="hover" class="table-card">
      <el-table :data="items" stripe v-loading="loading" empty-text="暂无交互记录">
        <el-table-column prop="created_at" label="时间" width="170" />
        <el-table-column prop="question" label="用户问题" min-width="180" show-overflow-tooltip />
        <el-table-column prop="answer" label="AI回答" min-width="220" show-overflow-tooltip />
        <el-table-column prop="response_time_ms" label="响应(ms)" width="100" align="center" />
        <el-table-column label="操作" width="80" align="center">
          <template #default="{ row }">
            <el-button text type="primary" size="small" @click="showDetail(row)">
              <el-icon><View /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @current-change="loadData"
          @size-change="loadData"
        />
      </div>
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="交互详情" width="700px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="时间">{{ detailRow?.created_at }}</el-descriptions-item>
        <el-descriptions-item label="用户问题">{{ detailRow?.question }}</el-descriptions-item>
        <el-descriptions-item label="AI回答">
          <div style="white-space: pre-wrap; max-height: 300px; overflow-y: auto;">{{ detailRow?.answer_full }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="响应时间">{{ detailRow?.response_time_ms }}ms</el-descriptions-item>
        <el-descriptions-item label="检索来源">
          <div style="white-space: pre-wrap;">{{ detailRow?.sources }}</div>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search, View } from '@element-plus/icons-vue'
import { getInteractions } from '../../api/admin'

const items = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const searchKeyword = ref('')
const dateRange = ref([])

const detailVisible = ref(false)
const detailRow = ref(null)

function showDetail(row) {
  detailRow.value = row
  detailVisible.value = true
}

async function loadData() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      keyword: searchKeyword.value,
      date_from: dateRange.value?.[0] || '',
      date_to: dateRange.value?.[1] || '',
    }
    const res = await getInteractions(params)
    items.value = res.items
    total.value = res.total
  } catch (e) {
    console.error('加载交互记录失败:', e)
  } finally {
    loading.value = false
  }
}

function search() {
  currentPage.value = 1
  loadData()
}

onMounted(loadData)
</script>

<style scoped>
.filter-card { margin-bottom: 20px; }

.total-info {
  text-align: right;
  color: #909399;
  font-size: 13px;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}
</style>
