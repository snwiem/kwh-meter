<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

interface Reading {
  id: number
  timestamp: string
  value_kwh: number
  comment: string | null
}

const reading = ref<Reading | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

function formatTimestamp(iso: string): string {
  const d = new Date(iso)
  const dd = String(d.getDate()).padStart(2, '0')
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const yyyy = d.getFullYear()
  const hh = String(d.getHours()).padStart(2, '0')
  const min = String(d.getMinutes()).padStart(2, '0')
  return `${dd}.${mm}.${yyyy} ${hh}:${min}`
}

async function fetchReading() {
  loading.value = true
  error.value = null
  try {
    const id = parseInt(route.params.id as string)
    if (isNaN(id)) throw new Error('Invalid reading ID')
    const res = await fetch(`/api/readings/${id}`)
    if (!res.ok) {
      if (res.status === 404) {
        router.replace('/')
        return
      }
      throw new Error(`Readings API error: ${res.status}`)
    }
    reading.value = await res.json()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Unbekannter Fehler'
  } finally {
    loading.value = false
  }
}

onMounted(fetchReading)
watch(() => route.params.id, fetchReading)
</script>

<template>
  <div class="screen">
    <main>
      <div v-if="error" class="error-msg">{{ error }}</div>
      <div v-else-if="loading" class="empty">Lädt…</div>
      <div v-else-if="reading" class="detail-wrapper">
        <div class="grid">
          <div class="grid-label">Datum/Uhrzeit</div>
          <div class="grid-value">{{ formatTimestamp(reading.timestamp) }}</div>

          <div class="grid-label">Zählerstand</div>
          <div class="grid-value">{{ reading.value_kwh.toFixed(1) }} kWh</div>
        </div>

        <div v-if="reading.comment" class="comment-section">
          <h3 class="comment-headline">Kommentar:</h3>
          <p class="comment-text">{{ reading.comment }}</p>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.screen {
  font-family: sans-serif;
  max-width: 600px;
  margin: 0 auto;
  padding: 1rem;
}

.empty {
  color: #888;
  font-style: italic;
  padding: 1rem 0;
}

.error-msg {
  color: #c0392b;
  padding: 0.5rem 0;
}

.detail-wrapper {
  padding: 1rem 0;
}

.grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 1rem;
  margin-bottom: 2rem;
}

.grid-label {
  font-weight: bold;
  color: #555;
  align-self: center;
}

.grid-value {
  font-size: 1.1rem;
  align-self: center;
}

.comment-section {
  margin-top: 2rem;
  border-top: 1px solid #eee;
  padding-top: 1.5rem;
}

.comment-headline {
  font-size: 1rem;
  font-weight: bold;
  color: #555;
  margin-bottom: 0.5rem;
}

.comment-text {
  white-space: pre-wrap;
  line-height: 1.4;
}
</style>