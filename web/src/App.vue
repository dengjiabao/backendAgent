<script setup lang="ts">
import { ref } from 'vue'
import { chat, decide, propose } from './api/client'

const message = ref('')
const result = ref('')
const conversationId = crypto.randomUUID()
const proposal = ref<{ status: string; risk: string; approval_id?: string } | null>(null)

async function ask() {
  result.value = JSON.stringify(await chat(message.value, conversationId), null, 2)
}

async function propose() {
  proposal.value = await propose('product.update', { id: 'p-100' }) as typeof proposal.value
}

async function decide(decision: 'approved' | 'rejected') {
  if (!proposal.value?.approval_id) return
  proposal.value = await decide(proposal.value.approval_id, decision) as typeof proposal.value
}
</script>

<template>
  <main class="shell">
    <header><span class="eyebrow">ENTERPRISE COMMERCE AGENT</span><h1>电商运营智能工作台</h1><p>独立运行，也可连接 litemall、OpenAPI 或 MCP 电商系统。</p></header>
    <section class="panel"><label for="question">向 Agent 提问</label><textarea id="question" v-model="message" placeholder="例如：查询商品库存，或分析订单状态"></textarea><button @click="ask">执行查询</button><pre v-if="result">{{ result }}</pre></section>
    <section class="panel"><h2>安全审批演示</h2><p>商品更新会进入审批；退款、删除和权限变更默认阻断。</p><button class="secondary" @click="propose">生成商品更新提案</button><template v-if="proposal?.status === 'waiting_approval'"><button @click="decide('approved')">批准</button><button class="danger" @click="decide('rejected')">拒绝</button></template><pre v-if="proposal">{{ proposal }}</pre></section>
  </main>
</template>
