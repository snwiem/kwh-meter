<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

interface Interval {
  start: string
  end: string
  energy_kwh: number
  duration_hours: number
  avg_power_kw: number | null
}

const intervals = ref<Interval[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

const CHART_W = 600
const CHART_H = 200
const PAD_TOP = 10

const totalDuration = computed(() =>
  intervals.value.reduce((sum, i) => sum + i.duration_hours, 0)
)
const maxEnergy = computed(() =>
  Math.max(...intervals.value.map((i) => i.energy_kwh), 0)
)

interface Bar {
  x: number
  w: number
  y: number
  h: number
  tooltip: string
}

function formatTs(iso: string): string {
  const d = new Date(iso)
  const dd = String(d.getDate()).padStart(2, '0')
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const yyyy = d.getFullYear()
  const hh = String(d.getHours()).padStart(2, '0')
  const min = String(d.getMinutes()).padStart(2, '0')
  return `${dd}.${mm}.${yyyy} ${hh}:${min}`
}

function formatDuration(hours: number): string {
  if (hours >= 48) return `${(hours / 24).toFixed(1)} Tage`
  return `${hours.toFixed(1)} h`
}

const bars = computed<Bar[]>(() => {
  let x = 0
  return intervals.value.map((i) => {
    const w =
      totalDuration.value > 0
        ? (i.duration_hours / totalDuration.value) * CHART_W
        : 0
    const h =
      maxEnergy.value > 0
        ? (i.energy_kwh / maxEnergy.value) * (CHART_H - PAD_TOP)
        : 0
    const avg =
      i.avg_power_kw !== null ? `Ø ${i.avg_power_kw.toFixed(2)} kW` : 'Ø –'
    const tooltip =
      `${formatTs(i.start)} → ${formatTs(i.end)}\n` +
      `${i.energy_kwh.toFixed(1)} kWh in ${formatDuration(i.duration_hours)}\n` +
      avg
    const bar: Bar = { x, w, y: CHART_H - h, h, tooltip }
    x += w
    return bar
  })
})

const rangeLabel = computed(() => {
  if (intervals.value.length === 0) return ''
  const first = intervals.value[0]
  const last = intervals.value[intervals.value.length - 1]
  return `${formatTs(first.start)} – ${formatTs(last.end)}`
})

async function load() {
  loading.value = true
  error.value = null
  try {
    const res = await fetch('/api/analytics/intervals')
    if (!res.ok) throw new Error(`Fehler ${res.status}`)
    intervals.value = await res.json()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Unbekannter Fehler'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="screen">
    <header class="header">
      <h1 class="title">Analyse</h1>
    </header>

    <main class="content">
      <div v-if="error" class="error-msg">
        {{ error }}
        <button class="retry-btn" @click="load">Erneut versuchen</button>
      </div>

      <div v-else-if="loading" class="empty">Lädt…</div>

      <div v-else-if="intervals.length === 0" class="empty">
        Noch keine Daten — mindestens zwei Ablesungen sind für die Analyse
        nötig.
      </div>

      <template v-else>
        <p class="description">
          Energieverbrauch zwischen den Ablesungen. Breite ∝ Dauer, Höhe =
          Energie (kWh). Details per Tipp auf einen Balken.
        </p>

        <div class="chart-wrap">
          <svg
            class="chart"
            :viewBox="`0 0 ${CHART_W} ${CHART_H}`"
            preserveAspectRatio="none"
            role="img"
            aria-label="Energieverbrauch pro Intervall"
          >
            <g v-for="(bar, idx) in bars" :key="idx">
              <rect
                :x="bar.x"
                :y="bar.y"
                :width="bar.w"
                :height="bar.h"
                class="bar"
              >
                <title>{{ bar.tooltip }}</title>
              </rect>
            </g>
          </svg>
          <div class="range-label">{{ rangeLabel }}</div>
        </div>
      </template>
    </main>
  </div>
</template>

<style scoped>
.screen {
  max-width: 600px;
  margin: 0 auto;
  padding: 1rem;
}

.header {
  display: flex;
  align-items: center;
  gap: 1rem;
  border-bottom: 1px solid #ccc;
  padding-bottom: 0.75rem;
  margin-bottom: 1.5rem;
}

.title {
  font-size: 1.2rem;
  margin: 0;
}

.description {
  color: #555;
  font-size: 0.85rem;
  margin-bottom: 1rem;
}

.chart-wrap {
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fff;
  padding: 0.75rem;
}

.chart {
  width: 100%;
  height: 200px;
  display: block;
}

.bar {
  fill: #3a7bd5;
}

.bar:hover {
  fill: #2b5ca8;
}

.range-label {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: #888;
  text-align: center;
}

.empty {
  text-align: center;
  color: #888;
  padding: 2rem 1rem;
}

.error-msg {
  background: #fdecea;
  color: #c0392b;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.retry-btn {
  align-self: flex-start;
  background: #fff;
  border: 1px solid #c0392b;
  color: #c0392b;
  border-radius: 4px;
  padding: 0.3rem 0.75rem;
  cursor: pointer;
  font-size: 0.85rem;
}
</style>
