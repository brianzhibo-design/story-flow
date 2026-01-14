<template>
  <div class="create-project-page">
    <!-- Main Content -->
    <main class="main-content">
      <!-- Top Bar -->
      <header class="top-bar">
        <button class="cancel-btn" @click="handleCancel">
          <div class="icon-wrapper">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
            </svg>
          </div>
          <span>取消</span>
        </button>
        
        <div class="step-indicator">
          步骤 <span class="step-current">1</span> / 2
        </div>
      </header>

      <!-- Form Container -->
      <div class="form-container">
        <div class="form-header">
          <h1>创建新项目</h1>
          <p>选择如何开始讲述你的故事</p>
        </div>

        <form class="create-form" @submit.prevent="handleSubmit">
          <!-- Section 1: Project Basics -->
          <div class="form-section">
            <div class="input-group" :class="{ focused: titleFocused }">
              <label>项目标题</label>
              <input
                v-model="form.title"
                type="text"
                placeholder="例如：2025年AI的未来"
                @focus="titleFocused = true"
                @blur="titleFocused = false"
              />
            </div>

            <!-- Aspect Ratio Selection -->
            <div class="ratio-section">
              <label class="section-label">画面比例</label>
              <div class="ratio-grid">
                <div
                  v-for="ratio in aspectRatios"
                  :key="ratio.value"
                  class="option-card"
                  :class="{ selected: form.aspect_ratio === ratio.value }"
                  @click="form.aspect_ratio = ratio.value"
                >
                  <div class="ratio-preview" :style="ratio.style"></div>
                  <div class="ratio-info">
                    <span class="ratio-name">{{ ratio.name }}</span>
                    <span class="ratio-desc">{{ ratio.desc }}</span>
                  </div>
                  <div class="check-icon" v-if="form.aspect_ratio === ratio.value">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                      <polyline points="22 4 12 14.01 9 11.01"/>
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Divider -->
          <div class="divider"></div>

          <!-- Section 2: Input Method -->
          <div class="form-section">
            <label class="section-label">创作方式</label>
            <div class="source-grid">
              <div
                v-for="source in inputSources"
                :key="source.value"
                class="option-card source-card"
                :class="{ 
                  selected: form.source_type === source.value,
                  disabled: source.disabled 
                }"
                @click="!source.disabled && (form.source_type = source.value)"
              >
                <div class="icon-box" :class="{ active: form.source_type === source.value }">
                  <component :is="source.icon" />
                </div>
                <div class="source-info">
                  <h3>{{ source.name }}</h3>
                  <p>{{ source.desc }}</p>
                </div>
                <div class="radio-icon">
                  <svg v-if="form.source_type === source.value" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="3" fill="currentColor"/>
                  </svg>
                  <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"/>
                  </svg>
                </div>
                <span v-if="source.disabled" class="coming-soon">即将推出</span>
              </div>
            </div>
          </div>

          <!-- Dynamic Input Area -->
          <div class="form-section input-area">
            <label class="section-label">
              <span>{{ inputLabel }}</span>
              <span class="inspiration-link" @click="showInspiration">需要灵感？</span>
            </label>
            <div class="textarea-wrapper" :class="{ focused: contentFocused }">
              <textarea
                v-model="form.story_text"
                :placeholder="inputPlaceholder"
                @focus="contentFocused = true"
                @blur="contentFocused = false"
              ></textarea>
              <div class="char-count">{{ form.story_text.length }}/5000</div>
            </div>
          </div>
        </form>
      </div>

      <!-- Sticky Bottom Bar -->
      <div class="bottom-bar">
        <div class="bottom-content">
          <div class="credit-info">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>
            </svg>
            <span>预计消耗约 <strong>15 积分</strong></span>
          </div>
          <div class="action-buttons">
            <button type="button" class="btn-secondary" @click="saveDraft">
              保存草稿
            </button>
            <button 
              type="button" 
              class="btn-primary"
              :disabled="!isFormValid || loading"
              @click="handleSubmit"
            >
              <span v-if="loading">创建中...</span>
              <template v-else>
                创建项目
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>
                </svg>
              </template>
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, h } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useProjectStore } from '@/stores'

