<script setup lang="ts">
/**
 * 元数据标签组件
 * 
 * 用法:
 * <MetaTag icon="Camera" text="Close-up" />
 * <MetaTag icon="Sun" text="Natural Light" />
 */

interface Props {
  /** 图标名称 */
  icon?: string
  /** 文本内容 */
  text: string
  /** 是否可点击 */
  clickable?: boolean
}

withDefaults(defineProps<Props>(), {
  clickable: false,
})

const emit = defineEmits<{
  click: []
}>()
</script>

<template>
  <span
    :class="[
      'meta-tag inline-flex items-center gap-1.5',
      'text-[11px] font-medium text-slate-500',
      'bg-slate-100 px-2 py-1 rounded-md',
      'transition-colors duration-200',
      { 'cursor-pointer hover:bg-slate-200 hover:text-slate-700': clickable },
    ]"
    @click="clickable && emit('click')"
  >
    <el-icon v-if="icon" class="w-3 h-3">
      <component :is="icon" />
    </el-icon>
    <span>{{ text }}</span>
  </span>
</template>

<style scoped>
.meta-tag {
  white-space: nowrap;
}
</style>

