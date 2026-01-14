<script setup lang="ts">
/**
 * 页面标题组件
 * 
 * 用法:
 * <PageHeader
 *   title="项目列表"
 *   description="管理您的所有视频项目"
 * >
 *   <el-button type="primary">新建</el-button>
 * </PageHeader>
 */

interface Props {
  /** 标题 */
  title: string
  /** 描述 */
  description?: string
  /** 是否显示返回按钮 */
  showBack?: boolean
}

withDefaults(defineProps<Props>(), {
  showBack: false,
})

const emit = defineEmits<{
  back: []
}>()
</script>

<template>
  <div class="page-header mb-8">
    <div class="flex items-start justify-between">
      <div class="flex items-start gap-4">
        <!-- 返回按钮 -->
        <button
          v-if="showBack"
          class="mt-1 p-2 rounded-lg text-slate-400 hover:text-slate-900 hover:bg-slate-100 transition-colors"
          @click="emit('back')"
        >
          <el-icon class="w-5 h-5">
            <ArrowLeft />
          </el-icon>
        </button>
        
        <div>
          <!-- 标题 -->
          <h1 class="text-2xl font-bold text-slate-900">
            {{ title }}
          </h1>
          
          <!-- 描述 -->
          <p v-if="description" class="text-slate-500 mt-1">
            {{ description }}
          </p>
        </div>
      </div>
      
      <!-- 操作区 -->
      <div class="flex items-center gap-3">
        <slot />
      </div>
    </div>
  </div>
</template>

