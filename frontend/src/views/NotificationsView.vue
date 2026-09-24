<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

interface NotificationTime {
  id: number
  time: string
}

interface ConnectionInfo {
  public_url: string
  topic: string
}

const times = ref<NotificationTime[]>([])
const newTime = ref('')
const adding = ref(false)
const error = ref<string | null>(null)
const connectionInfo = ref<ConnectionInfo | null>(null)

// ntfy://<host[:port]>/<topic> — strips the scheme from the public URL
const deepLink = computed(() => {
  if (!connectionInfo.value) return null
  const host = connectionInfo.value.public_url.replace(/^[a-zA-Z][a-zA-Z0-9+.-]*:\/\//, '').replace(/\/+$/, '')
  if (!host) return null
  return `ntfy://${host}/${connectionInfo.value.topic}`
})

async function fetchTimes() {
  try {
    const res = await fetch('/api/notification-times')
    if (res.ok) times.value = await res.json()
  } catch {
    // non-critical — list stays empty
  }
}

async function fetchConnectionInfo() {
  try {
    const res = await fetch('/api/notifications/connection-info')
    if (res.ok) connectionInfo.value = await res.json()
  } catch {
    // non-critical — info section degrades gracefully
  }
}

onMounted(() => {
  fetchTimes()
  fetchConnectionInfo()
})

async function addTime() {
  error.value = null
  const value = newTime.value
  if (!/^\d{2}:\d{2}$/.test(value)) {
    error.value = 'Bitte eine gültige Uhrzeit (HH:MM) wählen.'
    return
  }

  adding.value = true
  try {
    const res = await fetch('/api/notification-times', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ time: value }),
    })
    if (res.status === 409) {
      error.value = `Die Zeit ${value} ist bereits geplant.`
      return
    }
    if (!res.ok) {
      const body = await res.json().catch(() => null)
      throw new Error(body?.detail ?? `Fehler ${res.status}`)
    }
    newTime.value = ''
    await fetchTimes()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Unbekannter Fehler'
  } finally {
    adding.value = false
  }
}

async function removeTime(id: number) {
  error.value = null
  try {
    const res = await fetch(`/api/notification-times/${id}`, { method: 'DELETE' })
    if (!res.ok && res.status !== 404) {
      throw new Error(`Fehler ${res.status}`)
    }
    await fetchTimes()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Unbekannter Fehler'
  }
}
</script>

<template>
  <div class="screen">
    <header class="header">
      <button class="back-btn" @click="router.push('/')" aria-label="Zurück">← Zurück</button>
      <h1 class="title">Benachrichtigungen</h1>
    </header>

    <main class="content">
      <section class="section">
        <h2 class="section-title">Benachrichtigungszeiten</h2>
        <p class="description">
          Zu diesen Zeiten wirst du täglich an eine neue Zählerablesung erinnert.
        </p>

        <ul v-if="times.length" class="time-list">
          <li v-for="t in times" :key="t.id" class="time-item">
            <span class="time-value">⏰ {{ t.time }}</span>
            <button
              class="remove-btn"
              aria-label="Zeit entfernen"
              @click="removeTime(t.id)"
            >✕</button>
          </li>
        </ul>
        <p v-else class="empty-hint">Keine Benachrichtigungen geplant.</p>

        <form class="add-form" @submit.prevent="addTime">
          <input
            id="new-time"
            v-model="newTime"
            type="time"
            aria-label="Neue Benachrichtigungszeit"
          />
          <button type="submit" class="btn-add" :disabled="adding || !newTime">
            {{ adding ? 'Hinzufügen…' : 'Hinzufügen' }}
          </button>
        </form>

        <div v-if="error" class="error-msg">{{ error }}</div>
      </section>

      <section class="section">
        <h2 class="section-title">Mit der ntfy-App verbinden</h2>
        <template v-if="connectionInfo">
          <p class="description">
            Abonniere das Topic in der ntfy-App auf deinem Telefon, um die
            Erinnerungen zu erhalten:
          </p>
          <dl class="connection-info">
            <dt>Server</dt>
            <dd><code>{{ connectionInfo.public_url }}</code></dd>
            <dt>Topic</dt>
            <dd><code>{{ connectionInfo.topic }}</code></dd>
          </dl>
          <ol class="steps">
            <li>ntfy-App öffnen → <strong>Abo hinzufügen</strong> (+)</li>
            <li>Topic eingeben: <code>{{ connectionInfo.topic }}</code></li>
            <li>„Anderer Server" wählen: <code>{{ connectionInfo.public_url }}</code></li>
            <li>Abonnieren — fertig.</li>
          </ol>
          <a v-if="deepLink" class="deep-link" :href="deepLink">
            📲 Direkt in der ntfy-App abonnieren
          </a>
        </template>
        <p v-else class="empty-hint">Verbindungsinformationen nicht verfügbar.</p>
      </section>
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

.section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.05rem;
  margin: 0 0 0.5rem;
}

.description {
  color: #555;
  margin-bottom: 1rem;
}

.time-list {
  list-style: none;
  margin: 0 0 1rem;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.time-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.6rem 0.9rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  background: #fff;
}

.time-value {
  font-size: 1rem;
  font-weight: 600;
}

.remove-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  color: #888;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.remove-btn:hover {
  color: #c0392b;
  background: #f5f5f5;
}

.empty-hint {
  color: #888;
  font-style: italic;
  margin-bottom: 1rem;
}

.add-form {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.add-form input[type='time'] {
  flex: 1;
  padding: 0.5rem 0.6rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
  font-family: inherit;
}

.btn-add {
  padding: 0.5rem 1.25rem;
  border: none;
  border-radius: 4px;
  background: #2c7be5;
  color: #fff;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  white-space: nowrap;
}

.btn-add:disabled {
  opacity: 0.6;
  cursor: default;
}

.btn-add:hover:not(:disabled) {
  background: #1a63c5;
}

.error-msg {
  color: #c0392b;
  font-size: 0.9rem;
  margin-top: 0.6rem;
}

.connection-info {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 0.3rem 0.9rem;
  margin: 0 0 1rem;
}

.connection-info dt {
  font-weight: 600;
  font-size: 0.9rem;
}

.connection-info dd {
  margin: 0;
}

code {
  background: #f5f5f5;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  font-size: 0.9rem;
}

.steps {
  color: #555;
  font-size: 0.9rem;
  padding-left: 1.2rem;
  margin: 0 0 1rem;
}

.steps li {
  margin-bottom: 0.3rem;
}

.deep-link {
  display: inline-block;
  padding: 0.5rem 1rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  background: #fff;
  color: #2c7be5;
  text-decoration: none;
  font-weight: 600;
}

.deep-link:hover {
  background: #f5f5f5;
}
</style>
