<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useInfiniteScroll } from '@vueuse/core'

const router = useRouter()

interface Reading {
  id: number
  timestamp: string
  value_kwh: number
  comment: string | null
}

interface ReadingsPage {
  items: Reading[]
  page: number
  page_size: number
  total: number
}

const readings = ref<Reading[]>([])
const page = ref(1)
const total = ref(0)
const pageSize = 10
const loading = ref(true)
const loadingMore = ref(false)
const error = ref<string | null>(null)
const loadMoreError = ref<string | null>(null)

const hasMore = computed(() => readings.value.length < total.value)

function formatTimestamp(iso: string): string {
  const d = new Date(iso)
  const dd = String(d.getDate()).padStart(2, '0')
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const yyyy = d.getFullYear()
  const hh = String(d.getHours()).padStart(2, '0')
  const min = String(d.getMinutes()).padStart(2, '0')
  return `${dd}.${mm}.${yyyy} ${hh}:${min}`
}

async function fetchPage(p: number): Promise<ReadingsPage> {
  const res = await fetch(`/api/readings?page=${p}&page_size=${pageSize}`)
  if (!res.ok) throw new Error(`Readings API error: ${res.status}`)
  return await res.json()
}

async function loadInitial() {
  loading.value = true
  error.value = null
  try {
    const data = await fetchPage(1)
    readings.value = data.items
    total.value = data.total
    page.value = 1
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Unbekannter Fehler'
  } finally {
    loading.value = false
  }
}

async function loadMore() {
  if (loadingMore.value || !hasMore.value) return
  loadingMore.value = true
  loadMoreError.value = null
  try {
    const next = page.value + 1
    const data = await fetchPage(next)
    readings.value = [...readings.value, ...data.items]
    total.value = data.total
    page.value = next
  } catch (e) {
    loadMoreError.value = e instanceof Error ? e.message : 'Unbekannter Fehler'
  } finally {
    loadingMore.value = false
  }
}

// Scroll-driven loading: invoke loadMore when the user scrolls near the bottom.
useInfiniteScroll(
  window,
  () => loadMore(),
  {
    distance: 200,
    canLoadMore: () => hasMore.value && !loadMoreError.value,
  }
)

// Fill the viewport: when there is no scrollbar there are no scroll events, so
// after each data change load another batch while the content still fits the
// screen (plus a small lookahead).
function fitsViewport(): boolean {
  const doc = document.documentElement
  return doc.scrollHeight - window.scrollY <= window.innerHeight + 200
}

watch(readings, () => {
  nextTick(() => {
    if (fitsViewport()) {
      loadMore()
    }
  })
})

onMounted(loadInitial)
</script>

<template>
  <div class="screen">
    <main>
      <div v-if="error" class="error-msg">
        {{ error }}
        <button class="retry-btn" @click="loadInitial">Erneut versuchen</button>
      </div>

      <div v-else-if="loading" class="empty">Lädt…</div>

      <template v-else>
        <div v-if="readings.length === 0" class="empty">Keine Ablesungen vorhanden.</div>

        <div v-else class="list-wrapper">
          <table class="readings-table">
            <thead>
              <tr>
                <th>Datum/Uhrzeit</th>
                <th>Wert</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in readings" :key="r.id" @click="router.push(`/readings/${r.id}`)" class="clickable-row">
                <td>{{ formatTimestamp(r.timestamp) }}</td>
                <td class="value">{{ r.value_kwh.toFixed(1) }} kWh</td>
                <td class="comment-cell">
                  <span v-if="r.comment" class="comment-icon" :title="r.comment">💬</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="loadingMore" class="load-more-status">Lädt…</div>

        <div v-if="loadMoreError" class="load-more-error">
          {{ loadMoreError }}
          <button class="retry-btn" @click="loadMore">Erneut versuchen</button>
        </div>
      </template>
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

.list-wrapper {
  overflow-x: auto;
}

.readings-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}

.readings-table th {
  text-align: left;
  border-bottom: 2px solid #ccc;
  padding: 0.4rem 0.5rem;
  color: #555;
  font-weight: 600;
}

.readings-table td {
  padding: 0.5rem 0.5rem;
  border-bottom: 1px solid #eee;
}

.value {
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.comment-cell {
  text-align: center;
  width: 2rem;
}

.comment-icon {
  cursor: default;
  font-size: 1rem;
}

.clickable-row {
  cursor: pointer;
  transition: background 0.1s;
}

.clickable-row:hover {
  background: #f5f5f5;
}

.load-more-status {
  text-align: center;
  color: #888;
  padding: 0.75rem 0;
}

.load-more-error {
  text-align: center;
  color: #c0392b;
  padding: 0.75rem 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: center;
}

.retry-btn {
  padding: 0.3rem 0.75rem;
  cursor: pointer;
  border: 1px solid #ccc;
  border-radius: 4px;
  background: #fff;
  font-size: 0.9rem;
}

.retry-btn:hover {
  background: #f0f0f0;
}
</style>