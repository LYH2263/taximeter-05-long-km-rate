<script setup>
import { ref } from 'vue'
import { postJSON } from '../api'
const distance_km = ref(8)
const slow_min = ref(3)
const night = ref(false)
const out = ref(null)
const err = ref('')
const run = async () => {
  err.value = ''
  try {
    out.value = await postJSON('/api/fare', { distance_km: distance_km.value, slow_min: slow_min.value, night: night.value, persist: true })
  } catch (e) { err.value = e.message }
}
</script>
<template>
  <div class="page"><h1>打表试算</h1>
    <div class="panel">
      <label>公里 <input type="number" min="0" v-model.number="distance_km" /></label>
      <label>低速分钟 <input type="number" min="0" v-model.number="slow_min" /></label>
      <label><input type="checkbox" v-model="night" /> 夜间</label>
      <button @click="run">计算</button>
    </div>
    <p v-if="err" class="panel" style="border:1px solid #e06c4a;color:#ffb4a0">{{ err }}</p>
    <div v-if="out" class="panel">
      <p class="hero-num">¥{{ out.total }}</p>
      <table>
        <tr><td>起步价</td><td>¥{{ out.start }}</td></tr>
        <tr>
          <td>普通里程费（{{ out.normal_billable_km }} 公里 × 现价）</td>
          <td>¥{{ out.mileage }}</td>
        </tr>
        <tr v-if="out.long_km_rule_id">
          <td>远程里程费（超 {{ out.long_start_km }} 公里部分 {{ out.remote_billable_km }} 公里 × ¥{{ out.long_per_km }}）</td>
          <td>¥{{ out.long_mileage }}</td>
        </tr>
        <tr v-else><td>远程里程费（未启用远程规则）</td><td>¥0.00</td></tr>
        <tr><td>低速费（{{ out.slow_min }} 分钟）</td><td>¥{{ out.slow_fee }}</td></tr>
      </table>
      <p><small>应付 = 起步 + 普通里程 + 远程里程 + 低速 = ¥{{ out.start }} + ¥{{ out.mileage }} + ¥{{ out.long_mileage }} + ¥{{ out.slow_fee }} = ¥{{ out.total }}</small></p>
    </div>
  </div>
</template>
