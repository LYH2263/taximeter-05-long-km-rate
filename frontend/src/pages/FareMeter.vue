<script setup>
import { ref } from 'vue'
import { postJSON } from '../api'
const distance_km = ref(8)
const slow_min = ref(3)
const night = ref(false)
const persist = ref(false)
const out = ref(null)
const run = async () => { out.value = await postJSON('/api/fare', { distance_km: distance_km.value, slow_min: slow_min.value, night: night.value, persist: persist.value }) }
</script>
<template>
  <div class="page"><h1>打表试算</h1>
    <div class="panel">
      <label>公里 <input type="number" v-model.number="distance_km" /></label>
      <label>低速分钟 <input type="number" v-model.number="slow_min" /></label>
      <label><input type="checkbox" v-model="night" /> 夜间</label>
      <label><input type="checkbox" v-model="persist" /> 写入记录</label>
      <button @click="run">计算</button>
    </div>
    <p v-if="out" class="hero-num">¥{{ out.total }}</p>
    <div v-if="out" class="panel">
      <p>起步 ¥{{ out.start }}</p>
      <p>普通里程费 ¥{{ out.mileage }}({{ out.normal_km }} km)</p>
      <p>远程里程费 ¥{{ out.long_mileage }}({{ out.long_km }} km)</p>
      <p>低速费 ¥{{ out.slow_fee }}</p>
      <p>应付 = 起步 + 普通里程 + 远程里程 + 低速</p>
    </div>
  </div>
</template>
