<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ stats.today_count }}</div>
          <div class="stat-label">今日服务人次</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ stats.week_count }}</div>
          <div class="stat-label">本周服务人次</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ stats.total_count }}</div>
          <div class="stat-label">累计问答</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ stats.avg_response_ms }}<small>ms</small></div>
          <div class="stat-label">平均响应时间</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 知识库状态 -->
    <el-row :gutter="20" class="subsection">
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ stats.doc_count }}</div>
          <div class="stat-label">知识文档数</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ stats.chunk_count }}</div>
          <div class="stat-label">知识块总数</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ stats.unique_visitors_today }}</div>
          <div class="stat-label">今日独立访客</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :xs="24" :lg="14">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <span>交互趋势（近30天）</span>
          </template>
          <v-chart :option="trendOption" style="height: 300px" autoresize />
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="10">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <span>热门问题 Top 10</span>
          </template>
          <v-chart :option="popularOption" style="height: 300px" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <!-- 时段热力 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <span>今日时段分布</span>
          </template>
          <v-chart :option="hourlyOption" style="height: 200px" autoresize />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import {
  TitleComponent, TooltipComponent, GridComponent, LegendComponent
} from 'echarts/components'
import { getDashboard, getTrend, getPopular, getHourly } from '../../api/admin'

use([CanvasRenderer, LineChart, BarChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent])

const stats = reactive({
  today_count: 0,
  week_count: 0,
  total_count: 0,
  avg_response_ms: 0,
  unique_visitors_today: 0,
  doc_count: 0,
  chunk_count: 0,
})

const trendData = ref([])
const popularData = ref([])
const hourlyData = ref([])

let timer = null

async function loadStats() {
  const data = await getDashboard()
  Object.assign(stats, data)
}

async function loadTrend() {
  trendData.value = await getTrend(30)
}

async function loadPopular() {
  popularData.value = await getPopular(10, 30)
}

async function loadHourly() {
  hourlyData.value = await getHourly()
}

async function loadAll() {
  try {
    await Promise.all([loadStats(), loadTrend(), loadPopular(), loadHourly()])
  } catch (e) {
    console.error('加载仪表盘数据失败:', e)
  }
}

const trendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 40, right: 20, top: 10, bottom: 30 },
  xAxis: {
    type: 'category',
    data: trendData.value.map(d => d.date.slice(5)),
    axisLabel: { rotate: 45, fontSize: 10 },
  },
  yAxis: { type: 'value', minInterval: 1 },
  series: [{
    data: trendData.value.map(d => d.count),
    type: 'line',
    smooth: true,
    areaStyle: { color: 'rgba(64, 158, 255, 0.15)' },
    lineStyle: { color: '#409EFF', width: 2 },
    itemStyle: { color: '#409EFF' },
  }],
}))

const popularOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: 100, right: 20, top: 10, bottom: 10 },
  xAxis: { type: 'value', minInterval: 1 },
  yAxis: {
    type: 'category',
    data: popularData.value.map(d => d.question.length > 10 ? d.question.slice(0, 10) + '...' : d.question).reverse(),
    axisLabel: { fontSize: 11 },
    inverse: true,
  },
  series: [{
    data: popularData.value.map(d => d.count).reverse(),
    type: 'bar',
    itemStyle: {
      color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0,
        colorStops: [{ offset: 0, color: '#409EFF' }, { offset: 1, color: '#67C23A' }] },
      borderRadius: [0, 4, 4, 0],
    },
  }],
}))

const hourlyOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 40, right: 20, top: 10, bottom: 20 },
  xAxis: {
    type: 'category',
    data: Array.from({ length: 24 }, (_, i) => `${i}时`),
  },
  yAxis: { type: 'value', minInterval: 1 },
  series: [{
    data: (() => {
      const arr = new Array(24).fill(0)
      hourlyData.value.forEach(h => { arr[h.hour] = h.count })
      return arr
    })(),
    type: 'bar',
    itemStyle: {
      color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [{ offset: 0, color: '#79bbff' }, { offset: 1, color: '#409EFF' }] },
      borderRadius: [4, 4, 0, 0],
    },
  }],
}))

onMounted(() => {
  loadAll()
  timer = setInterval(loadAll, 30000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.stats-row { margin-bottom: 20px; }
.subsection { margin-bottom: 20px; }
.charts-row { margin-bottom: 20px; }

.stat-card {
  text-align: center;
  cursor: default;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 4px;
}

.stat-value small {
  font-size: 14px;
  font-weight: 400;
  color: #909399;
}

.stat-label {
  font-size: 13px;
  color: #909399;
}

.chart-card {
  height: 100%;
}
</style>
