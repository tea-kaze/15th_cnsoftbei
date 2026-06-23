<template>
  <div class="digital-human" :class="{ speaking: isSpeaking, [emotion]: true }">
    <!-- CSS 模式 -->
    <div v-if="!camMode" class="avatar-wrapper">
      <div class="avatar-body" :class="{ breathing: !isSpeaking }">
        <!-- 发簪装饰 -->
        <div class="hairpin"></div>
        <!-- 后发髻 -->
        <div class="hair-bun"></div>
        <!-- 头部 -->
        <div class="head">
          <!-- 侧发 -->
          <div class="hair-side left"></div>
          <div class="hair-side right"></div>
          <!-- 刘海 -->
          <div class="hair-bangs"></div>
          <!-- 耳朵 -->
          <div class="ear left"></div>
          <div class="ear right"></div>
          <!-- 脸部 -->
          <div class="face">
            <!-- 眉毛 -->
            <div class="eyebrow left" :class="{ raised: emotion === 'surprised' }"></div>
            <div class="eyebrow right" :class="{ raised: emotion === 'surprised' }"></div>
            <!-- 眼睛 -->
            <div class="eye left">
              <div class="eyelid"></div>
              <div class="eye-white">
                <div class="iris">
                  <div class="pupil"></div>
                  <div class="highlight"></div>
                </div>
              </div>
            </div>
            <div class="eye right">
              <div class="eyelid"></div>
              <div class="eye-white">
                <div class="iris">
                  <div class="pupil"></div>
                  <div class="highlight"></div>
                </div>
              </div>
            </div>
            <!-- 鼻子 -->
            <div class="nose">
              <div class="nose-bridge"></div>
              <div class="nose-tip"></div>
            </div>
            <!-- 嘴巴 -->
            <div class="mouth-area">
              <div class="upper-lip"></div>
              <div class="mouth" :class="{ open: isSpeaking, smile: emotion === 'happy', sad: emotion === 'sad' }">
                <div class="tongue" v-if="isSpeaking"></div>
              </div>
              <div class="lower-lip"></div>
            </div>
            <!-- 腮红 -->
            <div class="blush left"></div>
            <div class="blush right"></div>
          </div>
        </div>
        <!-- 脖子 -->
        <div class="neck"></div>
        <!-- 身体 / 汉服 -->
        <div class="body">
          <div class="collar-inner"></div>
          <div class="collar left"></div>
          <div class="collar right"></div>
          <div class="robe">
            <div class="robe-pattern"></div>
          </div>
          <div class="sash"></div>
        </div>
      </div>
    </div>

    <!-- VTS/OBS Virtual Cam 模式 -->
    <VirtualCamView
      v-else
      :is-speaking="isSpeaking"
      :vts-connected="vtsConnected"
    />

    <div class="avatar-info">
      <span class="avatar-name">灵小导</span>
      <span class="avatar-status">
        <span class="status-dot" :class="{ active: isSpeaking, vts: vtsConnected }"></span>
        {{ statusText }}
      </span>
    </div>

    <!-- 模式切换 -->
    <div class="mode-toggle">
      <el-tooltip :content="camMode ? '切换到 CSS 头像' : '切换到 Virtual Cam (OBS + VTS)'">
        <span class="mode-btn" @click="camMode = !camMode">
          {{ camMode ? '🎭' : '📷' }}
        </span>
      </el-tooltip>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import VirtualCamView from './VirtualCamView.vue'
import api from '../../api/chat.js'

const props = defineProps({
  speaking: { type: Boolean, default: false },
  emotion: { type: String, default: 'neutral' },
})

const isSpeaking = ref(false)
const camMode = ref(localStorage.getItem('digitalHumanCamMode') === 'true')
const vtsConnected = ref(false)
let vtsTimer = null

watch(camMode, (val) => {
  localStorage.setItem('digitalHumanCamMode', val ? 'true' : 'false')
})

const statusText = computed(() => {
  if (isSpeaking.value) return '讲解中...'
  if (vtsConnected.value) return 'VTS 在线'
  return '在线'
})

async function checkVTSStatus() {
  try {
    const { data } = await api.get('/vts/status')
    vtsConnected.value = data?.connected || false
  } catch {
    vtsConnected.value = false
  }
}

