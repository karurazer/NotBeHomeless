<script setup lang="ts">
import { type Room } from '@/api/client'

const props = defineProps<{ rooms: Room[] }>()

</script>

<template>
  <section>
    <ul class="rooms">
      <li v-for="room in props.rooms" :key="room.room_id" class="room">
        <div class="room-main">
          <a :href="room.link" target="_blank" rel="noopener noreferrer">{{ room.title }}</a>
          <span class="meta">{{ room.city }} · {{ room.size }} m² · €{{ room.price }}</span>
        </div>
        <div class="tags">
          <span v-if="room.private_kitchen" class="tag">kitchen</span>
          <span v-if="room.private_bathroom" class="tag">bathroom</span>
          <span v-if="room.furnished" class="tag">furnished</span>
          <span v-if="room.wifi" class="tag">wifi</span>
          <span class="tag" :class="room.status">{{ room.status }}</span>
        </div>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.rooms {
  list-style: none;
}

.room {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.room-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.meta {
  font-size: 0.78rem;
  color: var(--color-text);
  opacity: 0.9;
}

.tags {
  margin-top: 0.7rem;
}

.tag {
  display: inline-block;
  background-color: var(--color-background-mute);
  border: 1px solid transparent;
  border-radius: 4px;
  padding: 0.2rem 0.5rem;
  margin-right: 0.5rem;
  font-size: 0.8rem;
}

.tag.reacted {
  background-color: var(--color-success-bg);
  border-color: var(--color-success-border);
  color: var(--color-success);
}

.tag.not_reacted {
  background-color: var(--color-warning-bg);
  border-color: var(--color-warning-border);
  color: var(--color-warning);
}
</style>
