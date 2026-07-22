import { expect, test } from '@playwright/test'

test('对话工作台可以提交查询并显示结果', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { name: '让每一次运营决策，都有依据。' })).toBeVisible()
  await page.getByLabel('向 Agent 提问').fill('查询商品库存')
  await page.getByRole('button', { name: /执行查询/ }).click()
  await expect(page.locator('pre').first()).toContainText('run_id')
})

test('知识库上传和审批提案可以完成闭环', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('button', { name: '知识库' }).click()
  await page.locator('input[type="file"]').setInputFiles({
    name: 'playwright.md',
    mimeType: 'text/markdown',
    buffer: Buffer.from('# 退货制度\n支持七天无理由退货。'),
  })
  await expect(page.getByText(/已入库 \d+ 个片段/)).toBeVisible()

  await page.getByRole('button', { name: '对话工作台' }).click()
  await page.getByRole('button', { name: '生成商品更新提案' }).click()
  await expect(page.locator('pre').last()).toContainText('waiting_approval')
  await page.getByRole('button', { name: '拒绝' }).click()
  await expect(page.locator('pre').last()).toContainText('rejected')
})