const router = useRouter()
const projectStore = useProjectStore()

const loading = ref(false)
const titleFocused = ref(false)
const contentFocused = ref(false)

const form = reactive({
  title: '',
  story_text: '',
  description: '',
  aspect_ratio: '16:9',
  source_type: 'idea',
})

// Aspect Ratio Options
const aspectRatios = [
  { 
    value: '16:9', 
    name: '16:9 横屏', 
    desc: 'YouTube, 网页',
    style: { width: '48px', height: '28px' }
  },
  { 
    value: '9:16', 
    name: '9:16 竖屏', 
    desc: '抖音, Reels, Shorts',
    style: { width: '20px', height: '32px' }
  },
  { 
    value: '1:1', 
    name: '1:1 正方形', 
    desc: 'Instagram, 动态',
    style: { width: '32px', height: '32px' }
  },
]

// SVG Icon Components
const SparklesIcon = () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', width: 20, height: 20, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
  h('path', { d: 'm12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z' }),
  h('path', { d: 'M5 3v4' }),
  h('path', { d: 'M19 17v4' }),
  h('path', { d: 'M3 5h4' }),
  h('path', { d: 'M17 19h4' }),
])

const FileTextIcon = () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', width: 20, height: 20, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
  h('path', { d: 'M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z' }),
  h('polyline', { points: '14 2 14 8 20 8' }),
  h('line', { x1: 16, y1: 13, x2: 8, y2: 13 }),
  h('line', { x1: 16, y1: 17, x2: 8, y2: 17 }),
  h('line', { x1: 10, y1: 9, x2: 8, y2: 9 }),
])

const LinkIcon = () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', width: 20, height: 20, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
  h('path', { d: 'M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71' }),
  h('path', { d: 'M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71' }),
])

const MicIcon = () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', width: 20, height: 20, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
  h('path', { d: 'M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z' }),
  h('path', { d: 'M19 10v2a7 7 0 0 1-14 0v-2' }),
  h('line', { x1: 12, y1: 19, x2: 12, y2: 22 }),
])

// Input Source Options
const inputSources = [
  {
    value: 'idea',
    name: '灵感创作',
    desc: '用几句话描述你的想法，AI 将生成脚本和分镜',
    icon: SparklesIcon,
    disabled: false,
  },
  {
    value: 'script',
    name: '脚本转视频',
    desc: '粘贴你的完整脚本，我们会自动拆分成分镜',
    icon: FileTextIcon,
    disabled: false,
  },
  {
    value: 'blog',
    name: '文章转视频',
    desc: '粘贴文章链接，我们会提取内容生成视频脚本',
    icon: LinkIcon,
    disabled: false,
  },
  {
    value: 'audio',
    name: '音频转视频',
    desc: '上传配音文件，我们会根据语音匹配画面',
    icon: MicIcon,
    disabled: true,
  },
]

// Computed
const inputLabel = computed(() => {
  const labels: Record<string, string> = {
    idea: '你的创意',
    script: '你的脚本',
    blog: '文章链接',
    audio: '音频文件',
  }
  return labels[form.source_type] || '你的创意'
})

const inputPlaceholder = computed(() => {
  const placeholders: Record<string, string> = {
    idea: '描述一个关于2050年AI如何改变东京城市规划的未来纪录片...',
    script: '在这里粘贴你的完整脚本内容...',
    blog: '粘贴文章URL，例如：https://example.com/article',
    audio: '点击上传音频文件...',
  }
  return placeholders[form.source_type] || ''
})

const isFormValid = computed(() => {
  return form.title.trim().length > 0 && form.story_text.trim().length >= 10
})

// Methods
function handleCancel() {
  router.back()
}