watch(() => props.speaking, (val) => {
  isSpeaking.value = val
})

onMounted(() => {
  checkVTSStatus()
  vtsTimer = setInterval(checkVTSStatus, 10000)  // 每10秒探测VTS状态
})

onUnmounted(() => {
  if (vtsTimer) clearInterval(vtsTimer)
})
</script>

<style scoped>
/* ============================================
   数字人 CSS 头像 — 精美中国风导游
   ============================================ */

.digital-human {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 0 6px;
  transition: all 0.3s;
}

/* ---- 容器 ---- */
.avatar-wrapper {
  width: 120px;
  height: 180px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.avatar-body {
  position: relative;
  width: 80px;
}

/* ---- 呼吸动画（待机） ---- */
.avatar-body.breathing {
  animation: breathe 3.5s ease-in-out infinite;
}

@keyframes breathe {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.03); }
}

/* ---- 发髻（后脑勺） ---- */
.hair-bun {
  position: absolute;
  width: 36px;
  height: 30px;
  background: linear-gradient(180deg, #3C1F12, #2C160A);
  border-radius: 50%;
  top: -16px;
  left: 22px;
  z-index: 0;
}

/* ---- 发簪 ---- */
.hairpin {
  position: absolute;
  width: 3px;
  height: 28px;
  background: linear-gradient(180deg, #F9A825, #E65100);
  border-radius: 2px;
  top: -20px;
  left: 38px;
  z-index: 10;
  transform: rotate(-15deg);
}

.hairpin::after {
  content: '';
  position: absolute;
  width: 8px;
  height: 8px;
  background: #F9A825;
  border-radius: 50%;
  top: -4px;
  left: -3px;
  box-shadow: 0 0 4px rgba(249, 168, 37, 0.6);
}

/* ---- 头部 ---- */
.head {
  position: relative;
  width: 62px;
  height: 62px;
  margin: 0 auto;
  z-index: 1;
}

/* ---- 脸型（椭圆，不是正圆） ---- */
.face {
  width: 56px;
  height: 60px;
  background: linear-gradient(175deg, #FFF2E0 0%, #FDDCB5 40%, #F5C896 80%, #E8B88A 100%);
  border-radius: 50% 50% 45% 45%;
  position: absolute;
  top: 0;
  left: 3px;
  overflow: visible;
  box-shadow:
    inset 0 8px 12px rgba(255, 255, 255, 0.4),
    inset 0 -4px 8px rgba(200, 140, 100, 0.2),
    0 2px 8px rgba(0, 0, 0, 0.08);
}

/* ---- 耳朵 ---- */
.ear {
  position: absolute;
  width: 10px;
  height: 14px;
  background: linear-gradient(90deg, #F5C896, #FDDCB5);
  border-radius: 60% 40% 50% 50%;
  top: 22px;
  z-index: -1;
}

.ear.left { left: -3px; transform: rotate(-5deg); }
.ear.right { right: -3px; transform: rotate(5deg); }

.ear::after {
  content: '';
  position: absolute;
  width: 4px;
  height: 6px;
  background: rgba(200, 140, 100, 0.3);
  border-radius: 50%;
  top: 4px;
  left: 3px;
}

/* ---- 头发 ---- */

/* 刘海 */
.hair-bangs {
  position: absolute;
  top: -4px;
  left: -1px;
  width: 64px;
  height: 24px;
  background: linear-gradient(180deg, #2C160A, #3C1F12);
  border-radius: 60% 40% 0 0;
  z-index: 5;
}

.hair-bangs::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 6px;
  width: 48px;
  height: 6px;
  background: linear-gradient(180deg, rgba(44, 22, 10, 0.6), transparent);
  border-radius: 0 0 50% 50%;
}

/* 侧发 (鬓角) */
.hair-side {
  position: absolute;
  width: 8px;
  height: 36px;
  background: linear-gradient(180deg, #3C1F12, #2C160A);
  top: 8px;
  z-index: 5;
  border-radius: 0 0 4px 4px;
}

.hair-side.left { left: -1px; }
.hair-side.right { right: -1px; }

/* ---- 眉毛 ---- */
.eyebrow {
  position: absolute;
  width: 16px;
  height: 3px;
  background: linear-gradient(90deg, #8B6B4A, #5D3A1A, #3C1F12);
  top: 20px;
  z-index: 2;
  border-radius: 2px;
  transition: transform 0.25s ease;
}

.eyebrow.left { left: 7px; transform: rotate(-8deg); }
.eyebrow.right { right: 7px; transform: rotate(8deg); }
.eyebrow.raised { transform: translateY(-4px) !important; }

/* ---- 眼睛 ---- */
.eye {
  position: absolute;
  width: 14px;
  height: 16px;
  top: 24px;
  z-index: 1;
}

.eye.left { left: 8px; }
.eye.right { right: 8px; }

/* 眼白 */
.eye-white {
  width: 14px;
  height: 14px;
  background: #fff;
  border-radius: 50%;
  position: relative;
  overflow: hidden;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.06);
}

/* 虹膜 */
.iris {
  position: absolute;
  width: 9px;
  height: 9px;
  background: radial-gradient(circle at 40% 40%, #6B4226, #3C1F12);
  border-radius: 50%;
  top: 2px;
  left: 2px;
}

/* 瞳孔 */
.pupil {
  position: absolute;
  width: 4px;
  height: 4px;
  background: #0a0a0a;
  border-radius: 50%;
  top: 2px;
  left: 2px;
}

/* 高光 */
.highlight {
  position: absolute;
  width: 3px;
  height: 3px;
  background: #fff;
  border-radius: 50%;
  top: 0px;
  left: 3px;
}

/* 眼睑 */
.eyelid {
  position: absolute;
  width: 14px;
  height: 5px;
  background: rgba(245, 200, 150, 0.6);
  border-radius: 0 0 50% 50%;
  top: -1px;
  z-index: 2;
}

/* 眨眼动画 */
.eye {
  animation: blink 4s infinite;
}

@keyframes blink {
  0%, 94%, 100% { transform: scaleY(1); }
  96% { transform: scaleY(0.1); }
}

/* ---- 鼻子 ---- */
.nose {
  position: absolute;
  top: 32px;
  left: 27px;
  z-index: 1;
}

.nose-bridge {
  width: 3px;
  height: 8px;
  background: linear-gradient(180deg, rgba(200, 150, 120, 0.3), rgba(200, 150, 120, 0));
  border-radius: 2px;
}

.nose-tip {
  width: 6px;
  height: 4px;
  background: rgba(210, 160, 130, 0.5);
  border-radius: 50%;
  margin-left: -1px;
}

/* ---- 嘴巴区域 ---- */
.mouth-area {
  position: absolute;
  top: 42px;
  left: 17px;
  width: 22px;
  height: 14px;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.upper-lip {
  width: 14px;
  height: 2px;
  background: rgba(210, 140, 120, 0.4);
  border-radius: 50%;
  margin-bottom: 1px;
}

.lower-lip {
  width: 14px;
  height: 2px;
  background: rgba(210, 140, 120, 0.3);
  border-radius: 50%;
  margin-top: 1px;
}

/* 嘴巴 */
.mouth {
  width: 14px;
  height: 4px;
  background: #D4786A;
  border-radius: 0 0 8px 8px;
  transition: all 0.2s ease;
  position: relative;
}

/* 舌头 */
.tongue {
  position: absolute;
  bottom: -3px;
  left: 3px;
  width: 8px;
  height: 5px;
  background: #E8908A;
  border-radius: 2px 2px 4px 4px;
}

/* 嘴巴状态 */
.mouth.open {
  width: 10px;
  height: 10px;
  border-radius: 4px;
  background: #C06058;
  margin-top: 1px;
}

.mouth.smile {
  width: 18px;
  height: 5px;
  border-radius: 0 0 12px 12px;
  margin-top: 1px;
}

.mouth.sad {
  width: 12px;
  height: 5px;
  border-radius: 10px 10px 0 0;
  background: #D4786A;
}

/* ---- 腮红 ---- */
.blush {
  position: absolute;
  width: 10px;
  height: 6px;
  background: radial-gradient(ellipse, rgba(255, 150, 140, 0.35), transparent);
  border-radius: 50%;
  top: 34px;
  z-index: 0;
}

.blush.left { left: 4px; }
.blush.right { right: 4px; }

/* ---- 脖子 ---- */
.neck {
  width: 16px;
  height: 10px;
  background: linear-gradient(180deg, #F5C896, #E8B88A);
  margin: 0 auto;
  border-radius: 0 0 4px 4px;
}

/* ---- 身体 / 汉服 ---- */
.body {
  position: relative;
  width: 64px;
  margin: 0 auto;
}

/* 内领 */
.collar-inner {
  width: 16px;
  height: 6px;
  background: #FFF8E1;
  margin: 0 auto;
  border-radius: 0 0 4px 4px;
}

/* 外领 */
.collar {
  position: absolute;
  width: 0;
  height: 0;
  border-bottom: 10px solid #C62828;
  top: 0;
  z-index: 3;
}

.collar.left {
  left: 16px;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-bottom: 10px solid #C62828;
}

.collar.right {
  right: 16px;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-bottom: 10px solid #C62828;
}

/* 衣袍 */
.robe {
  width: 64px;
  height: 50px;
  background: linear-gradient(180deg, #D32F2F 0%, #C62828 30%, #B71C1C 100%);
  border-radius: 10px 10px 6px 6px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

/* 衣袍金色纹样 */
.robe-pattern {
  position: absolute;
  top: 14px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 24px;
  border: 2px solid rgba(255, 215, 0, 0.35);
  border-radius: 2px;
}

.robe-pattern::before {
  content: '';
  position: absolute;
  top: 4px;
  left: 4px;
  width: 8px;
  height: 12px;
  border: 1px solid rgba(255, 215, 0, 0.3);
  border-radius: 1px;
}

.robe-pattern::after {
  content: '';
  position: absolute;
  top: 6px;
  left: 6px;
  width: 4px;
  height: 8px;
  background: rgba(255, 215, 0, 0.25);
  border-radius: 50%;
}

/* 腰带 */
.sash {
  width: 64px;
  height: 5px;
  background: linear-gradient(180deg, #F9A825, #E65100);
  border-radius: 2px;
  margin-top: 2px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

/* ---- 名字 ---- */
.avatar-info {
  text-align: center;
  margin-top: 6px;
}

.avatar-name {
  font-size: 14px;
  font-weight: 700;
  color: #5D4037;
  letter-spacing: 1px;
}

.avatar-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  font-size: 11px;
  color: #67C23A;
  margin-top: 2px;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #67C23A;
  display: inline-block;
  box-shadow: 0 0 4px rgba(103, 194, 58, 0.4);
}

.status-dot.active {
  background: #409EFF;
  box-shadow: 0 0 6px rgba(64, 158, 255, 0.6);
  animation: pulse 0.8s infinite;
}

.status-dot.vts {
  background: #E6A23C;
  box-shadow: 0 0 6px rgba(230, 162, 60, 0.5);
}

.mode-toggle {
  margin-top: 4px;
}

.mode-btn {
  font-size: 15px;
  cursor: pointer;
  opacity: 0.5;
  transition: all 0.2s;
  padding: 3px 8px;
  border-radius: 10px;
  background: rgba(255,255,255,0.2);
}

.mode-btn:hover {
  opacity: 1;
  background: rgba(255,255,255,0.35);
}

/* ---- 动画 ---- */
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(1.4); }
}

/* 说话时的头部微动 */
.digital-human.speaking .avatar-body {
  animation: speakBob 0.4s infinite alternate ease-in-out;
}

@keyframes speakBob {
  from { transform: translateY(0) rotate(0deg); }
  to { transform: translateY(-2px) rotate(0.5deg); }
}

/* 惊讶表情 */
.digital-human.surprised .mouth {
  width: 10px !important;
  height: 12px !important;
  border-radius: 50% !important;
  background: #C06058 !important;
  margin-top: 2px !important;
}

.digital-human.surprised .iris {
  transform: scale(0.7);
}

/* 开心时的整体微动 */
.digital-human.happy .avatar-body {
  animation: happySway 0.7s infinite alternate ease-in-out;
}

@keyframes happySway {
  from { transform: translateX(-1px) rotate(-1deg); }
  to { transform: translateX(1px) rotate(1deg); }
}

/* 难过时低头 */
.digital-human.sad .avatar-body {
  transform: translateY(2px);
  transition: transform 0.5s ease;
}
</style>
