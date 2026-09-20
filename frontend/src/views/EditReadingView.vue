<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const readingId = computed(() => parseInt(route.params.id as string))

interface ReadingNeighbour {
  value_kwh: number
  timestamp: string
}

interface Neighbours {
  previous: ReadingNeighbour | null
  next: ReadingNeighbour | null
}

function toLocalDatetimeInput(iso: string): string {
  const d = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, '0')
  return (
    `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}` +
    `T${pad(d.getHours())}:${pad(d.getMinutes())}`
  )
}

function formatTs(iso: string): string {
  const d = new Date(iso)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${pad(d.getDate())}.${pad(d.getMonth() + 1)}.${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

const timestamp = ref('')
const valueKwh = ref<string>('')
const comment = ref<string>('')
const submitting = ref(false)
const loading = ref(true)
const error = ref<string | null>(null)
const neighbours = ref<Neighbours | null>(null)

function roundToOneDecimal(val: string): number {
  return Math.round(parseFloat(val) * 10) / 10
}

function valueRangeError(): string | null {
  if (!valueKwh.value || !neighbours.value) return null
  const val = roundToOneDecimal(valueKwh.value)
  if (isNaN(val)) return null
  const { previous, next } = neighbours.value
  if (previous !== null && val < previous.value_kwh) {
    return `Wert muss mindestens ${previous.value_kwh.toFixed(1)} kWh betragen (vorherige Ablesung vom ${formatTs(previous.timestamp)}).`
  }
  if (next !== null && val > next.value_kwh) {
    return `Wert darf höchstens ${next.value_kwh.toFixed(1)} kWh betragen (nächste Ablesung vom ${formatTs(next.timestamp)}).`
  }
  return null
}

async function fetchNeighbours() {
  if (!timestamp.value) return
  try {
    const iso = new Date(timestamp.value).toISOString()
    const res = await fetch(
      `/api/readings/neighbours?timestamp=${encodeURIComponent(iso)}&exclude_id=${readingId.value}`
    )
    if (res.ok) neighbours.value = await res.json()
  } catch {
    // non-critical — backend will still validate on submit
  }
}

async function load() {
  loading.value = true
  error.value = null
  try {
    const res = await fetch(`/api/readings/${readingId.value}`)
    if (res.status === 404) {
      router.replace(`/readings/${readingId.value}`)
      return
    }
    if (!res.ok) throw new Error(`Readings API error: ${res.status}`)
    const data = await res.json()
    timestamp.value = toLocalDatetimeInput(data.timestamp)
    valueKwh.value = String(data.value_kwh)
    comment.value = data.comment ?? ''
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Unbekannter Fehler'
  } finally {
    loading.value = false
  }
}

async function submit() {
  error.value = null

  const numVal = parseFloat(valueKwh.value)
  if (!valueKwh.value || isNaN(numVal) || numVal <= 0) {
    error.value = 'Bitte einen gültigen positiven kWh-Wert eingeben.'
    return
  }
  if (!timestamp.value) {
    error.value = 'Bitte Datum und Uhrzeit angeben.'
    return
  }

  const rangeErr = valueRangeError()
  if (rangeErr) {
    error.value = rangeErr
    return
  }

  submitting.value = true
  try {
    const res = await fetch(`/api/readings/${readingId.value}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        timestamp: new Date(timestamp.value).toISOString(),
        value_kwh: roundToOneDecimal(valueKwh.value),
        comment: comment.value.trim() || null,
      }),
    })
    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      throw new Error(body?.detail ?? `Fehler ${res.status}`)
    }
    router.push(`/readings/${readingId.value}`)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Unbekannter Fehler'
  } finally {
    submitting.value = false
  }
}

function cancel() {
  router.push(`/readings/${readingId.value}`)
}

// Re-fetch neighbours whenever timestamp changes
watch(timestamp, fetchNeighbours)

onMounted(load)
</script>

<template>
  <div class="screen">
    <main>
      <div v-if="loading" class="empty">Lädt…</div>

      <div v-else>
        <header class="header">
          <h1 class="title">Ablesung bearbeiten</h1>
        </header>

        <form class="form" @submit.prevent="submit">
          <div class="field">
            <label for="timestamp">Datum &amp; Uhrzeit</label>
            <input
              id="timestamp"
              v-model="timestamp"
              type="datetime-local"
              required
            />
          </div>

          <div class="field">
            <label for="value">Zählerstand</label>
            <div class="input-with-unit">
              <input
                id="value"
                v-model="valueKwh"
                type="number"
                step="0.1"
                min="0.1"
                placeholder="0.0"
                required
                :class="{ 'input-error': valueRangeError() !== null }"
              />
              <span class="unit">kWh</span>
            </div>
            <!-- Inline range hint from neighbours -->
            <div v-if="neighbours" class="range-hint">
              <span v-if="neighbours.previous">
                ≥ {{ neighbours.previous.value_kwh.toFixed(1) }} kWh
                <span class="hint-meta">({{ formatTs(neighbours.previous.timestamp) }})</span>
              </span>
              <span v-if="neighbours.previous && neighbours.next" class="hint-sep"> · </span>
              <span v-if="neighbours.next">
                ≤ {{ neighbours.next.value_kwh.toFixed(1) }} kWh
                <span class="hint-meta">({{ formatTs(neighbours.next.timestamp) }})</span>
              </span>
            </div>
            <div v-if="valueRangeError()" class="field-error">{{ valueRangeError() }}</div>
          </div>

          <div class="field">
            <label for="comment">Kommentar <span class="optional">(optional)</span></label>
            <textarea
              id="comment"
              v-model="comment"
              maxlength="255"
              rows="3"
              placeholder="z.B. Auto lädt gerade"
            />
          </div>

          <div v-if="error" class="error-msg">{{ error }}</div>

          <div class="actions">
            <button type="button" class="btn-cancel" @click="cancel">Abbrechen</button>
            <button type="submit" class="btn-save" :disabled="submitting">
              {{ submitting ? 'Speichern…' : 'Speichern' }}
            </button>
          </div>
        </form>
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

.header {
  display: flex;
  align-items: center;
  border-bottom: 1px solid #ccc;
  padding-bottom: 0.75rem;
  margin-bottom: 1.5rem;
}

.title {
  font-size: 1.2rem;
  margin: 0;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

label {
  font-weight: 600;
  font-size: 0.95rem;
}

.optional {
  font-weight: normal;
  color: #888;
  font-size: 0.85rem;
}

input[type='datetime-local'],
input[type='number'],
textarea {
  padding: 0.5rem 0.6rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
  width: 100%;
  box-sizing: border-box;
}

.input-with-unit {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.input-with-unit input {
  flex: 1;
}

.unit {
  font-size: 1rem;
  color: #555;
  white-space: nowrap;
}

textarea {
  resize: vertical;
}

.error-msg {
  color: #c0392b;
  font-size: 0.9rem;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.btn-cancel {
  padding: 0.5rem 1.25rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  background: #fff;
  cursor: pointer;
  font-size: 1rem;
}

.btn-save {
  padding: 0.5rem 1.25rem;
  border: none;
  border-radius: 4px;
  background: #2c7be5;
  color: #fff;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: default;
}

.btn-save:hover:not(:disabled) {
  background: #1a63c5;
}

.input-error {
  border-color: #c0392b !important;
}

.range-hint {
  font-size: 0.82rem;
  color: #666;
  margin-top: 0.25rem;
}

.hint-meta {
  color: #999;
}

.hint-sep {
  color: #bbb;
}

.field-error {
  font-size: 0.85rem;
  color: #c0392b;
  margin-top: 0.2rem;
}
</style>