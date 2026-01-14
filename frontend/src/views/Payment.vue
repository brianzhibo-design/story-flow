<template>
  <div class="payment-page">
    <el-card class="payment-card" shadow="never">
      <!-- 步骤指示器 -->
      <el-steps :active="step" finish-status="success" simple class="steps">
        <el-step title="确认订单" />
        <el-step title="选择支付" />
        <el-step title="完成支付" />
      </el-steps>
      
      <el-divider />
      
      <!-- 订单信息 -->
      <div class="order-info">
        <h2>订单信息</h2>
        
        <div class="order-details">
          <div class="order-row">
            <span class="label">订阅计划</span>
            <span class="value">{{ planName }}</span>
          </div>
          <div class="order-row">
            <span class="label">计费周期</span>
            <span class="value">{{ cycleText }}</span>
          </div>
          <div class="order-row" v-if="priceInfo.saved > 0">
            <span class="label">原价</span>
            <span class="value original">¥{{ priceInfo.original_price }}</span>
          </div>
          <div class="order-row" v-if="priceInfo.saved > 0">
            <span class="label">优惠</span>
            <span class="value discount">-¥{{ priceInfo.saved }}</span>
          </div>
        </div>
        
        <el-divider />
        
        <div class="order-total">
          <span class="label">应付金额</span>
          <span class="price">¥{{ priceInfo.final_price }}</span>
        </div>
      </div>
      
      <!-- 支付方式选择 -->
      <div class="payment-methods" v-if="!order">
        <h3>选择支付方式</h3>
        
        <div class="methods">
          <div 
            class="method" 
            :class="{ active: paymentMethod === 'alipay' }"
            @click="paymentMethod = 'alipay'"
          >
            <div class="method-icon alipay">
              <svg viewBox="0 0 24 24" width="32" height="32">
                <path fill="currentColor" d="M8.14 14.44L12 12.5l3.86 1.94a6.5 6.5 0 1 0-7.72 0zm1.36-1.94l2.5-1.25 2.5 1.25a5 5 0 1 1-5 0z"/>
              </svg>
            </div>
            <div class="method-info">
              <span class="method-name">支付宝</span>
              <span class="method-desc">支持花呗、余额宝</span>
            </div>
            <el-icon v-if="paymentMethod === 'alipay'" class="check-icon"><Check /></el-icon>
          </div>
          
          <div 
            class="method"
            :class="{ active: paymentMethod === 'wechat' }"
            @click="paymentMethod = 'wechat'"
          >
            <div class="method-icon wechat">
              <svg viewBox="0 0 24 24" width="32" height="32">
                <path fill="currentColor" d="M8.5 6C4.9 6 2 8.5 2 11.5c0 1.7.9 3.2 2.3 4.2l-.5 1.8 2-1.1c.6.2 1.1.3 1.7.3.3 0 .6 0 .9-.1A5.5 5.5 0 0 1 8 14c0-3 2.7-5.5 6-5.5.4 0 .7 0 1 .1C14.4 7 11.6 6 8.5 6z"/>
              </svg>
            </div>
            <div class="method-info">
              <span class="method-name">微信支付</span>
              <span class="method-desc">扫码支付</span>
            </div>
            <el-icon v-if="paymentMethod === 'wechat'" class="check-icon"><Check /></el-icon>
          </div>
        </div>
        
        <el-button 
          type="primary" 
          size="large" 
          class="pay-button"
          :loading="loading"
          @click="createOrder"
        >
          立即支付 ¥{{ priceInfo.final_price }}
        </el-button>
        
        <p class="pay-tip">
          点击支付即表示您同意 
          <a href="/terms" target="_blank">服务条款</a> 和 
          <a href="/privacy" target="_blank">隐私政策</a>
        </p>
      </div>
      
      <!-- 微信支付二维码 -->
      <div class="qrcode-section" v-if="order && paymentMethod === 'wechat'">
        <h3>微信扫码支付</h3>
        
        <div class="qrcode-wrapper">
          <div class="qrcode">
            <!-- 使用 canvas 绘制二维码 -->
            <canvas ref="qrcodeCanvas"></canvas>
          </div>
          
          <p class="qrcode-tip">请使用微信扫一扫完成支付</p>
          
          <div class="countdown">
            <el-icon><Timer /></el-icon>
            <span>支付剩余时间: <strong>{{ countdown }}</strong></span>
          </div>
        </div>
        
        <el-button type="text" @click="cancelOrder">取消支付</el-button>
      </div>
      
      <!-- 支付宝跳转提示 -->
      <div class="redirect-section" v-if="order && paymentMethod === 'alipay'">
        <el-icon class="loading-icon" :size="64" color="var(--el-color-primary)">
          <Loading />
        </el-icon>
        <h3>正在跳转支付宝...</h3>
        <p class="redirect-tip">
          如果没有自动跳转，请 
          <a :href="order.pay_url" target="_blank">点击这里</a>
        </p>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Check, Timer, Loading } from '@element-plus/icons-vue'
import { paymentApi, type PaymentOrder, type PriceInfo } from '@/api/payment'
import QRCode from 'qrcode'

const route = useRoute()
const router = useRouter()

// 路由参数
const planType = route.query.plan as string || 'basic'
const billingCycle = route.query.cycle as string || 'monthly'