function showInspiration() {
  const ideas = [
    '一个关于时间旅行者回到过去拯救未来的科幻故事',
    '探索深海未知生物的纪录片风格视频',
    '一位年轻创业者从失败到成功的励志故事',
    '解释量子计算原理的趣味科普视频',
    '展示中国传统节日习俗的文化纪录片',
  ]
  const randomIdea = ideas[Math.floor(Math.random() * ideas.length)]
  form.story_text = randomIdea
  ElMessage.success('已为你生成灵感！')
}

function saveDraft() {
  // TODO: Implement draft saving
  ElMessage.info('草稿保存功能即将推出')
}

async function handleSubmit() {
  if (!isFormValid.value) {
    ElMessage.warning('请填写项目标题和内容')
    return
  }

  loading.value = true
  try {
    const project = await projectStore.create({
      title: form.title,
      story_text: form.story_text,
      description: form.description,
    })
    ElMessage.success('项目创建成功！')
    router.push(`/projects/${project.id}`)
  } catch (error) {
    const err = error as Error
    ElMessage.error(err.message || '创建失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* CSS Variables */
.create-project-page {
  --bg-app: #F9FAFB;
  --bg-white: #FFFFFF;
  --text-primary: #111827;
  --text-secondary: #6B7280;
  --text-muted: #9CA3AF;
  --border-subtle: #E5E7EB;
  --border-hover: #CBD5E1;
  --primary: #4F46E5;
  --primary-light: #EEF2FF;
  --primary-dark: #4338CA;
  
  min-height: 100vh;
  background-color: var(--bg-app);
  display: flex;
}

/* Main Content */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  position: relative;
  overflow-y: auto;
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Top Bar */
.top-bar {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  position: sticky;
  top: 0;
  background: rgba(249, 250, 251, 0.9);
  backdrop-filter: blur(8px);
  z-index: 20;
}

.cancel-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  background: none;
  border: none;
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  transition: color 0.2s;
}

.cancel-btn:hover {
  color: var(--text-primary);
}

.cancel-btn .icon-wrapper {
  padding: 4px;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.cancel-btn:hover .icon-wrapper {
  background-color: #E5E7EB;
}

.step-indicator {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-muted);
  font-family: 'JetBrains Mono', monospace;
}

.step-current {
  color: var(--primary);
  font-weight: 700;
}

/* Form Container */
.form-container {
  flex: 1;
  width: 100%;
  max-width: 768px;
  margin: 0 auto;
  padding: 32px 32px 120px;
}

.form-header {
  text-align: center;
  margin-bottom: 40px;
}

.form-header h1 {
  font-size: 30px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.025em;
  margin-bottom: 12px;
}

.form-header p {
  font-size: 16px;
  color: var(--text-secondary);
}

/* Form Sections */
.create-form {
  display: flex;
  flex-direction: column;
  gap: 48px;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.section-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

/* Input Group */
.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-group label {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  transition: color 0.2s;
}

.input-group.focused label {
  color: var(--primary);
}

.input-group input {
  width: 100%;
  background: var(--bg-white);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  padding: 12px 16px;
  font-size: 18px;
  font-weight: 500;
  color: var(--text-primary);
  outline: none;
  transition: all 0.2s;
}

.input-group input::placeholder {
  color: #D1D5DB;
}

.input-group input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.1);
}

/* Ratio Grid */
.ratio-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

/* Option Card */
.option-card {
  position: relative;
  background: var(--bg-white);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.option-card:hover {
  border-color: var(--border-hover);
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.03), 0 4px 6px -4px rgba(0, 0, 0, 0.02);
}

.option-card.selected {
  border-color: var(--primary);
  background-color: var(--primary-light);
  box-shadow: 0 0 0 2px var(--primary), 0 4px 6px -1px rgba(79, 70, 229, 0.1);
}

/* Ratio Preview */
.ratio-grid .option-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.ratio-preview {
  border: 2px solid var(--text-muted);
  border-radius: 4px;
  transition: border-color 0.2s;
}

.option-card:hover .ratio-preview,
.option-card.selected .ratio-preview {
  border-color: var(--text-secondary);
}

.ratio-info {
  text-align: center;
}

.ratio-name {
  display: block;
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
}

.ratio-desc {
  display: block;
  font-size: 10px;
  color: var(--text-muted);
  margin-top: 2px;
}

.check-icon {
  position: absolute;
  top: 12px;
  right: 12px;
  color: var(--primary);
}

/* Divider */
.divider {
  height: 1px;
  background: var(--border-subtle);
  width: 100%;
}

/* Source Grid */
.source-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.source-card {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
}

.source-card.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.source-card.disabled:hover {
  transform: none;
  box-shadow: none;
  border-color: var(--border-subtle);
}

.icon-box {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: #F3F4F6;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.icon-box.active {
  background: var(--primary);
  color: white;
}

.source-info {
  flex: 1;
  min-width: 0;
}

.source-info h3 {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.source-info p {
  font-size: 12px;
  color: var(--text-secondary);
  margin: 4px 0 0;
  line-height: 1.5;
}

.radio-icon {
  position: absolute;
  top: 16px;
  right: 16px;
  color: var(--text-muted);
}

.source-card.selected .radio-icon {
  color: var(--primary);
}

.coming-soon {
  position: absolute;
  top: 8px;
  right: 8px;
  font-size: 10px;
  font-weight: 600;
  color: var(--text-muted);
  background: #F3F4F6;
  padding: 2px 8px;
  border-radius: 4px;
}

/* Input Area */
.input-area {
  padding-top: 8px;
}

.inspiration-link {
  color: var(--primary);
  cursor: pointer;
  font-weight: 600;
  text-transform: none;
  letter-spacing: 0;
  font-size: 12px;
}

.inspiration-link:hover {
  color: var(--primary-dark);
}

.textarea-wrapper {
  position: relative;
}

.textarea-wrapper textarea {
  width: 100%;
  height: 128px;
  background: var(--bg-white);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  padding: 16px;
  font-size: 14px;
  font-family: 'JetBrains Mono', monospace;
  color: var(--text-primary);
  resize: none;
  outline: none;
  transition: all 0.2s;
}

.textarea-wrapper textarea::placeholder {
  color: var(--text-muted);
}

.textarea-wrapper textarea:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.1);
}

