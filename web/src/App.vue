<script setup lang="ts">
import { ref, watch } from 'vue'
import { auditEvents, chat, decide as decideApproval, listApprovals, propose as proposeAction, uploadMarkdown } from './api/client'

const message = ref('')
const result = ref('')
const conversationId = crypto.randomUUID()
const proposal = ref<{ status: string; risk: string; approval_id?: string } | null>(null)
const activeView = ref<'chat' | 'approvals' | 'knowledge' | 'trace' | 'evaluation'>('chat')
const trace = ref<string[]>([])
const approvals = ref<Record<string, unknown>[]>([])
const uploadMessage = ref('')

watch(activeView, async (view) => {
  if (view === 'approvals') approvals.value = await listApprovals()
  if (view === 'trace') trace.value = (await auditEvents()).map((event) => JSON.stringify(event))
})

async function upload(file: Event) {
  const input = file.target as HTMLInputElement
  if (!input.files?.[0]) return
  const response = await uploadMarkdown(input.files[0])
  uploadMessage.value = `已入库 ${response.chunk_count ?? 0} 个片段`
}

async function ask() {
  result.value = JSON.stringify(await chat(message.value, conversationId), null, 2)
  trace.value.unshift(`${new Date().toLocaleTimeString()} · 对话运行完成`)
}

async function propose() {
  proposal.value = await proposeAction('product.update', { id: 'p-100' }) as typeof proposal.value
}

async function decide(decision: 'approved' | 'rejected') {
  if (!proposal.value?.approval_id) return
  proposal.value = await decideApproval(proposal.value.approval_id, decision) as typeof proposal.value
}
</script>

<template>
  <main class="shell">
    <header class="hero"><div><span class="eyebrow">OPS / AGENT CONTROL ROOM</span><h1>让每一次运营决策，都有依据。</h1><p>把实时业务、制度知识与人工审批放在同一条可追溯链路上。</p></div><div class="signal"><span></span>系统在线</div></header>
    <nav class="tabs" aria-label="工作台导航"><button v-for="item in [['chat','对话工作台'],['approvals','审批中心'],['knowledge','知识库'],['trace','运行轨迹'],['evaluation','评估中心']]" :key="item[0]" :class="{ active: activeView === item[0] }" @click="activeView = item[0] as typeof activeView">{{ item[1] }}</button></nav>
    <section v-if="activeView === 'chat'" class="workspace"><div class="panel primary"><div class="panel-kicker">LIVE QUERY · {{ conversationId.slice(0, 8) }}</div><label for="question">向 Agent 提问</label><textarea id="question" v-model="message" placeholder="例如：查询商品库存，或分析订单状态"></textarea><button @click="ask">执行查询 <span>↗</span></button><pre v-if="result">{{ result }}</pre></div><aside class="panel rail"><h2>安全审批</h2><p>商品更新进入人工确认；退款、删除和权限变更默认阻断。</p><button class="secondary" @click="propose">生成商品更新提案</button><template v-if="proposal?.status === 'waiting_approval'"><button @click="decide('approved')">批准</button><button class="danger" @click="decide('rejected')">拒绝</button></template><pre v-if="proposal">{{ proposal }}</pre></aside></section>
    <section v-else-if="activeView === 'approvals'" class="panel empty"><span class="number">02</span><h2>审批中心</h2><p>待处理提案会在这里聚合。</p><ul><li v-for="item in approvals" :key="String(item.id)">{{ item.action }} · {{ item.status }}</li><li v-if="!approvals.length">暂无审批记录</li></ul><button @click="activeView = 'chat'">返回对话</button></section>
    <section v-else-if="activeView === 'knowledge'" class="panel empty"><span class="number">03</span><h2>知识库</h2><p>上传制度、源码和运营手册，转换后生成可引用证据。</p><label class="dropzone">选择 Markdown 文件<input type="file" accept=".md,.txt" hidden @change="upload" /></label><p v-if="uploadMessage">{{ uploadMessage }}</p></section>
    <section v-else-if="activeView === 'trace'" class="panel empty"><span class="number">04</span><h2>运行轨迹</h2><p>不展示隐藏思维链，只展示状态、工具、审批和引用事件。</p><ul><li v-for="item in trace" :key="item">{{ item }}</li><li v-if="!trace.length">尚未运行任务</li></ul></section>
    <section v-else class="panel empty"><span class="number">05</span><h2>评估中心</h2><p>Golden Questions、工具正确率和安全决策准确率将在此展示。</p><div class="score-grid"><strong>—<small>Recall@K</small></strong><strong>—<small>工具正确率</small></strong><strong>—<small>安全准确率</small></strong></div></section>
  </main>
</template>
