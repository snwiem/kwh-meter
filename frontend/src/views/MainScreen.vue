<script setup lang="ts">
import { ref, onMounted } from 'vue'

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

const totalPages = () => Math.max(1, Math.ceil(total.value / pageSize))

async function fetchReadings() {
  const res = await fetch(`/api/readings?page=${page.value}&page_size=${pageSize}`)
  if (!res.ok) throw new Error(`Readings API error: ${res.status}`)
  const data: ReadingsPage = await res.json()
  readings.value = data.items
  total.value = data.total
}

async function load() {
  loading.value = true
  error.value = null
  try {
    await fetchReadings()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Unbekannter Fehler'
  } finally {
    loading.value = false
  }
}

async function goToPage(p: number) {
  page.value = p
  await fetchReadings()
}

onMounted(load)
</script>

<template>
  <div class="screen">
    <main>
      <div v-if="error" class="error-msg">{{ error }}</div>

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
              <tr v-for="r in readings" :key="r.id">
                <td>{{ formatTimestamp(r.timestamp) }}</td>
                <td class="value">{{ r.value_kwh.toFixed(1) }} kWh</td>
                <td class="comment-cell">
                  <span v-if="r.comment" class="comment-icon" :title="r.comment">💬</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="totalPages() > 1" class="pagination">
          <button :disabled="page <= 1" @click="goToPage(page - 1)">&lt; Zurück</button>
          <span>Seite {{ page }} / {{ totalPages() }}</span>
          <button :disabled="page >= totalPages()" @click="goToPage(page + 1)">Weiter &gt;</button>
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

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
  gap: 0.5rem;
}

.pagination button {
  padding: 0.3rem 0.75rem;
  cursor: pointer;
  border: 1px solid #ccc;
  border-radius: 4px;
  background: #fff;
}

.pagination button:disabled {
  opacity: 0.4;
  cursor: default;
}
</style>
