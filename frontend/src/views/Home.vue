<template>
  <div class="min-h-screen bg-slate-900">
    <!-- 导航 -->
    <header class="fixed top-0 left-0 right-0 z-50 bg-slate-900/80 backdrop-blur-xl border-b border-slate-800/50">
      <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <!-- Logo -->
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 bg-indigo-600 rounded-lg flex items-center justify-center">
            <el-icon class="w-5 h-5 text-white"><MagicStick /></el-icon>
          </div>
          <span class="text-xl font-bold text-white">StoryFlow</span>
        </div>
        
        <!-- 导航链接 -->
        <nav class="hidden md:flex items-center gap-8">
          <a href="#features" class="text-slate-400 hover:text-white transition-colors text-sm">功能</a>
          <a href="#pricing" class="text-slate-400 hover:text-white transition-colors text-sm">定价</a>
          <router-link to="/pricing" class="text-slate-400 hover:text-white transition-colors text-sm">方案</router-link>
        </nav>
        
        <!-- CTA -->
        <div class="flex items-center gap-4">
          <router-link
            v-if="!isLoggedIn"
            to="/login"
            class="text-slate-300 hover:text-white transition-colors text-sm font-medium"
          >
            登录
          </router-link>
          <router-link
            :to="isLoggedIn ? '/dashboard' : '/register'"
            class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors shadow-glow"
          >
            {{ isLoggedIn ? '进入工作台' : '免费开始' }}
          </router-link>
        </div>
      </div>
    </header>
    
    <!-- Hero Section -->
    <section class="relative min-h-screen flex items-center justify-center pt-20 overflow-hidden">
      <!-- 背景效果 -->
      <div class="absolute inset-0">
        <div class="absolute top-1/3 left-1/4 w-[500px] h-[500px] bg-indigo-600/20 rounded-full blur-[120px]" />
        <div class="absolute bottom-1/4 right-1/3 w-[400px] h-[400px] bg-purple-600/15 rounded-full blur-[100px]" />
        <div class="absolute top-1/2 right-1/4 w-[300px] h-[300px] bg-cyan-600/10 rounded-full blur-[80px]" />
      </div>
      
      <!-- 网格背景 -->
      <div class="absolute inset-0 bg-[linear-gradient(rgba(148,163,184,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(148,163,184,0.03)_1px,transparent_1px)] bg-[size:64px_64px]" />
      
      <!-- 内容 -->
      <div class="relative z-10 max-w-4xl mx-auto text-center px-6">
        <!-- 标签 -->
        <div class="inline-flex items-center gap-2 bg-slate-800/50 border border-slate-700/50 rounded-full px-4 py-1.5 mb-8">
          <span class="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
          <span class="text-sm text-slate-300">AI 驱动的下一代视频创作</span>
        </div>
        
        <!-- 主标题 -->
        <h1 class="text-5xl md:text-6xl lg:text-7xl font-bold text-white mb-6 leading-tight">
          故事变视频<br />
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">
            只需一键
          </span>
        </h1>
        
        <!-- 副标题 -->
        <p class="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto mb-10">
          输入您的故事文本，AI 自动生成分镜脚本、绘制画面、合成视频。
          让创意变成现实，前所未有地简单。
        </p>
        
        <!-- CTA 按钮 -->
        <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
          <router-link
            :to="isLoggedIn ? '/dashboard' : '/register'"
            class="group flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-4 rounded-xl text-lg font-semibold transition-all shadow-glow"
          >
            <span>{{ isLoggedIn ? '开始创作' : '免费试用' }}</span>
            <el-icon class="w-5 h-5 transition-transform group-hover:translate-x-1"><ArrowRight /></el-icon>
          </router-link>
          <a
            href="#demo"
            class="flex items-center gap-2 text-slate-300 hover:text-white px-6 py-4 rounded-xl text-lg font-medium transition-colors"
          >
            <el-icon class="w-5 h-5"><VideoPlay /></el-icon>
            <span>观看演示</span>
          </a>
        </div>
        
        <!-- 统计 -->
        <div class="flex items-center justify-center gap-12 mt-16">
          <div class="text-center">
            <div class="text-3xl font-bold text-white">10K+</div>
            <div class="text-sm text-slate-500">创作者</div>
          </div>
          <div class="w-px h-10 bg-slate-700" />
          <div class="text-center">
            <div class="text-3xl font-bold text-white">50K+</div>
            <div class="text-sm text-slate-500">视频生成</div>
          </div>
          <div class="w-px h-10 bg-slate-700" />
          <div class="text-center">
            <div class="text-3xl font-bold text-white">99.9%</div>
            <div class="text-sm text-slate-500">满意度</div>
          </div>
        </div>
      </div>
    </section>
    
    <!-- Features Section -->
    <section id="features" class="py-24 px-6">
      <div class="max-w-6xl mx-auto">
        <div class="text-center mb-16">
          <h2 class="text-3xl md:text-4xl font-bold text-white mb-4">
            强大功能，简单体验
          </h2>
          <p class="text-slate-400 max-w-xl mx-auto">
            我们将复杂的视频制作流程简化为三步，让每个人都能成为创作者
          </p>
        </div>
        
        <div class="grid md:grid-cols-3 gap-8">
          <!-- 功能卡片 1 -->
          <div class="group bg-slate-800/50 border border-slate-700/50 rounded-2xl p-8 hover:border-indigo-500/50 transition-colors">
            <div class="w-14 h-14 bg-indigo-600/20 rounded-xl flex items-center justify-center mb-6 group-hover:bg-indigo-600/30 transition-colors">
              <el-icon class="w-7 h-7 text-indigo-400"><Document /></el-icon>
            </div>
            <h3 class="text-xl font-semibold text-white mb-3">智能分镜</h3>
            <p class="text-slate-400 leading-relaxed">
              AI 分析您的故事文本，自动拆分场景、规划镜头、生成详细的分镜脚本
            </p>
          </div>
          
          <!-- 功能卡片 2 -->
          <div class="group bg-slate-800/50 border border-slate-700/50 rounded-2xl p-8 hover:border-purple-500/50 transition-colors">
            <div class="w-14 h-14 bg-purple-600/20 rounded-xl flex items-center justify-center mb-6 group-hover:bg-purple-600/30 transition-colors">
              <el-icon class="w-7 h-7 text-purple-400"><Picture /></el-icon>
            </div>
            <h3 class="text-xl font-semibold text-white mb-3">AI 绘图</h3>
            <p class="text-slate-400 leading-relaxed">
              根据分镜描述，AI 自动生成高质量的场景图片，支持多种艺术风格
            </p>
          </div>
          
          <!-- 功能卡片 3 -->
          <div class="group bg-slate-800/50 border border-slate-700/50 rounded-2xl p-8 hover:border-cyan-500/50 transition-colors">
            <div class="w-14 h-14 bg-cyan-600/20 rounded-xl flex items-center justify-center mb-6 group-hover:bg-cyan-600/30 transition-colors">
              <el-icon class="w-7 h-7 text-cyan-400"><VideoCamera /></el-icon>
            </div>
            <h3 class="text-xl font-semibold text-white mb-3">视频合成</h3>
            <p class="text-slate-400 leading-relaxed">
              将图片、配音、字幕自动合成为完整视频，一键导出高清成片
            </p>
          </div>
        </div>
      </div>
    </section>
    
    <!-- CTA Section -->
    <section class="py-24 px-6">
      <div class="max-w-4xl mx-auto text-center">
        <div class="bg-gradient-to-br from-indigo-600/20 to-purple-600/20 border border-indigo-500/30 rounded-3xl p-12 md:p-16">
          <h2 class="text-3xl md:text-4xl font-bold text-white mb-4">
            准备好开始创作了吗？
          </h2>
          <p class="text-slate-300 mb-8 max-w-lg mx-auto">
            免费注册即可获得初始配额，立即体验 AI 视频创作的魅力
          </p>
          <router-link
            :to="isLoggedIn ? '/dashboard' : '/register'"
            class="inline-flex items-center gap-2 bg-white text-slate-900 px-8 py-4 rounded-xl text-lg font-semibold hover:bg-slate-100 transition-colors"
          >
            <span>{{ isLoggedIn ? '进入工作台' : '免费开始' }}</span>
            <el-icon class="w-5 h-5"><ArrowRight /></el-icon>
          </router-link>
        </div>
      </div>
    </section>
    
    <!-- Footer -->
    <footer class="border-t border-slate-800 py-12 px-6">
      <div class="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
            <el-icon class="w-4 h-4 text-white"><MagicStick /></el-icon>
          </div>
          <span class="text-lg font-bold text-white">StoryFlow</span>
        </div>
        <p class="text-slate-500 text-sm">
          © 2025 StoryFlow. All rights reserved.
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import {
  MagicStick, ArrowRight, VideoPlay, Document, Picture, VideoCamera
} from '@element-plus/icons-vue'
import { useAuth } from '@/composables/useAuth'

const { isLoggedIn } = useAuth()
</script>

<style scoped>
.shadow-glow {
  box-shadow: 0 0 30px -5px rgba(79, 70, 229, 0.5);
}
</style>
