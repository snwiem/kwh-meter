<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

function download(path: string) {
  const a = document.createElement('a')
  a.href = path
  a.download = ''
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}
</script>

<template>
  <div class="screen">
    <header class="header">
      <button class="back-btn" @click="router.push('/')" aria-label="Zurück">← Zurück</button>
      <h1 class="title">Export</h1>
    </header>

    <main class="content">
      <p class="description">
        Alle Ablesungen des aktuellen Zählers als Datei herunterladen.
      </p>

      <div class="buttons">
        <button class="download-btn tsv-btn" @click="download('/api/export/tsv')">
          <span class="btn-icon">📄</span>
          <span class="btn-label">
            <strong>Export als TSV</strong>
            <small>Tabulatorgetrennte Werte</small>
          </span>
        </button>

        <button class="download-btn json-btn" @click="download('/api/export/json')">
          <span class="btn-icon">📋</span>
          <span class="btn-label">
            <strong>Export als JSON</strong>
            <small>Strukturiertes JSON-Format</small>
          </span>
        </button>
      </div>
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

.description {
  color: #555;
  margin-bottom: 1.5rem;
}

.buttons {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.download-btn {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  text-align: left;
  width: 100%;
  transition: background 0.15s;
}

.download-btn:hover {
  background: #f5f5f5;
}

.btn-icon {
  font-size: 1.8rem;
  line-height: 1;
}

.btn-label {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.btn-label strong {
  font-size: 1rem;
}

.btn-label small {
  font-size: 0.8rem;
  color: #888;
}
</style>
