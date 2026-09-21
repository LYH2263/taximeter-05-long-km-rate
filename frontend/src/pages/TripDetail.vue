<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getJSON, postJSON } from '../api'
const route = useRoute()
const trip = ref(null)
const fare = ref(null)
const load = async () => {
  trip.value = await getJSON(`/api/trips/${route.params.id}`)
  // 行程详情为只读打表：persist=false，不写记录。
  fare.value = await postJSON('/api/fare', { distance_km: trip.value.distance_km, slow_min: trip.value.slow_min, night: !!trip.value.night, trip_id: trip.value.id, persist: false })
}
onMounted(load); watch(() => route.params.id, load)
</script>
<template>
  <div class="page" v-if="trip"><h1>{{ trip.label }}</h1>
    <div v-if="fare" class="panel">
      <p class="hero-num">¥{{ fare.total }}</p>
      <table>
        <tr><td>起步</td><td>¥{{ fare.start }}</td></tr>
        <tr>
          <td>普通里程（{{ fare.normal_billable_km }} 公里）</td>
          <td>¥{{ fare.mileage }}</td>
        </tr>
        <tr v-if="fare.long_km_rule_id">
          <td>远程里程（超 {{ fare.long_start_km }} 公里部分 {{ fare.remote_billable_km }} 公里 × ¥{{ fare.long_per_km }}）</td>
          <td>¥{{ fare.long_mileage }}</td>
        </tr>
        <tr v-else><td>远程里程（未启用远程规则）</td><td>¥0.00</td></tr>
        <tr><td>低速</td><td>¥{{ fare.slow_fee }}</td></tr>
      </table>
      <p><small>应付 = 起步 + 普通里程 + 远程里程 + 低速</small></p>
    </div>
  </div>
</template>
