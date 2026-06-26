<template>
  <div class="digital-human" :class="{ speaking: isSpeaking, [emotion]: true }">
    <!-- CSS 模式 -->
    <div v-if="!camMode" class="avatar-wrapper">
      <!-- 曼荼罗光环背景 -->
      <div class="mandala-backdrop">
        <div class="mandala-halo"></div>
        <div class="mandala-ring ring-outer"></div>
        <div class="mandala-ring ring-inner"></div>
        <div class="mandala-lotus">
          <span
            v-for="n in 8"
            :key="n"
            class="lotus-petal"
            :style="{ transform: `rotate(${(n - 1) * 45}deg) translateY(-58px)` }"
          ></span>
        </div>
        <div class="mandala-center-glow"></div>
      </div>

      <!-- 浮动灵光粒子 -->
      <div class="spirit-particles">
        <span
          v-for="n in 6"
          :key="n"
          class="particle"
          :style="{
            '--delay': `${(n - 1) * 1.8}s`,
            '--drift': `${(n % 2 === 0 ? 1 : -1) * (15 + n * 5)}px`,
            '--size': `${3 + (n % 3)}px`,
            left: `${15 + n * 12}%`,
          }"
        ></span>
      </div>

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
      <div class="name-plate">
        <span class="name-bracket">【</span>
        <span class="avatar-name">灵小导</span>
        <span class="name-bracket">】</span>
      </div>
      <div class="avatar-status">
        <span class="status-dot" :class="{ active: isSpeaking, vts: vtsConnected }"></span>
        <span class="status-label">{{ statusText }}</span>
      </div>
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
  vtsTimer = setInterval(checkVTSStatus, 10000)
})

onUnmounted(() => {
  if (vtsTimer) clearInterval(vtsTimer)
})
</script>

<style scoped>
/* ============================================
   数字人 CSS 头像 — 灵小导 · 灵山胜境 AI 导游
   设计系统：佛教曼荼罗 + 中国风汉服 + 灵光粒子
   ============================================ */

/* ============================================
   第一层：CSS 变量体系
   ============================================ */
.digital-human {
  /* ---- 肤色 ---- */
  --dh-skin-light: #FFF2E0;
  --dh-skin-mid: #FDDCB5;
  --dh-skin-shadow: #F5C896;
  --dh-skin-deep: #E8B88A;
  --dh-skin-blush: rgba(255, 150, 140, 0.35);

  /* ---- 发色 ---- */
  --dh-hair-root: #1A0E06;
  --dh-hair-mid: #2C160A;
  --dh-hair-tip: #3C1F12;
  --dh-hair-sheen: #5D3A1A;

  /* ---- 汉服 ---- */
  --dh-robe-bright: #D32F2F;
  --dh-robe-mid: #C62828;
  --dh-robe-deep: #B71C1C;
  --dh-robe-inner: #FFF8E1;
  --dh-collar: #8B1A1A;

  /* ---- 金色点缀 ---- */
  --dh-gold-light: #FFE082;
  --dh-gold: #F9A825;
  --dh-gold-deep: #E65100;
  --dh-gold-glow: rgba(249, 168, 37, 0.5);

  /* ---- 五官 ---- */
  --dh-brow: #5D3A1A;
  --dh-eye-iris: #6B4226;
  --dh-eye-pupil: #0a0a0a;
  --dh-mouth-neutral: #D4786A;
  --dh-mouth-open: #C06058;
  --dh-tongue: #E8908A;

  /* ---- 缩放 ---- */
  --dh-scale: 0.9;

  /* ---- 动画时间 ---- */
  --dh-breathe-duration: 4s;
  --dh-blink-interval: 4.5s;
  --dh-emotion-transition: 0.4s cubic-bezier(0.25, 0.1, 0.25, 1);
  --dh-mandala-rotation: 60s;

  /* ---- 光晕 ---- */
  --dh-aura-color: rgba(249, 168, 37, 0.3);
  --dh-aura-speaking: rgba(249, 168, 37, 0.6);
  --dh-face-shadow: 0 3px 12px rgba(0, 0, 0, 0.1);

  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 0 4px;
  position: relative;
  z-index: 1;
}

/* ============================================
   第二层：容器与等比缩放
   ============================================ */
.avatar-wrapper {
  width: calc(180px * var(--dh-scale));
  height: calc(270px * var(--dh-scale));
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
}

