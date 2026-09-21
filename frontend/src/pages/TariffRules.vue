<script setup>
import { onMounted, reactive, ref } from 'vue'
import { getJSON, postJSON, putJSON } from '../api'

const t = ref(null)
const items = ref([])
const err = ref('')
const form = reactive({ id: null, label: '', start_km: 10, per_km: 3.5, active: false })

async function load() {
  [t.value, items.value] = await Promise.all([
    getJSON('/api/tariff'),
    getJSON('/api/long-km-rates').then(r => r.items),
  ])
}
onMounted(load)

function resetForm() {
  form.id = null; form.label = ''; form.start_km = 10; form.per_km = 3.5; form.active = false
}

async function submit() {
  err.value = ''
  try {
    const body = { label: form.label, start_km: form.start_km, per_km: form.per_km, active: form.active }
    if (form.id == null) await postJSON('/api/long-km-rates', body)
    else await putJSON(`/api/long-km-rates/${form.id}`, body)
    resetForm()
    await load()
  } catch (e) { err.value = e.message }
}

function edit(row) {
  err.value = ''
  form.id = row.id; form.label = row.label
  form.start_km = row.start_km; form.per_km = row.per_km; form.active = !!row.active
}

async function deactivate(row) {
  err.value = ''
  try {
    await postJSON(`/api/long-km-rates/${row.id}/deactivate`)
    if (form.id === row.id) resetForm()
    await load()
  } catch (e) { err.value = e.message }
}
</script>
<template>
  <div class="page">
    <h1>运价表</h1>
    <div v-if="t" class="panel">
      <strong>现行运价</strong>
      起步 ¥{{ t.start_price }}（含 {{ t.start_include_km }} 公里）·
      每公里 ¥{{ t.per_km }} · 低速每分钟 ¥{{ t.per_slow_min }}
      <br /><small>远程起算公里必须大于现行含公里（{{ t.start_include_km }} 公里）；同一时间只允许一条远程规则启用。</small>
    </div>

    <h2>远程里程单价</h2>
    <p v-if="err" class="panel" style="border:1px solid #e06c4a;color:#ffb4a0">{{ err }}</p>

    <table>
      <tr><th>#</th><th>标识</th><th>远程起算(公里)</th><th>远程单价(元/公里)</th><th>状态</th><th>操作</th></tr>
      <tr v-for="r in items" :key="r.id">
        <td>{{ r.id }}</td>
        <td>{{ r.label }}</td>
        <td>{{ r.start_km }}</td>
        <td>{{ r.per_km }}</td>
        <td>{{ r.active ? '启用中' : '已停用' }}</td>
        <td>
          <button @click="edit(r)">编辑</button>
          <button v-if="r.active" @click="deactivate(r)">停用</button>
        </td>
      </tr>
      <tr v-if="!items.length"><td colspan="6">暂无远程规则</td></tr>
    </table>

    <div class="panel">
      <h3>{{ form.id == null ? '新建远程规则' : `编辑规则 #${form.id}` }}</h3>
      <label>标识 <input v-model="form.label" placeholder="如：夜间长途远程价" /></label>
      <label>远程起算公里 <input type="number" min="0" step="0.1" v-model.number="form.start_km" /></label>
      <label>远程每公里单价 <input type="number" min="0" step="0.1" v-model.number="form.per_km" /></label>
      <label><input type="checkbox" v-model="form.active" /> 立即启用</label>
      <p><button @click="submit">保存</button> <button v-if="form.id != null" @click="resetForm">取消编辑</button></p>
    </div>
  </div>
</template>
