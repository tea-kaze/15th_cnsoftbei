<template>
  <div class="report-panel">
    <!-- 生成控制 -->
    <el-card shadow="hover" class="control-card">
      <el-row align="middle" :gutter="16">
        <el-col :xs="24" :sm="6">
          <span class="control-label">分析周期：</span>
          <el-select v-model="reportDays" style="width: 140px">
            <el-option :value="7" label="近 7 天" />
            <el-option :value="14" label="近 14 天" />
            <el-option :value="30" label="近 30 天" />
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="6">
          <el-button type="primary" :loading="loading" @click="generateReport">
            <el-icon><DocumentChecked /></el-icon>
            {{ loading ? '分析中...' : '生成报告' }}
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 报告内容 -->
    <template v-if="report">
      <!-- 统计概览 -->
      <el-row :gutter="20" class="summary-row">
        <el-col :xs="12" :sm="8">
          <el-card shadow="hover" class="summary-card">
            <div class="summary-value">{{ report.total_interactions || 0 }}</div>
            <div class="summary-label">周期内交互总量</div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="8">
          <el-card shadow="hover" class="summary-card">
            <div class="summary-value">{{ report.top_concerns?.length || 0 }}</div>
            <div class="summary-label">关注维度</div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="8">
          <el-card shadow="hover" class="summary-card">
            <div class="summary-value">{{ report.suggestions?.length || 0 }}</div>
            <div class="summary-label">服务建议</div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 关注点分析 -->
      <el-card shadow="hover" class="section-card">
        <template #header><span>游客关注点分析</span></template>
        <v-chart :option="concernOption" style="height: 280px" autoresize />
      </el-card>

      <!-- 情感趋势 -->
      <el-card shadow="hover" class="section-card">
        <template #header><span>交互量趋势</span></template>
        <v-chart :option="sentimentOption" style="height: 250px" autoresize />
      </el-card>

      <!-- 热门问题 -->
      <el-card shadow="hover" class="section-card">
        <template #header><span>热门问题 Top 10</span></template>
        <el-table :data="report.popular_questions || []" stripe size="small">
          <el-table-column type="index" label="#" width="60" />
          <el-table-column prop="question" label="问题" show-overflow-tooltip />
          <el-table-column prop="count" label="次数" width="100" align="center">
            <template #default="{ row }">
              <el-tag type="warning">{{ row.count }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 服务建议 -->
      <el-card shadow="hover" class="section-card">
        <template #header><span>服务改进建议</span></template>
        <el-timeline>
          <el-timeline-item
            v-for="(s, idx) in report.suggestions"
            :key="idx"
            :timestamp="`建议 ${idx + 1}`"
            placement="top"
            :color="idx === 0 ? '#409EFF' : '#67C23A'"
          >
            <p>{{ s }}</p>
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </template>

    <!-- 空状态 -->
    <el-empty v-else description="点击「生成报告」开始分析" :image-size="120" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart } from 'echarts/charts'
import {
  TitleComponent, TooltipComponent, GridComponent, LegendComponent
} from 'echarts/components'
import { DocumentChecked } from '@element-plus/icons-vue'
import { getReport } from '../../api/admin'

use([CanvasRenderer, BarChart, LineChart, TitleComponent, TooltipComponent, GridComponent, LegendComponent])

const reportDays = ref(7)
const loading = ref(false)
const report = ref(null)

async function generateReport() {
  loading.value = true
  try {
    report.value = await getReport(reportDays.value)
  } catch (e) {
    console.error('生成报告失败:', e)
  } finally {
    loading.value = false
  }
}

const concernOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: 80, right: 40, top: 10, bottom: 20 },
  xAxis: { type: 'value' },
  yAxis: {
    type: 'category',
    data: (report.value?.top_concerns || []).map(c => c.category).reverse(),
    inverse: true,
  },
  series: [{
    data: (report.value?.top_concerns || []).map(c => c.score).reverse(),
    type: 'bar',
    barWidth: 24,
    itemStyle: {
      borderRadius: [0, 6, 6, 0],
      color: { type: 'linear', x: 0, y: 0, x2: 1, y2: 0,
        colorStops: [{ offset: 0, color: '#409EFF' }, { offset: 1, color: '#67C23A' }] },
    },
    label: { show: true, position: 'right' },
  }],
}))

const sentimentOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 40, right: 20, top: 10, bottom: 30 },
  xAxis: {
    type: 'category',
    data: (report.value?.sentiment_trend || []).map(d => d.date.slice(5)),
    axisLabel: { rotate: 45, fontSize: 10 },
  },
  yAxis: { type: 'value', minInterval: 1 },
  series: [{
    data: (report.value?.sentiment_trend || []).map(d => d.count),
    type: 'line',
    smooth: true,
    areaStyle: { color: 'rgba(103, 194, 58, 0.15)' },
    lineStyle: { color: '#67C23A', width: 2 },
    itemStyle: { color: '#67C23A' },
  }],
}))

// 首次自动加载
generateReport()
</script>

<style scoped>
.control-card { margin-bottom: 20px; }
.control-label { font-size: 14px; color: #606266; font-weight: 500; }
.summary-row { margin-bottom: 20px; }

.summary-card {
  text-align: center;
  margin-bottom: 16px;
}

.summary-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.summary-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.section-card { margin-bottom: 20px; }
</style>