.avatar-body {
  position: relative;
  width: calc(80px * var(--dh-scale));
  transition: transform var(--dh-emotion-transition);
  z-index: 1;
}

/* ---- 响应式缩放 ---- */
@media (max-width: 360px) {
  .digital-human { --dh-scale: 0.85; }
}
@media (min-width: 481px) {
  .digital-human { --dh-scale: 1.0; }
}

/* ============================================
   第三层：曼荼罗光环背景
   ============================================ */
.mandala-backdrop {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: calc(160px * var(--dh-scale));
  height: calc(160px * var(--dh-scale));
  animation: mandalaRotate var(--dh-mandala-rotation) linear infinite;
  z-index: 0;
}

.mandala-halo {
  position: absolute;
  inset: calc(-30px * var(--dh-scale));
  border-radius: 50%;
  background: radial-gradient(circle,
    rgba(249, 168, 37, 0.12) 0%,
    rgba(249, 168, 37, 0.05) 50%,
    transparent 70%
  );
  transition: background var(--dh-emotion-transition);
}

.mandala-ring {
  position: absolute;
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.ring-outer {
  width: calc(150px * var(--dh-scale));
  height: calc(150px * var(--dh-scale));
  border: calc(1.5px * var(--dh-scale)) dashed rgba(249, 168, 37, 0.2);
}

.ring-inner {
  width: calc(120px * var(--dh-scale));
  height: calc(120px * var(--dh-scale));
  border: calc(1px * var(--dh-scale)) solid rgba(249, 168, 37, 0.15);
  box-shadow: inset 0 0 calc(30px * var(--dh-scale)) rgba(249, 168, 37, 0.05);
}

/* 莲花瓣 */
.mandala-lotus {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
}

.lotus-petal {
  position: absolute;
  width: calc(18px * var(--dh-scale));
  height: calc(36px * var(--dh-scale));
  background: linear-gradient(180deg,
    rgba(255, 224, 130, 0.22) 0%,
    rgba(249, 168, 37, 0.08) 100%
  );
  border-radius: 50%;
  transform-origin: center top;
  margin-left: calc(-9px * var(--dh-scale));
  margin-top: 0;
}

/* 中心光晕 */
.mandala-center-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: calc(70px * var(--dh-scale));
  height: calc(70px * var(--dh-scale));
  border-radius: 50%;
  background: radial-gradient(circle,
    rgba(255, 224, 130, 0.12) 0%,
    transparent 70%
  );
  transition: all var(--dh-emotion-transition);
}

/* ---- 曼荼罗旋转动画 ---- */
@keyframes mandalaRotate {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to   { transform: translate(-50%, -50%) rotate(360deg); }
}

/* ============================================
   第四层：浮动灵光粒子
   ============================================ */
