<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'
const items = ref([])
const res = (h) => { try { return JSON.parse(h.result_json) } catch { return {} } }
onMounted(async () => { items.value = (await getJSON('/api/history')).items })
</script>
<template>
  <div class="page"><h1>记录</h1>
    <table>
      <tr><th>#</th><th>类型</th><th>里程费</th><th>远程里程费</th><th>合计</th></tr>
      <tr v-for="h in items" :key="h.id">
        <td>#{{ h.id }}</td><td>{{ h.kind }}</td>
        <td>{{ res(h).mileage ?? '—' }}</td>
        <td>{{ res(h).long_mileage ?? '—' }}</td>
        <td>{{ res(h).total ?? '—' }}</td>
      </tr>
    </table>
  </div>
</template>
