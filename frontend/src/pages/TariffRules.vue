<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON, putJSON } from '../api'
const t = ref(null)
const items = ref([])
const start_km = ref(10)
const per_km = ref(4)
const err = ref('')
const editId = ref(null)
const editStart = ref(0)
const editPer = ref(0)
const showErr = (e) => {
  let msg = e.message
  try { const d = JSON.parse(e.message).detail; msg = typeof d === 'string' ? d : JSON.stringify(d) } catch { /* 保留原文 */ }
  err.value = msg
}
const load = async () => {
  t.value = await getJSON('/api/tariff')
  items.value = (await getJSON('/api/long-km-rate')).items
}
const create = async () => {
  err.value = ''
  try {
    await postJSON('/api/long-km-rate', { start_km: start_km.value, per_km: per_km.value })
    await load()
  } catch (e) { showErr(e) }
}
const beginEdit = (r) => { editId.value = r.id; editStart.value = r.start_km; editPer.value = r.per_km; err.value = '' }
const saveEdit = async (id) => {
  err.value = ''
  try {
    await putJSON(`/api/long-km-rate/${id}`, { start_km: editStart.value, per_km: editPer.value })
    editId.value = null
    await load()
  } catch (e) { showErr(e) }
}
const deactivate = async (id) => {
  err.value = ''
  try { await postJSON(`/api/long-km-rate/${id}/deactivate`, {}); await load() }
  catch (e) { showErr(e) }
}
const activate = async (id) => {
  err.value = ''
  try { await putJSON(`/api/long-km-rate/${id}`, { active: true }); await load() }
  catch (e) { showErr(e) }
}
onMounted(load)
</script>
<template>
  <div class="page"><h1>运价表</h1>
    <div v-if="t" class="panel">
      起步 ¥{{ t.start_price }}(含 {{ t.start_include_km }}km)· 每公里 ¥{{ t.per_km }} ·
      低速每分钟 ¥{{ t.per_slow_min }} · 夜间系数 ×{{ t.night_factor }}
    </div>
    <h2>远程里程单价</h2>
    <div class="panel">
      <label>远程起算公里 <input type="number" step="0.1" v-model.number="start_km" /></label>
      <label>远程每公里单价 <input type="number" step="0.1" v-model.number="per_km" /></label>
      <button @click="create">创建</button>
      <p v-if="err" class="err">{{ err }}</p>
    </div>
    <table v-if="items.length">
      <tr><th>#</th><th>起算公里</th><th>每公里单价</th><th>状态</th><th>操作</th></tr>
      <tr v-for="r in items" :key="r.id">
        <td>#{{ r.id }}</td>
        <template v-if="editId === r.id">
          <td><input type="number" step="0.1" v-model.number="editStart" /></td>
          <td><input type="number" step="0.1" v-model.number="editPer" /></td>
        </template>
        <template v-else>
          <td>{{ r.start_km }}</td>
          <td>{{ r.per_km }}</td>
        </template>
        <td>{{ r.active ? '启用' : '停用' }}</td>
        <td>
          <template v-if="editId === r.id">
            <button @click="saveEdit(r.id)">保存</button>
            <button @click="editId = null">取消</button>
          </template>
          <template v-else>
            <button @click="beginEdit(r)">编辑</button>
            <button v-if="r.active" @click="deactivate(r.id)">停用</button>
            <button v-else @click="activate(r.id)">启用</button>
          </template>
        </td>
      </tr>
    </table>
    <p v-else>暂无远程规则,全程按每公里 ¥{{ t?.per_km }} 计。</p>
  </div>
</template>
