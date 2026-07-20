<script setup lang="ts">
import { ref } from 'vue'

const message = ref('')
const result = ref('')
const proposal = ref<{ status: string; risk: string } | null>(null)

async function ask() {
  const response = await fetch('http://127.0.0.1:8000/api/v1/chat', {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: message.value }),
  })
  result.value = JSON.stringify(await response.json(), null, 2)
}

async function propose() {
  const response = await fetch('http://127.0.0.1:8000/api/v1/tools/propose', {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'product.update', arguments: { id: 'p-100' } }),
  })
  proposal.value = await response.json()
}
</script>

<template>
  <main class="shell">
    <header><span class="eyebrow">ENTERPRISE COMMERCE AGENT</span><h1>电商运营智能工作台</h1><p>独立运行，也可连接 litemall、OpenAPI 或 MCP 电商系统。</p></header>
    <section class="panel"><label for="question">向 Agent 提问</label><textarea id="question" v-model="message" placeholder="例如：查询商品库存，或分析订单状态"></textarea><button @click="ask">执行查询</button><pre v-if="result">{{ result }}</pre></section>
    <section class="panel"><h2>安全审批演示</h2><p>商品更新会进入审批；退款、删除和权限变更默认阻断。</p><button class="secondary" @click="propose">生成商品更新提案</button><pre v-if="proposal">{{ proposal }}</pre></section>
  </main>
</template>
