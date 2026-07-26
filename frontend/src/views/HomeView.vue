<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getRooms, type Room } from '@/api/client'
import RoomCardsList from '@/components/RoomCardsList.vue'

const rooms = ref<Room[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

async function load() {
  loading.value = true
  error.value = null
  try {
    rooms.value = await getRooms()
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <section>
    <div class="header">
      <h1>Rooms</h1>
      <button @click="load" :disabled="loading">Refresh</button>
    </div>

    <p v-if="loading">Loading…</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <p v-else-if="rooms.length === 0">No rooms found.</p>
    <RoomCardsList v-else :rooms="rooms" />

  </section>
</template>

<style scoped>
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }
</style>
