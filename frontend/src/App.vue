<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const menuOpen = ref(false)
const zaehlerNr = ref<string>('')
const deleteOpen = ref(false)
const deleteError = ref<string | null>(null)
const deleting = ref(false)

const isDetailPage = computed(() => {
  return /\/readings\/\d+(\/edit)?$/.test(route.path)
})

const isEditPage = computed(() => {
  return /\/readings\/\d+\/edit$/.test(route.path)
})

onMounted(async () => {
  try {
    const res = await fetch('/api/meter')
    if (res.ok) {
      const data = await res.json()
      zaehlerNr.value = data.zaehler_nr
    }
  } catch {
    // non-critical — top bar degrades gracefully
  }
})

function navigate(to: string) {
  menuOpen.value = false
  router.push(to)
}

function goBack() {
  if (isEditPage.value) {
    router.push(`/readings/${route.params.id}`)
  } else {
    router.push('/')
  }
}

function editReading() {
  const id = route.params.id
  if (id) router.push(`/readings/${id}/edit`)
}

function openDelete() {
  deleteOpen.value = true
}

function cancelDelete() {
  deleteOpen.value = false
}

async function confirmDelete() {
  deleting.value = true
  deleteError.value = null
  const id = route.params.id
  try {
    const res = await fetch(`/api/readings/${id}`, { method: 'DELETE' })
    if (res.ok) {
      deleteOpen.value = false
      router.push('/')
      return
    }
    let message = `Fehler ${res.status}`
    const body = await res.json().catch(() => null)
    if (body && typeof body.detail === 'string') message = body.detail
    deleteOpen.value = false
    deleteError.value = message
  } catch (e) {
    deleteOpen.value = false
    deleteError.value = e instanceof Error ? e.message : 'Unbekannter Fehler'
  } finally {
    deleting.value = false
  }
}

// Reset delete state when navigating away
watch(
  () => route.path,
  () => {
    deleteOpen.value = false
    deleteError.value = null
  }
)
</script>

<template>
  <div class="app-shell">
    <!-- Global top bar -->
    <div class="top-bar">
      <button
        v-if="isDetailPage"
        class="back-btn"
        aria-label="Zurück zur Übersicht"
        @click="goBack"
      >←</button>
      <span class="zaehler-label" :title="zaehlerNr">
        {{ zaehlerNr || '…' }}
      </span>
      <div class="top-bar-actions">
        <!-- Show + only on main screen -->
        <button
          v-if="route.path === '/'"
          class="add-btn"
          aria-label="Neue Ablesung hinzufügen"
          @click="router.push('/add')"
        >+</button>
        <!-- Show edit/delete on detail page (not edit page) -->
        <template v-if="isDetailPage && !isEditPage">
          <button class="edit-btn" aria-label="Eintrag bearbeiten" @click="editReading">✏️</button>
          <button class="delete-btn" aria-label="Eintrag löschen" @click="openDelete">🗑️</button>
        </template>
        <button class="burger-btn" aria-label="Menü öffnen" @click="menuOpen = true">☰</button>
      </div>
    </div>

    <!-- Slide-in overlay menu -->
    <Transition name="fade">
      <div v-if="menuOpen" class="menu-overlay" @click.self="menuOpen = false">
        <div class="menu-panel">
          <button class="menu-close" aria-label="Menü schließen" @click="menuOpen = false">✕</button>
          <nav class="menu-nav">
            <button class="menu-item" @click="navigate('/')">🏠 Übersicht</button>
            <button class="menu-item" @click="navigate('/export')">⬇ Export</button>
          </nav>
        </div>
      </div>
    </Transition>

    <!-- Delete confirmation modal -->
    <Transition name="fade">
      <div v-if="deleteOpen" class="delete-overlay" @click.self="cancelDelete">
        <div class="delete-dialog" role="dialog" aria-modal="true" aria-label="Wirklich löschen?">
          <p class="delete-question">Wirklich löschen?</p>
          <div class="delete-actions">
            <button type="button" class="btn-no" :disabled="deleting" @click="cancelDelete">Nein</button>
            <button type="button" class="btn-yes" :disabled="deleting" @click="confirmDelete">Ja</button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Page content -->
    <main class="page-content">
      <div
        v-if="deleteError && isDetailPage && !isEditPage"
        class="delete-error"
      >{{ deleteError }}</div>
      <RouterView />
    </main>
  </div>
</template>

<style>
/* Global reset */
*, *::before, *::after {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: sans-serif;
  background: #fafafa;
}
</style>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #1a1a2e;
  color: #fff;
  padding: 0.6rem 1rem;
  position: sticky;
  top: 0;
  z-index: 100;
  gap: 0.5rem;
}

.zaehler-label {
  font-size: 0.9rem;
  font-family: monospace;
  opacity: 0.9;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  min-width: 0;
}

.top-bar-actions {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-shrink: 0;
}

.add-btn {
  background: #fff;
  color: #1a1a2e;
  border: none;
  border-radius: 4px;
  font-size: 1.3rem;
  font-weight: 700;
  line-height: 1;
  padding: 0.2rem 0.6rem;
  cursor: pointer;
}

.add-btn:hover {
  background: #e8e8e8;
}

.back-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.2rem 0.4rem;
  flex-shrink: 0;
}

.back-btn:hover {
  opacity: 0.75;
}

.edit-btn,
.delete-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 0.1rem 0.3rem;
}

.edit-btn:hover,
.delete-btn:hover {
  opacity: 0.75;
}

.burger-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 1.4rem;
  cursor: pointer;
  padding: 0.1rem 0.3rem;
  line-height: 1;
}

.burger-btn:hover {
  opacity: 0.75;
}

/* Overlay */
.menu-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 200;
  display: flex;
  justify-content: flex-end;
}

.menu-panel {
  background: #fff;
  width: min(280px, 80vw);
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 1rem;
  box-shadow: -4px 0 16px rgba(0, 0, 0, 0.2);
}

.menu-close {
  align-self: flex-end;
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #333;
  padding: 0.2rem 0.4rem;
  margin-bottom: 1rem;
}

.menu-nav {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.menu-item {
  background: none;
  border: none;
  text-align: left;
  font-size: 1rem;
  padding: 0.75rem 0.5rem;
  cursor: pointer;
  border-radius: 6px;
  color: #222;
}

.menu-item:hover {
  background: #f0f0f0;
}

.page-content {
  flex: 1;
}

/* Delete error banner */
.delete-error {
  background: #fdecea;
  color: #c0392b;
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  border-bottom: 1px solid #f5c6c2;
}

/* Delete confirmation modal */
.delete-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 300;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.delete-dialog {
  background: #fff;
  border-radius: 8px;
  padding: 1.25rem;
  width: min(320px, 90vw);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  text-align: center;
}

.delete-question {
  margin: 0 0 1.25rem;
  font-size: 1.1rem;
  font-weight: 600;
  color: #222;
}

.delete-actions {
  display: flex;
  justify-content: center;
  gap: 0.75rem;
}

.btn-no {
  padding: 0.5rem 1.25rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  background: #fff;
  cursor: pointer;
  font-size: 1rem;
}

.btn-no:hover:not(:disabled) {
  background: #f0f0f0;
}

.btn-yes {
  padding: 0.5rem 1.25rem;
  border: none;
  border-radius: 4px;
  background: #d9534f;
  color: #fff;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
}

.btn-yes:hover:not(:disabled) {
  background: #c9302c;
}

.btn-no:disabled,
.btn-yes:disabled {
  opacity: 0.6;
  cursor: default;
}

/* Transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