// 状态
const step = ref(0)
const priceInfo = ref<PriceInfo>({ original_price: 0, final_price: 0, discount: 0, saved: 0 })
const paymentMethod = ref<'alipay' | 'wechat'>('alipay')
const order = ref<PaymentOrder | null>(null)
const loading = ref(false)
const countdown = ref('30:00')
const qrcodeCanvas = ref<HTMLCanvasElement | null>(null)

// 计划名称
const planNames: Record<string, string> = {
  basic: '基础版',
  pro: '专业版',
  enterprise: '企业版'
}
const planName = computed(() => planNames[planType] || planType)
const cycleText = computed(() => billingCycle === 'yearly' ? '年付' : '月付')

// 获取价格
onMounted(async () => {
  try {
    const res = await paymentApi.getPrice(planType, billingCycle)
    priceInfo.value = res.data.data
  } catch (error) {
    ElMessage.error('获取价格失败')
    router.push('/pricing')
  }
})

// 创建订单
async function createOrder() {
  loading.value = true
  step.value = 1
  
  try {
    const res = await paymentApi.createOrder(planType, billingCycle, paymentMethod.value)
    order.value = res.data.data
    step.value = 2
    
    if (paymentMethod.value === 'alipay') {
      // 支付宝跳转
      window.location.href = order.value!.pay_url
    } else {
      // 微信生成二维码
      await nextTick()
      generateQRCode(order.value!.pay_url)
      startPolling()
      startCountdown()
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '创建订单失败')
    step.value = 0
  } finally {
    loading.value = false
  }
}

// 生成二维码
async function generateQRCode(url: string) {
  if (qrcodeCanvas.value) {
    await QRCode.toCanvas(qrcodeCanvas.value, url, {
      width: 200,
      margin: 2,
      color: {
        dark: '#000000',
        light: '#ffffff'
      }
    })
  }
}

// 轮询订单状态
let pollTimer: number | null = null
function startPolling() {
  pollTimer = window.setInterval(async () => {
    if (!order.value) return
    
    try {
      const res = await paymentApi.queryOrder(order.value.order_no)
      if (res.data.data.payment_status === 'paid') {
        stopPolling()
        router.push(`/payment/success?order=${order.value.order_no}`)
      }
    } catch (error) {
      console.error('Poll order failed:', error)
    }
  }, 3000)
}

function stopPolling() {
  if (pollTimer) {
    window.clearInterval(pollTimer)
    pollTimer = null
  }
}

// 倒计时
let countdownTimer: number | null = null
function startCountdown() {
  let seconds = 30 * 60 // 30 分钟
  
  countdownTimer = window.setInterval(() => {
    seconds--
    const min = Math.floor(seconds / 60)
    const sec = seconds % 60
    countdown.value = `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`
    
    if (seconds <= 0) {
      stopCountdown()
      router.push('/payment/expired')
    }
  }, 1000)
}

function stopCountdown() {
  if (countdownTimer) {
    window.clearInterval(countdownTimer)
    countdownTimer = null
  }
}

// 取消支付
function cancelOrder() {
  stopPolling()
  stopCountdown()
  order.value = null
  step.value = 0
}

// 清理
onUnmounted(() => {
  stopPolling()
  stopCountdown()
})
</script>

<style scoped>
.payment-page {
  min-height: 100vh;
  background: var(--el-fill-color-lighter);
  padding: 40px 24px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.payment-card {
  width: 100%;
  max-width: 560px;
  border-radius: 16px;
}

.steps {
  margin-bottom: 24px;
}

.order-info h2 {
  font-size: 20px;
  font-weight: 600;
  margin: 0 0 20px;
}

.order-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.order-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.order-row .label {
  color: var(--el-text-color-secondary);
}

.order-row .value {
  font-weight: 500;
}

.order-row .value.original {
  text-decoration: line-through;
  color: var(--el-text-color-secondary);
}

.order-row .value.discount {
  color: var(--el-color-success);
}

.order-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.order-total .label {
  font-size: 16px;
  font-weight: 500;
}

.order-total .price {
  font-size: 32px;
  font-weight: 700;
  color: var(--el-color-primary);
}

.payment-methods h3 {
  font-size: 16px;
  font-weight: 600;
  margin: 24px 0 16px;
}

.methods {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.method {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border: 2px solid var(--el-border-color);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.method:hover {
  border-color: var(--el-color-primary-light-5);
}

.method.active {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.method-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.method-icon.alipay {
  background: #1677ff;
  color: white;
}

.method-icon.wechat {
  background: #07c160;
  color: white;
}

.method-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.method-name {
  font-weight: 600;
}

.method-desc {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.check-icon {
  color: var(--el-color-primary);
  font-size: 20px;
}

.pay-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
}

.pay-tip {
  text-align: center;
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 16px;
}

.pay-tip a {
  color: var(--el-color-primary);
}

.qrcode-section,
.redirect-section {
  text-align: center;
  padding: 24px 0;
}

.qrcode-section h3,
.redirect-section h3 {
  font-size: 18px;
  margin-bottom: 24px;
}

.qrcode-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.qrcode {
  padding: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.qrcode canvas {
  display: block;
}

.qrcode-tip {
  color: var(--el-text-color-secondary);
}

.countdown {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--el-color-warning);
}

.redirect-section .loading-icon {
  animation: spin 1.5s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.redirect-tip {
  color: var(--el-text-color-secondary);
  margin-top: 16px;
}

.redirect-tip a {
  color: var(--el-color-primary);
}
</style>

