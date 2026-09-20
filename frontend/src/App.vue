<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Meter {
  zaehler_nr: string
  street: string
  house_number: string
  postal_code: string
  city: string
}

const meter = ref<Meter | null>(null)
const error = ref<string | null>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const response = await fetch('/api/meter')
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`)
    }
    meter.value = await response.json()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unknown error'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="app">
    <header class="app-header">
      <div v-if="loading" class="zaehler-nr">Lädt…</div>
      <div v-else-if="error" class="zaehler-nr error">Fehler: {{ error }}</div>
      <!-- Prominently display the Zählernummer as required by Feature 0001 -->
      <div v-else-if="meter" class="zaehler-nr">
        Zählernummer: <strong>{{ meter.zaehler_nr }}</strong>
      </div>

      <!-- "+" button placeholder — full functionality implemented in issue #3 -->
      <button class="add-btn" aria-label="Neue Ablesung hinzufügen">+</button>
    </header>

    <main>
      <!-- Readings list placeholder — implemented in issue #3 -->
      <p class="placeholder">Ablesungen werden in Issue #3 implementiert.</p>
    </main>
  </div>
</template>

<style scoped>
.app {
  font-family: sans-serif;
  max-width: 600px;
  margin: 0 auto;
  padding: 1rem;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #ccc;
  padding-bottom: 0.75rem;
  margin-bottom: 1rem;
}

.zaehler-nr {
  font-size: 1.1rem;
}

.zaehler-nr.error {
  color: #c0392b;
}

.add-btn {
  font-size: 1.5rem;
  line-height: 1;
  padding: 0.25rem 0.75rem;
  cursor: pointer;
  border: 1px solid #333;
  border-radius: 4px;
  background: #fff;
}

.placeholder {
  color: #888;
  font-style: italic;
}
</style>