.spirit-particles {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.particle {
  position: absolute;
  bottom: 10%;
  width: var(--size);
  height: var(--size);
  background: var(--dh-gold-light);
  border-radius: 50%;
  opacity: 0;
  box-shadow:
    0 0 calc(var(--size) * 2) var(--dh-gold),
    0 0 calc(var(--size) * 4) var(--dh-gold-glow);
  animation: particleFloat 6s ease-in-out var(--delay) infinite;
}

@keyframes particleFloat {
  0% {
    opacity: 0;
    transform: translateY(0) translateX(0) scale(0.5);
  }
  15% {
    opacity: 0.7;
  }
  50% {
    opacity: 0.35;
    transform: translateY(calc(-60px * var(--dh-scale))) translateX(var(--drift)) scale(1.2);
  }
  85% {
    opacity: 0.08;
  }
  100% {
    opacity: 0;
    transform: translateY(calc(-130px * var(--dh-scale))) translateX(calc(var(--drift) * -0.5)) scale(0.3);
  }
}

/* ============================================
   第五层：色彩与渐变深度优化
   ============================================ */

/* ---- 呼吸动画（待机） ---- */
.avatar-body.breathing {
  animation: breathe var(--dh-breathe-duration) ease-in-out infinite;
}

@keyframes breathe {
  0%, 100% { transform: scale(1) translateY(0); }
  40%      { transform: scale(1.025) translateY(calc(-2px * var(--dh-scale))); }
  70%      { transform: scale(1.01) translateY(calc(-1px * var(--dh-scale))); }
}

/* ---- 发髻 ---- */
.hair-bun {
  position: absolute;
  width: calc(36px * var(--dh-scale));
  height: calc(30px * var(--dh-scale));
  background:
    radial-gradient(ellipse at 50% 30%, var(--dh-hair-sheen) 0%, transparent 50%),
    linear-gradient(180deg, var(--dh-hair-mid), var(--dh-hair-root));
  border-radius: 50%;
  top: calc(-16px * var(--dh-scale));
  left: calc(22px * var(--dh-scale));
  z-index: 0;
}

/* ---- 发簪 ---- */
.hairpin {
  position: absolute;
  width: calc(3px * var(--dh-scale));
  height: calc(28px * var(--dh-scale));
  background: linear-gradient(180deg, var(--dh-gold-light), var(--dh-gold), var(--dh-gold-deep));
  border-radius: calc(2px * var(--dh-scale));
  top: calc(-20px * var(--dh-scale));
  left: calc(38px * var(--dh-scale));
  z-index: 10;
  transform: rotate(-15deg);
}

/* 红宝石点缀 */
.hairpin::before {
  content: '';
  position: absolute;
  width: calc(5px * var(--dh-scale));
  height: calc(5px * var(--dh-scale));
  background: #FF5252;
  border-radius: 50%;
  top: calc(2px * var(--dh-scale));
  left: calc(-1px * var(--dh-scale));
  box-shadow: 0 0 calc(3px * var(--dh-scale)) rgba(255, 82, 82, 0.5);
  z-index: 1;
}

/* 金色珠子 */
.hairpin::after {
  content: '';
  position: absolute;
  width: calc(8px * var(--dh-scale));
  height: calc(8px * var(--dh-scale));
  background: var(--dh-gold);
  border-radius: 50%;
  top: calc(-4px * var(--dh-scale));
  left: calc(-3px * var(--dh-scale));
  box-shadow: 0 0 calc(4px * var(--dh-scale)) var(--dh-gold-glow);
}

/* ---- 头部 ---- */
.head {
  position: relative;
  width: calc(62px * var(--dh-scale));
  height: calc(62px * var(--dh-scale));
  margin: 0 auto;
  z-index: 1;
}

/* ---- 脸型 ---- */
.face {
  width: calc(56px * var(--dh-scale));
  height: calc(60px * var(--dh-scale));
  background:
    radial-gradient(ellipse at 30% 20%, rgba(255, 255, 240, 0.35) 0%, transparent 50%),
    linear-gradient(175deg,
      var(--dh-skin-light) 0%,
      var(--dh-skin-mid) 35%,
      var(--dh-skin-shadow) 75%,
      var(--dh-skin-deep) 100%
    );
  border-radius: 50% 50% 45% 45%;
  position: absolute;
  top: 0;
  left: calc(3px * var(--dh-scale));
  overflow: visible;
  box-shadow:
    inset 0 calc(6px * var(--dh-scale)) calc(16px * var(--dh-scale)) rgba(255, 255, 255, 0.35),
    inset 0 calc(-6px * var(--dh-scale)) calc(14px * var(--dh-scale)) rgba(180, 120, 90, 0.25),
    var(--dh-face-shadow);
}

/* ---- 耳朵 ---- */
.ear {
  position: absolute;
  width: calc(10px * var(--dh-scale));
  height: calc(14px * var(--dh-scale));
  background: linear-gradient(90deg, var(--dh-skin-shadow), var(--dh-skin-mid));
  border-radius: 60% 40% 50% 50%;
  top: calc(22px * var(--dh-scale));
  z-index: -1;
}

.ear.left { left: calc(-3px * var(--dh-scale)); transform: rotate(-5deg); }
.ear.right { right: calc(-3px * var(--dh-scale)); transform: rotate(5deg); }

.ear::after {
  content: '';
  position: absolute;
  width: calc(4px * var(--dh-scale));
  height: calc(6px * var(--dh-scale));
  background: rgba(200, 140, 100, 0.3);
  border-radius: 50%;
  top: calc(4px * var(--dh-scale));
  left: calc(3px * var(--dh-scale));
}

/* ---- 头发 ---- */

/* 刘海 */
.hair-bangs {
  position: absolute;
  top: calc(-4px * var(--dh-scale));
  left: calc(-1px * var(--dh-scale));
  width: calc(64px * var(--dh-scale));
  height: calc(24px * var(--dh-scale));
  background:
    radial-gradient(ellipse at 40% 50%, var(--dh-hair-sheen) 0%, transparent 60%),
    linear-gradient(180deg, var(--dh-hair-mid), var(--dh-hair-root));
  border-radius: 60% 40% 0 0;
  z-index: 5;
}

.hair-bangs::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: calc(6px * var(--dh-scale));
  width: calc(48px * var(--dh-scale));
  height: calc(6px * var(--dh-scale));
  background: linear-gradient(180deg, rgba(44, 22, 10, 0.6), transparent);
  border-radius: 0 0 50% 50%;
}

