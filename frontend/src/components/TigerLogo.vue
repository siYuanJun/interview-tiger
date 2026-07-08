<template>
  <svg 
    :width="size" 
    :height="size" 
    viewBox="0 0 200 200" 
    class="animate-float-slow"
    :class="{ 'animate-pulse-glow': glow }"
  >
    <defs>
      <linearGradient id="tigerGradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:#fbbf24"/>
        <stop offset="50%" style="stop-color:#f59e0b"/>
        <stop offset="100%" style="stop-color:#d97706"/>
      </linearGradient>
      <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
        <feGaussianBlur stdDeviation="6" result="coloredBlur"/>
        <feMerge>
          <feMergeNode in="coloredBlur"/>
          <feMergeNode in="SourceGraphic"/>
        </feMerge>
      </filter>
    </defs>
    
    <circle 
      cx="100" 
      cy="100" 
      :r="radius" 
      fill="rgba(30,27,75,0.9)" 
      stroke="url(#tigerGradient)" 
      stroke-width="3" 
      filter="url(#glow)"
    />
    
    <g>
      <ellipse cx="80" cy="88" rx="12" ry="14" fill="url(#tigerGradient)" opacity="0.9"/>
      <ellipse cx="120" cy="88" rx="12" ry="14" fill="url(#tigerGradient)" opacity="0.9"/>
      
      <ellipse cx="80" cy="88" rx="6" ry="8" fill="#fff" opacity="0.8"/>
      <ellipse cx="120" cy="88" rx="6" ry="8" fill="#fff" opacity="0.8"/>
      <circle cx="82" cy="88" r="3" fill="#0f0f23"/>
      <circle cx="122" cy="88" r="3" fill="#0f0f23"/>
      
      <path d="M 86 110 L 100 126 L 114 110" stroke="#fbbf24" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
      
      <circle cx="72" cy="106" r="3" fill="#fbbf24" opacity="0.7"/>
      <circle cx="68" cy="114" r="2" fill="#fbbf24" opacity="0.5"/>
      <circle cx="128" cy="106" r="3" fill="#fbbf24" opacity="0.7"/>
      <circle cx="132" cy="114" r="2" fill="#fbbf24" opacity="0.5"/>
      
      <ellipse cx="100" cy="132" rx="8" ry="6" fill="#fbbf24" opacity="0.6"/>
    </g>
    
    <g transform="translate(100, 40)">
      <path d="M 0 0 Q 15 -25 30 0 Q 15 25 0 0" stroke="#3b82f6" stroke-width="2" fill="none" opacity="0.6">
        <animate attributeName="d" values="M 0 0 Q 15 -25 30 0 Q 15 25 0 0;M 0 0 Q 15 -40 30 0 Q 15 40 0 0;M 0 0 Q 15 -25 30 0 Q 15 25 0 0" dur="2s" repeatCount="indefinite"/>
      </path>
      <path d="M 0 0 Q 25 -20 50 0 Q 25 20 0 0" stroke="#8b5cf6" stroke-width="2" fill="none" opacity="0.4">
        <animate attributeName="d" values="M 0 0 Q 25 -20 50 0 Q 25 20 0 0;M 0 0 Q 25 -35 50 0 Q 25 35 0 0;M 0 0 Q 25 -20 50 0 Q 25 20 0 0" dur="2.5s" repeatCount="indefinite"/>
      </path>
      <path d="M 0 0 Q 35 -15 70 0 Q 35 15 0 0" stroke="#d946ef" stroke-width="2" fill="none" opacity="0.3">
        <animate attributeName="d" values="M 0 0 Q 35 -15 70 0 Q 35 15 0 0;M 0 0 Q 35 -30 70 0 Q 35 30 0 0;M 0 0 Q 35 -15 70 0 Q 35 15 0 0" dur="3s" repeatCount="indefinite"/>
      </path>
    </g>
    
    <g transform="translate(100, 160)">
      <path d="M 0 0 Q -15 -25 -30 0 Q -15 25 0 0" stroke="#3b82f6" stroke-width="2" fill="none" opacity="0.6">
        <animate attributeName="d" values="M 0 0 Q -15 -25 -30 0 Q -15 25 0 0;M 0 0 Q -15 -40 -30 0 Q -15 40 0 0;M 0 0 Q -15 -25 -30 0 Q -15 25 0 0" dur="2s" repeatCount="indefinite"/>
      </path>
      <path d="M 0 0 Q -25 -20 -50 0 Q -25 20 0 0" stroke="#8b5cf6" stroke-width="2" fill="none" opacity="0.4">
        <animate attributeName="d" values="M 0 0 Q -25 -20 -50 0 Q -25 20 0 0;M 0 0 Q -25 -35 -50 0 Q -25 35 0 0;M 0 0 Q -25 -20 -50 0 Q -25 20 0 0" dur="2.5s" repeatCount="indefinite"/>
      </path>
      <path d="M 0 0 Q -35 -15 -70 0 Q -35 15 0 0" stroke="#d946ef" stroke-width="2" fill="none" opacity="0.3">
        <animate attributeName="d" values="M 0 0 Q -35 -15 -70 0 Q -35 15 0 0;M 0 0 Q -35 -30 -70 0 Q -35 30 0 0;M 0 0 Q -35 -15 -70 0 Q -35 15 0 0" dur="3s" repeatCount="indefinite"/>
      </path>
    </g>
  </svg>
</template>

<script setup lang="ts">
defineProps<{
  size?: number
  glow?: boolean
  radius?: number
}>()
</script>

<script lang="ts">
export default {
  name: 'TigerLogo',
  props: {
    size: {
      type: Number,
      default: 160
    },
    glow: {
      type: Boolean,
      default: true
    },
    radius: {
      type: Number,
      default: 85
    }
  }
}
</script>
