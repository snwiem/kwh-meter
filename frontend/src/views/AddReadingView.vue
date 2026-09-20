<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

function localDatetimeNow(): string {
  const now = new Date()
  const pad = (n: number) => String(n).padStart(2, '0')
  return (
    `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}` +
    `T${pad(now.getHours())}:${pad(now.getMinutes())}`
  )
}

const timestamp = ref(localDatetimeNow())
const valueKwh = ref<string>('')
const comment = ref<string>('')
const submitting = ref(false)
const error = ref<string | null>(null)

function roundToOneDecimal(val: string): number {
  return Math.round(parseFloat(val) * 10) / 10
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

  submitting.value = true
  try {
    const res = await fetch('/api/readings', {
      method: 'POST',
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
    router.push('/')
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Unbekannter Fehler'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="screen">
    <header class="header">
      <button class="back-btn" @click="router.push('/')" aria-label="Zurück">← Zurück</button>
      <h1 class="title">Neue Ablesung</h1>
    </header>

    <main>
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
            />
            <span class="unit">kWh</span>
          </div>
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
          <button type="button" class="btn-cancel" @click="router.push('/')">Abbrechen</button>
          <button type="submit" class="btn-save" :disabled="submitting">
            {{ submitting ? 'Speichern…' : 'Speichern' }}
          </button>
        </div>
      </form>
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

.header {
  display: flex;
  align-items: center;
  gap: 1rem;
  border-bottom: 1px solid #ccc;
  padding-bottom: 0.75rem;
  margin-bottom: 1.5rem;
}

.back-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  color: #333;
  padding: 0;
}

.back-btn:hover {
  text-decoration: underline;
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
</style>
