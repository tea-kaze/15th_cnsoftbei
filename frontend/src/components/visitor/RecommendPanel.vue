<template>
  <div class="recommend-panel">
    <!-- 兴趣选择 -->
    <div v-if="!selectedRoute" class="interest-cards">
      <h3>告诉我您的兴趣，我为您推荐专属路线</h3>
      <div class="cards-row">
        <div
          v-for="card in interestCards"
          :key="card.key"
          class="interest-card"
          :class="{ active: activeCard === card.key }"
          @click="selectInterest(card.key, card.label)"
        >
          <span class="card-icon">{{ card.icon }}</span>
          <span class="card-label">{{ card.label }}</span>
          <span class="card-desc">{{ card.desc }}</span>
        </div>
      </div>
      <div class="custom-input">
        <el-input
          v-model="customInterest"
          placeholder="或输入您的兴趣，如'我想带老人和孩子轻松游'..."
          @keyup.enter="selectInterest('custom', customInterest)"
        >
          <template #suffix>
            <el-button type="primary" size="small" @click="selectInterest('custom', customInterest)" :disabled="!customInterest.trim()">
              推荐
            </el-button>
          </template>
        </el-input>
      </div>
    </div>

    <!-- 路线详情 -->
    <div v-else class="route-detail">
      <div class="route-header">
        <button class="back-btn" @click="selectedRoute = null">← 重新选择</button>
        <span class="route-type">{{ selectedRoute.type }}</span>
      </div>

      <div class="route-card">
        <div class="route-name">
          <span class="route-icon">{{ selectedRoute.icon }}</span>
          {{ selectedRoute.name }}
        </div>
        <div class="route-meta">
          <el-tag size="small">{{ selectedRoute.duration }}</el-tag>
        </div>
        <p class="route-reason">{{ selectedRoute.reason }}</p>
        <p class="route-desc">{{ selectedRoute.description }}</p>
      </div>

      <!-- 景点时间线 -->
      <div class="spots-timeline">
        <h4>游览路线</h4>
        <el-timeline>
          <el-timeline-item
            v-for="(spot, idx) in selectedRoute.spots"
            :key="idx"
            :timestamp="`第${idx + 1}站`"
            placement="top"
            :color="idx === 0 ? '#409EFF' : '#67C23A'"
          >
            <div class="spot-item">
              <strong>{{ spot.name }}</strong>
              <p>{{ spot.highlight }}</p>
            </div>
          </el-timeline-item>
        </el-timeline>
      </div>

      <!-- 贴士 -->
      <div class="tips-section">
        <h4>实用小贴士</h4>
        <ul>
          <li v-for="(tip, idx) in selectedRoute.tips" :key="idx">💡 {{ tip }}</li>
        </ul>
      </div>

      <!-- 追问 -->
      <div class="route-actions">
        <el-button type="primary" plain @click="$emit('ask', `请详细介绍一下${selectedRoute.name}`)">
          详细讲解这条路线
        </el-button>
        <el-button plain @click="$emit('ask', `${selectedRoute.name}中哪个景点最值得看？`)">
          哪个景点最值得看？
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { getRecommendation } from '../../api/chat'

const emit = defineEmits(['ask'])

const selectedRoute = ref(null)
const activeCard = ref('')
const customInterest = ref('')

const interestCards = [
  { key: 'history', icon: '🏛️', label: '历史文化', desc: '佛教文化、千年古迹' },
  { key: 'nature', icon: '🏞️', label: '自然风光', desc: '太湖山水、摄影打卡' },
  { key: 'family', icon: '👨‍👩‍👧‍👦', label: '亲子家庭', desc: '轻松休闲、寓教于乐' },
]

async function selectInterest(key, label) {
  activeCard.value = key
  try {
    const res = await getRecommendation({ interest: label })
    if (res.recommended) {
      selectedRoute.value = res.recommended
    } else if (res.routes) {
      // 匹配对应路线
      selectedRoute.value = res.routes.find(r => r.id === key) || res.routes[0]
    }
  } catch (e) {
    console.error('推荐失败:', e)
  }
}
</script>

<style scoped>
.recommend-panel {
  padding: 12px 0;
}

.interest-cards h3 {
  font-size: 15px;
  color: #5D4037;
  text-align: center;
  margin-bottom: 12px;
}

.cards-row {
  display: flex;
  gap: 10px;
  margin-bottom: 12px;
}

.interest-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 14px 8px;
  background: #fff;
  border: 2px solid #EFEBE9;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.interest-card:hover,
.interest-card.active {
  border-color: #8B4513;
  background: #F8F4EB;
}

.card-icon { font-size: 28px; margin-bottom: 6px; }
.card-label { font-size: 14px; font-weight: 600; color: #5D4037; }
.card-desc { font-size: 11px; color: #A1887F; margin-top: 2px; }

.custom-input {
  margin-top: 4px;
}

.route-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.back-btn {
  background: none;
  border: none;
  color: #8B4513;
  font-size: 14px;
  cursor: pointer;
  padding: 0;
}

.route-type {
  background: #F8F4EB;
  color: #8B4513;
  padding: 2px 10px;
  border-radius: 10px;
  font-size: 12px;
}

.route-card {
  background: linear-gradient(135deg, #F8F4EB, #FFF);
  border: 1px solid #EFEBE9;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
}

.route-name {
  font-size: 18px;
  font-weight: 700;
  color: #5D4037;
  margin-bottom: 6px;
}

.route-icon { margin-right: 6px; }

.route-meta { margin-bottom: 8px; }

.route-reason {
  font-size: 13px;
  color: #8B4513;
  font-weight: 500;
  margin-bottom: 4px;
}

.route-desc {
  font-size: 13px;
  color: #8D6E63;
  line-height: 1.5;
}

.spots-timeline {
  margin-bottom: 16px;
}

.spots-timeline h4,
.tips-section h4 {
  font-size: 15px;
  color: #5D4037;
  margin-bottom: 10px;
}

.spot-item strong {
  font-size: 14px;
  color: #303133;
}

.spot-item p {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.tips-section ul {
  list-style: none;
  padding: 0;
}

.tips-section li {
  font-size: 13px;
  color: #6D4C41;
  padding: 4px 0;
  line-height: 1.5;
}

.route-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 12px;
}
</style>
