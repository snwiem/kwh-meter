<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const menuOpen = ref(false)

function navigate(to: string) {
  menuOpen.value = false
  router.push(to)
}
</script>

<template>
  <div class="app-shell">
    <!-- Global top bar -->
    <div class="top-bar">
      <span class="app-title">⚡ kWh Meter</span>
      <button class="burger-btn" aria-label="Menü öffnen" @click="menuOpen = true">☰</button>
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

    <!-- Page content -->
    <main class="page-content">
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
}

.app-title {
  font-weight: 700;
  font-size: 1rem;
  letter-spacing: 0.02em;
}

.burger-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 1.4rem;
  cursor: pointer;
  padding: 0.1rem 0.4rem;
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