/* 刘海光泽 */
.hair-bangs::before {
  content: '';
  position: absolute;
  top: calc(2px * var(--dh-scale));
  left: calc(12px * var(--dh-scale));
  width: calc(18px * var(--dh-scale));
  height: calc(3px * var(--dh-scale));
  background: rgba(100, 60, 30, 0.35);
  border-radius: 50%;
  z-index: 1;
}

/* 侧发 (鬓角) */
.hair-side {
  position: absolute;
  width: calc(8px * var(--dh-scale));
  height: calc(36px * var(--dh-scale));
  background: linear-gradient(180deg, var(--dh-hair-tip), var(--dh-hair-mid));
  top: calc(8px * var(--dh-scale));
  z-index: 5;
  border-radius: 0 0 calc(4px * var(--dh-scale)) calc(4px * var(--dh-scale));
}

.hair-side.left { left: calc(-1px * var(--dh-scale)); }
.hair-side.right { right: calc(-1px * var(--dh-scale)); }

/* ---- 眉毛 ---- */
.eyebrow {
  position: absolute;
  width: calc(16px * var(--dh-scale));
  height: calc(3px * var(--dh-scale));
  background: linear-gradient(90deg, #8B6B4A, var(--dh-brow), var(--dh-hair-root));
  top: calc(20px * var(--dh-scale));
  z-index: 2;
  border-radius: calc(2px * var(--dh-scale));
  transition: all var(--dh-emotion-transition);
}

.eyebrow.left { left: calc(7px * var(--dh-scale)); transform: rotate(-8deg); }
.eyebrow.right { right: calc(7px * var(--dh-scale)); transform: rotate(8deg); }
.eyebrow.raised { transform: translateY(calc(-4px * var(--dh-scale))) !important; }

/* ---- 眼睛 ---- */
.eye {
  position: absolute;
  width: calc(14px * var(--dh-scale));
  height: calc(16px * var(--dh-scale));
  top: calc(24px * var(--dh-scale));
  z-index: 1;
}

.eye.left { left: calc(8px * var(--dh-scale)); }
.eye.right { right: calc(8px * var(--dh-scale)); }

/* 眼白 */
.eye-white {
  width: calc(14px * var(--dh-scale));
  height: calc(14px * var(--dh-scale));
  background: #fff;
  border-radius: 50%;
  position: relative;
  overflow: hidden;
  box-shadow: inset 0 calc(1px * var(--dh-scale)) calc(3px * var(--dh-scale)) rgba(0,0,0,0.06);
}

/* 虹膜 */
.iris {
  position: absolute;
  width: calc(9px * var(--dh-scale));
  height: calc(9px * var(--dh-scale));
  background: radial-gradient(circle at 40% 40%, var(--dh-eye-iris), var(--dh-hair-root));
  border-radius: 50%;
  top: calc(2px * var(--dh-scale));
  left: calc(2px * var(--dh-scale));
  transition: transform var(--dh-emotion-transition);
}

/* 瞳孔 */
.pupil {
  position: absolute;
  width: calc(4px * var(--dh-scale));
  height: calc(4px * var(--dh-scale));
  background: var(--dh-eye-pupil);
  border-radius: 50%;
  top: calc(2px * var(--dh-scale));
  left: calc(2px * var(--dh-scale));
}

/* 高光 */
.highlight {
  position: absolute;
  width: calc(3px * var(--dh-scale));
  height: calc(3px * var(--dh-scale));
  background: #fff;
  border-radius: 50%;
  top: 0;
  left: calc(3px * var(--dh-scale));
  animation: eyeSparkle 3s ease-in-out infinite;
}

/* 眼睑 — 眨眼动画 */
.eyelid {
  position: absolute;
  width: calc(14px * var(--dh-scale));
  height: calc(5px * var(--dh-scale));
  background: rgba(245, 200, 150, 0.6);
  border-radius: 0 0 50% 50%;
  top: calc(-1px * var(--dh-scale));
  z-index: 2;
  animation: eyelidBlink var(--dh-blink-interval) ease-in-out infinite;
  transform-origin: top center;
}

@keyframes eyelidBlink {
  0%, 92% { transform: scaleY(0.2); }
  94%     { transform: scaleY(1.3); }
  96%     { transform: scaleY(0.2); }
  100%    { transform: scaleY(0.2); }
}

@keyframes eyeSparkle {
  0%, 85% { opacity: 1; transform: scale(1); }
  88%     { opacity: 1; transform: scale(1.5); }
  91%     { opacity: 0.5; transform: scale(0.7); }
  94%     { opacity: 1; transform: scale(1); }
  100%    { opacity: 1; transform: scale(1); }
}

/* ---- 鼻子 ---- */
.nose {
  position: absolute;
  top: calc(32px * var(--dh-scale));
  left: calc(27px * var(--dh-scale));
  z-index: 1;
}

.nose-bridge {
  width: calc(3px * var(--dh-scale));
  height: calc(8px * var(--dh-scale));
  background: linear-gradient(180deg, rgba(200, 150, 120, 0.3), rgba(200, 150, 120, 0));
  border-radius: calc(2px * var(--dh-scale));
}

.nose-tip {
  width: calc(6px * var(--dh-scale));
  height: calc(4px * var(--dh-scale));
  background: rgba(210, 160, 130, 0.5);
  border-radius: 50%;
  margin-left: calc(-1px * var(--dh-scale));
}

/* ---- 嘴巴区域 ---- */
.mouth-area {
  position: absolute;
  top: calc(42px * var(--dh-scale));
  left: calc(17px * var(--dh-scale));
  width: calc(22px * var(--dh-scale));
  height: calc(14px * var(--dh-scale));
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.upper-lip {
  width: calc(14px * var(--dh-scale));
  height: calc(2px * var(--dh-scale));
  background: rgba(210, 140, 120, 0.4);
  border-radius: 50%;
  margin-bottom: calc(1px * var(--dh-scale));
}

.lower-lip {
  width: calc(14px * var(--dh-scale));
  height: calc(2px * var(--dh-scale));
  background: rgba(210, 140, 120, 0.3);
  border-radius: 50%;
  margin-top: calc(1px * var(--dh-scale));
}

/* 嘴巴 */
.mouth {
  width: calc(14px * var(--dh-scale));
  height: calc(4px * var(--dh-scale));
  background: var(--dh-mouth-neutral);
  border-radius: 0 0 calc(8px * var(--dh-scale)) calc(8px * var(--dh-scale));
  transition: all var(--dh-emotion-transition);
  position: relative;
}

/* 舌头 */
.tongue {
  position: absolute;
  bottom: calc(-3px * var(--dh-scale));
  left: calc(3px * var(--dh-scale));
  width: calc(8px * var(--dh-scale));
  height: calc(5px * var(--dh-scale));
  background: var(--dh-tongue);
  border-radius: calc(2px * var(--dh-scale)) calc(2px * var(--dh-scale)) calc(4px * var(--dh-scale)) calc(4px * var(--dh-scale));
}

/* 嘴巴状态 */
.mouth.open {
  width: calc(10px * var(--dh-scale));
  height: calc(10px * var(--dh-scale));
  border-radius: calc(4px * var(--dh-scale));
  background: var(--dh-mouth-open);
  margin-top: calc(1px * var(--dh-scale));
}

.mouth.smile {
  width: calc(18px * var(--dh-scale));
  height: calc(5px * var(--dh-scale));
  border-radius: 0 0 calc(12px * var(--dh-scale)) calc(12px * var(--dh-scale));
  margin-top: calc(1px * var(--dh-scale));
}

.mouth.sad {
  width: calc(12px * var(--dh-scale));
  height: calc(5px * var(--dh-scale));
  border-radius: calc(10px * var(--dh-scale)) calc(10px * var(--dh-scale)) 0 0;
  background: var(--dh-mouth-neutral);
}

/* ---- 腮红 ---- */
.blush {
  position: absolute;
  width: calc(10px * var(--dh-scale));
  height: calc(6px * var(--dh-scale));
  background: radial-gradient(ellipse, var(--dh-skin-blush), transparent);
  border-radius: 50%;
  top: calc(34px * var(--dh-scale));
  z-index: 0;
  transition: all var(--dh-emotion-transition);
}

.blush.left { left: calc(4px * var(--dh-scale)); }
.blush.right { right: calc(4px * var(--dh-scale)); }

/* ---- 脖子 ---- */
.neck {
  width: calc(16px * var(--dh-scale));
  height: calc(10px * var(--dh-scale));
  background: linear-gradient(180deg, var(--dh-skin-shadow), var(--dh-skin-deep));
  margin: 0 auto;
  border-radius: 0 0 calc(4px * var(--dh-scale)) calc(4px * var(--dh-scale));
}

/* ---- 身体 / 汉服 ---- */
.body {
  position: relative;
  width: calc(64px * var(--dh-scale));
  margin: 0 auto;
}

/* 内领 */
.collar-inner {
  width: calc(16px * var(--dh-scale));
  height: calc(6px * var(--dh-scale));
  background: var(--dh-robe-inner);
  margin: 0 auto;
  border-radius: 0 0 calc(4px * var(--dh-scale)) calc(4px * var(--dh-scale));
}

/* 外领 */
.collar {
  position: absolute;
  top: 0;
  z-index: 3;
}

.collar.left {
  left: calc(16px * var(--dh-scale));
  border-left: calc(6px * var(--dh-scale)) solid transparent;
  border-right: calc(6px * var(--dh-scale)) solid transparent;
  border-bottom: calc(10px * var(--dh-scale)) solid var(--dh-collar);
}

.collar.right {
  right: calc(16px * var(--dh-scale));
  border-left: calc(6px * var(--dh-scale)) solid transparent;
  border-right: calc(6px * var(--dh-scale)) solid transparent;
  border-bottom: calc(10px * var(--dh-scale)) solid var(--dh-collar);
}

/* 衣袍 */
.robe {
  width: calc(64px * var(--dh-scale));
  height: calc(50px * var(--dh-scale));
  background:
    linear-gradient(90deg,
      transparent 0%,
      rgba(255,255,255,0.04) 40%,
      rgba(255,255,255,0.06) 50%,
      rgba(255,255,255,0.04) 60%,
      transparent 100%
    ),
    linear-gradient(180deg,
      var(--dh-robe-bright) 0%,
      var(--dh-robe-mid) 40%,
      var(--dh-robe-deep) 100%
    );
  border-radius: calc(10px * var(--dh-scale)) calc(10px * var(--dh-scale)) calc(6px * var(--dh-scale)) calc(6px * var(--dh-scale));
  position: relative;
  overflow: hidden;
  box-shadow:
    inset 0 calc(2px * var(--dh-scale)) calc(8px * var(--dh-scale)) rgba(255,255,255,0.1),
    0 calc(3px * var(--dh-scale)) calc(12px * var(--dh-scale)) rgba(0,0,0,0.18);
}

/* 衣袍纹样 — 菱形 + 圆 + 点（佛教纹饰） */
.robe-pattern {
  position: absolute;
  top: calc(14px * var(--dh-scale));
  left: 50%;
  width: calc(24px * var(--dh-scale));
  height: calc(24px * var(--dh-scale));
  border: calc(1.5px * var(--dh-scale)) solid rgba(255, 215, 0, 0.4);
  border-radius: 1px;
  transform: translateX(-50%) rotate(45deg);
}

.robe-pattern::before {
  content: '';
  position: absolute;
  width: calc(8px * var(--dh-scale));
  height: calc(8px * var(--dh-scale));
  border: calc(1px * var(--dh-scale)) solid rgba(255, 215, 0, 0.3);
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.robe-pattern::after {
  content: '';
  position: absolute;
  width: calc(3px * var(--dh-scale));
  height: calc(3px * var(--dh-scale));
  background: rgba(255, 215, 0, 0.35);
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* 腰带 */
.sash {
  width: calc(64px * var(--dh-scale));
  height: calc(5px * var(--dh-scale));
  background: linear-gradient(180deg, var(--dh-gold-light), var(--dh-gold), var(--dh-gold-deep));
  border-radius: calc(2px * var(--dh-scale));
  margin-top: calc(2px * var(--dh-scale));
  box-shadow: 0 calc(1px * var(--dh-scale)) calc(3px * var(--dh-scale)) rgba(0,0,0,0.2);
}

/* ============================================
   第六层 + 第七层：动画系统与情绪系统
   ============================================ */

/* ---- 鬓发微摆 ---- */
.hair-side.left {
  animation: hairSwayLeft 5s ease-in-out infinite;
}
.hair-side.right {
  animation: hairSwayRight 5s ease-in-out infinite;
}

@keyframes hairSwayLeft {
  0%, 100% { transform: rotate(0deg); }
  30%      { transform: rotate(2deg); }
  70%      { transform: rotate(-1deg); }
}
@keyframes hairSwayRight {
  0%, 100% { transform: rotate(0deg); }
  30%      { transform: rotate(-2deg); }
  70%      { transform: rotate(1deg); }
}

/* ---- 说话时的头部微动 ---- */
.digital-human.speaking .avatar-body {
  animation: speakBob 0.4s infinite alternate ease-in-out;
}

@keyframes speakBob {
  0%   { transform: translateY(0) rotate(0deg); }
  33%  { transform: translateY(calc(-3px * var(--dh-scale))) rotate(0.5deg); }
  66%  { transform: translateY(calc(-1px * var(--dh-scale))) rotate(-0.3deg); }
  100% { transform: translateY(calc(-3px * var(--dh-scale))) rotate(0.5deg); }
}

/* ---- 说话时曼荼罗加速 + 光晕增强 ---- */
.digital-human.speaking .mandala-backdrop {
  animation-duration: calc(var(--dh-mandala-rotation) * 0.5);
}

.digital-human.speaking .mandala-halo {
  animation: auraPulse 1.5s ease-in-out infinite;
  background: radial-gradient(circle,
    rgba(249, 168, 37, 0.22) 0%,
    rgba(249, 168, 37, 0.1) 60%,
    transparent 80%
  );
}

.digital-human.speaking .mandala-center-glow {
  background: radial-gradient(circle,
    rgba(255, 224, 130, 0.3) 0%,
    rgba(249, 168, 37, 0.12) 40%,
    transparent 70%
  );
}

@keyframes auraPulse {
  0%, 100% {
    box-shadow: 0 0 calc(20px * var(--dh-scale)) calc(5px * var(--dh-scale)) rgba(249, 168, 37, 0.12);
  }
  50% {
    box-shadow: 0 0 calc(40px * var(--dh-scale)) calc(12px * var(--dh-scale)) rgba(249, 168, 37, 0.25);
  }
}

/* ---- 说话时粒子加速 ---- */
.digital-human.speaking .particle {
  animation-duration: 3.5s;
  box-shadow:
    0 0 calc(var(--size) * 3) var(--dh-gold),
    0 0 calc(var(--size) * 6) var(--dh-gold-glow);
}

/* ============================================
   情绪状态
   ============================================ */

/* ---- Neutral 显式重置 ---- */
.digital-human.neutral .eyebrow.left  { transform: rotate(-8deg) translateY(0); }
.digital-human.neutral .eyebrow.right { transform: rotate(8deg) translateY(0); }
.digital-human.neutral .mouth {
  width: calc(14px * var(--dh-scale));
  height: calc(4px * var(--dh-scale));
  border-radius: 0 0 calc(8px * var(--dh-scale)) calc(8px * var(--dh-scale));
  background: var(--dh-mouth-neutral);
}
.digital-human.neutral .iris  { transform: scale(1); }
.digital-human.neutral .blush { background: radial-gradient(ellipse, var(--dh-skin-blush), transparent); }

/* ---- Happy 开心摇摆 ---- */
.digital-human.happy .avatar-body {
  animation: happySway 0.7s infinite alternate ease-in-out;
}

@keyframes happySway {
  0%   { transform: translateX(0) rotate(0deg); }
  25%  { transform: translateX(calc(-2px * var(--dh-scale))) rotate(-2deg); }
  75%  { transform: translateX(calc(2px * var(--dh-scale))) rotate(2deg); }
  100% { transform: translateX(0) rotate(0deg); }
}

/* ---- Sad 难过低头 ---- */
.digital-human.sad .avatar-body {
  transform: translateY(calc(2px * var(--dh-scale)));
  transition: transform 0.5s ease;
}

/* ---- Surprised 惊讶 ---- */
.digital-human.surprised .avatar-body {
  animation: surprisedStartle 0.5s ease-out forwards;
}

.digital-human.surprised .mouth {
  width: calc(10px * var(--dh-scale));
  height: calc(12px * var(--dh-scale));
  border-radius: 50%;
  background: var(--dh-mouth-open);
  margin-top: calc(2px * var(--dh-scale));
}

.digital-human.surprised .iris {
  transform: scale(0.65);
  transition: transform 0.15s ease;
}

@keyframes surprisedStartle {
  0%   { transform: translateY(0) scale(1); }
  15%  { transform: translateY(calc(-6px * var(--dh-scale))) scale(1.04); }
  30%  { transform: translateY(calc(-3px * var(--dh-scale))) scale(1.02); }
  100% { transform: translateY(calc(-2px * var(--dh-scale))) scale(1.01); }
}

/* ---- Angry 生气 ---- */
.digital-human.angry .avatar-body {
  animation: angryTremble 0.6s ease-out;
}

.digital-human.angry .eyebrow.left {
  transform: rotate(10deg) translateY(calc(2px * var(--dh-scale)));
}
.digital-human.angry .eyebrow.right {
  transform: rotate(-10deg) translateY(calc(2px * var(--dh-scale)));
}
.digital-human.angry .mouth {
  width: calc(10px * var(--dh-scale));
  height: calc(3px * var(--dh-scale));
  border-radius: calc(2px * var(--dh-scale));
  background: var(--dh-mouth-open);
}
.digital-human.angry .iris {
  transform: scale(0.85);
}
.digital-human.angry .blush {
  background: radial-gradient(ellipse, rgba(255, 80, 70, 0.45), transparent);
}

@keyframes angryTremble {
  0%, 100% { transform: translateX(0); }
  10%      { transform: translateX(calc(-1.5px * var(--dh-scale))); }
  20%      { transform: translateX(calc(1.5px * var(--dh-scale))); }
  30%      { transform: translateX(calc(-1px * var(--dh-scale))); }
  40%      { transform: translateX(calc(1px * var(--dh-scale))); }
  50%      { transform: translateX(calc(-0.5px * var(--dh-scale))); }
  60%      { transform: translateX(0); }
}

/* ============================================
   第八层：状态指示器
   ============================================ */
.avatar-info {
  text-align: center;
  margin-top: calc(8px * var(--dh-scale));
}

.name-plate {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: calc(4px * var(--dh-scale));
}

.name-bracket {
  font-size: calc(11px * var(--dh-scale));
  color: rgba(255, 255, 255, 0.45);
  font-weight: 300;
  letter-spacing: 0;
}

.avatar-name {
  font-size: calc(15px * var(--dh-scale));
  font-weight: 700;
  color: var(--dh-gold-light);
  letter-spacing: calc(3px * var(--dh-scale));
  text-shadow: 0 calc(1px * var(--dh-scale)) calc(3px * var(--dh-scale)) rgba(0, 0, 0, 0.3);
}

.avatar-status {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: calc(6px * var(--dh-scale));
  margin-top: calc(4px * var(--dh-scale));
  background: rgba(0, 0, 0, 0.15);
  border-radius: calc(12px * var(--dh-scale));
  padding: calc(3px * var(--dh-scale)) calc(14px * var(--dh-scale));
}

.status-dot {
  width: calc(6px * var(--dh-scale));
  height: calc(6px * var(--dh-scale));
  border-radius: 50%;
  background: #67C23A;
  box-shadow: 0 0 calc(5px * var(--dh-scale)) rgba(103, 194, 58, 0.5);
  transition: all var(--dh-emotion-transition);
}

.status-dot.active {
  background: var(--dh-gold-light);
  box-shadow: 0 0 calc(8px * var(--dh-scale)) rgba(255, 224, 130, 0.7);
  animation: statusPulse 1.2s ease-in-out infinite;
}

.status-dot.vts {
  background: #E6A23C;
  box-shadow: 0 0 calc(6px * var(--dh-scale)) rgba(230, 162, 60, 0.5);
}

.status-label {
  font-size: calc(11px * var(--dh-scale));
  color: rgba(255, 255, 255, 0.8);
  letter-spacing: 0.5px;
}

@keyframes statusPulse {
  0%, 100% { box-shadow: 0 0 calc(5px * var(--dh-scale)) rgba(255, 224, 130, 0.5); }
  50%      { box-shadow: 0 0 calc(12px * var(--dh-scale)) rgba(255, 224, 130, 0.9); }
}

/* ---- 模式切换 ---- */
.mode-toggle {
  margin-top: calc(4px * var(--dh-scale));
}

.mode-btn {
  font-size: calc(13px * var(--dh-scale));
  cursor: pointer;
  opacity: 0.6;
  transition: all 0.3s;
  padding: calc(4px * var(--dh-scale)) calc(10px * var(--dh-scale));
  border-radius: calc(12px * var(--dh-scale));
  background: rgba(255, 255, 255, 0.15);
  border: calc(1px * var(--dh-scale)) solid rgba(255, 255, 255, 0.15);
}

.mode-btn:hover {
  opacity: 1;
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.3);
}
</style>
