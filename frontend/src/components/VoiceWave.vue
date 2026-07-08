<script setup lang="ts">
defineProps<{
  size?: number
  status?: 'idle' | 'starting' | 'listening' | 'recognizing' | 'error'
}>()
</script>

<template>
  <svg
    :width="size || 64"
    :height="size || 64"
    viewBox="0 0 80 80"
    class="mic-root"
    :class="{
      'mic--idle': status === 'idle',
      'mic--starting': status === 'starting',
      'mic--listening': status === 'listening',
      'mic--recognizing': status === 'recognizing',
      'mic--error': status === 'error',
    }"
  >
    <defs>
      <radialGradient id="micGlowGrad" cx="50%" cy="40%" r="50%">
        <stop offset="0%" stop-color="#A78BFA" stop-opacity="0.35" />
        <stop offset="100%" stop-color="#7C3AED" stop-opacity="0" />
      </radialGradient>
      <radialGradient id="micGlowErr" cx="50%" cy="40%" r="50%">
        <stop offset="0%" stop-color="#F87171" stop-opacity="0.35" />
        <stop offset="100%" stop-color="#EF4444" stop-opacity="0" />
      </radialGradient>
    </defs>

    <!-- 呼吸光晕 -->
    <circle cx="38" cy="30" r="32" fill="url(#micGlowGrad)" class="mic-glow" />
    <circle cx="38" cy="30" r="32" fill="url(#micGlowErr)" class="mic-glow-err" />

    <!-- 麦克风外网罩 -->
    <ellipse cx="38" cy="28" rx="18" ry="20" fill="none" stroke="#7C3AED" stroke-width="5" class="mic-grille" />
    <ellipse cx="38" cy="28" rx="14" ry="16" fill="none" stroke="#A78BFA" stroke-width="1.5" opacity="0.5" class="mic-grille-inner" />
    <!-- 网罩横线 -->
    <line x1="22" y1="20" x2="54" y2="20" stroke="#A78BFA" stroke-width="0.8" opacity="0.3" />
    <line x1="22" y1="28" x2="54" y2="28" stroke="#A78BFA" stroke-width="0.8" opacity="0.3" />
    <line x1="22" y1="36" x2="54" y2="36" stroke="#A78BFA" stroke-width="0.8" opacity="0.3" />

    <!-- 麦克风手柄 -->
    <path
      d="M33 46 L33 62 Q33 68 38 68 Q43 68 43 62 L43 46"
      fill="#7C3AED"
      class="mic-handle"
    />

    <!-- 底部底座弧线 -->
    <path
      d="M26 66 Q38 74 50 66"
      fill="none"
      stroke="#7C3AED"
      stroke-width="3"
      stroke-linecap="round"
      class="mic-base"
    />
  </svg>
</template>

<style scoped>
.mic-root {
  transition: transform 0.3s ease;
}

/* idle: 全部灰暗 */
.mic--idle .mic-grille { stroke: #6B7280; }
.mic--idle .mic-grille-inner { stroke: #9CA3AF; }
.mic--idle .mic-handle { fill: #6B7280; }
.mic--idle .mic-base { stroke: #6B7280; }
.mic--idle .mic-glow { opacity: 0; }
.mic--idle .mic-glow-err { opacity: 0; }
.mic--idle line { stroke: #9CA3AF; }

/* starting / listening: 紫色 + 呼吸 */
.mic--starting .mic-grille,
.mic--listening .mic-grille { stroke: #7C3AED; }
.mic--starting .mic-handle,
.mic--listening .mic-handle { fill: #7C3AED; }
.mic--starting .mic-base,
.mic--listening .mic-base { stroke: #7C3AED; }
.mic--starting .mic-glow,
.mic--listening .mic-glow {
  animation: micBreathe 2.6s ease-in-out infinite;
}
.mic--starting .mic-glow-err,
.mic--listening .mic-glow-err { opacity: 0; }
.mic--starting line,
.mic--listening line { stroke: #A78BFA; }

/* recognizing: 半透明 + 呼吸 */
.mic--recognizing .mic-grille { stroke: #7C3AED; opacity: 0.7; }
.mic--recognizing .mic-handle { fill: #7C3AED; opacity: 0.7; }
.mic--recognizing .mic-base { stroke: #7C3AED; opacity: 0.7; }
.mic--recognizing .mic-glow {
  animation: micBreathe 1.4s ease-in-out infinite;
}
.mic--recognizing .mic-glow-err { opacity: 0; }
.mic--recognizing line { stroke: #A78BFA; opacity: 0.5; }

/* error: 红色 + 呼吸 */
.mic--error .mic-grille { stroke: #EF4444; }
.mic--error .mic-handle { fill: #EF4444; }
.mic--error .mic-base { stroke: #EF4444; }
.mic--error .mic-glow { opacity: 0; }
.mic--error .mic-glow-err {
  animation: micBreathe 2.6s ease-in-out infinite;
}
.mic--error line { stroke: #F87171; }

@keyframes micBreathe {
  0%, 100% { opacity: 0.15; transform: scale(1); }
  50% { opacity: 0.45; transform: scale(1.06); }
}
</style>