.char-count {
  position: absolute;
  bottom: 12px;
  right: 12px;
  font-size: 12px;
  font-family: 'JetBrains Mono', monospace;
  color: var(--text-muted);
  transition: color 0.2s;
}

.textarea-wrapper.focused .char-count {
  color: var(--primary);
}

/* Bottom Bar */
.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--bg-white);
  border-top: 1px solid var(--border-subtle);
  padding: 16px;
  z-index: 30;
}

.bottom-content {
  max-width: 768px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.credit-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-secondary);
}

.credit-info svg {
  color: var(--text-muted);
}

.credit-info strong {
  font-weight: 600;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-secondary {
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  background: none;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  color: var(--text-primary);
  background: #F3F4F6;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 700;
  color: white;
  background: var(--primary);
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 0 20px -5px rgba(99, 102, 241, 0.4);
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-dark);
}

.btn-primary:active:not(:disabled) {
  transform: scale(0.95);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  box-shadow: none;
}

/* Responsive */
@media (max-width: 768px) {
  .ratio-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
  }
  
  .source-grid {
    grid-template-columns: 1fr;
  }
  
  .form-container {
    padding: 16px 16px 120px;
  }
  
  .top-bar {
    padding: 0 16px;
  }
  
  .bottom-content {
    flex-direction: column;
    gap: 12px;
  }
  
  .action-buttons {
    width: 100%;
  }
  
  .btn-primary,
  .btn-secondary {
    flex: 1;
    justify-content: center;
  }
}
</style>
