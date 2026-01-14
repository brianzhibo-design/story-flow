/**
 * 项目状态管理
 * 
 * 功能:
 * - 项目列表管理
 * - 当前项目状态
 * - 分镜和任务状态
 * - 分页支持
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { projectsApi, tasksApi } from '@/api'
import type { 
  Project, 
  Scene, 
  Task,
  CreateProjectParams,
  UpdateProjectParams,
  UpdateSceneParams,
  ListProjectsParams,
} from '@/api'

export const useProjectStore = defineStore('project', () => {
  // ==================== 状态 ====================
  
  /** 项目列表 */
  const projects = ref<Project[]>([])
  
  /** 当前编辑的项目 */
  const currentProject = ref<Project | null>(null)
  
  /** 当前项目的分镜列表 */
  const scenes = ref<Scene[]>([])
  
  /** 当前项目的任务列表 */
  const tasks = ref<Task[]>([])
  
  /** 加载状态 */
  const loading = ref(false)
  
  /** 分页信息 */
  const pagination = ref({
    page: 1,
    page_size: 20,
    total: 0,
    total_pages: 0,
  })
  
  // ==================== 计算属性 ====================
  
  /** 当前项目是否正在处理 */
  const isProcessing = computed(() => currentProject.value?.status === 'processing')
  
  /** 已完成的分镜 */
  const completedScenes = computed(() => scenes.value.filter(s => s.status === 'completed'))
  
  /** 生成进度 (百分比) */
  const progress = computed(() => {
    if (scenes.value.length === 0) return 0
    return Math.round((completedScenes.value.length / scenes.value.length) * 100)
  })
  
  /** 当前运行中的任务 */
  const runningTask = computed(() => tasks.value.find(t => t.status === 'running'))
  
  /** 待处理的任务 */
  const pendingTasks = computed(() => 
    tasks.value.filter(t => t.status === 'pending' || t.status === 'queued')
  )
  
  // ==================== 方法 ====================
  
  /**
   * 获取项目列表
   */
  async function fetchProjects(params?: ListProjectsParams) {
    loading.value = true
    try {
      const { items, pagination: pag } = await projectsApi.list({
        page: params?.page ?? pagination.value.page,
        page_size: params?.page_size ?? pagination.value.page_size,
        status: params?.status,
        keyword: params?.keyword,
      })
      projects.value = items
      pagination.value = pag
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 获取项目详情
   */
  async function fetchProject(id: string) {
    loading.value = true
    try {
      const data = await projectsApi.detail(id)
      currentProject.value = data
      scenes.value = data.scenes || []
      
      // 同时获取任务列表
      await fetchTasks(id)
      
      return data
    } finally {
      loading.value = false
    }
  }
  
  /**
   * 获取项目任务列表
   */
  async function fetchTasks(projectId: string) {
    try {
      tasks.value = await tasksApi.list(projectId)
    } catch (error) {
      console.error('Failed to fetch tasks:', error)
    }
  }
  
  /**
   * 创建项目
   */
  async function create(params: CreateProjectParams) {
    const data = await projectsApi.create(params)
    projects.value.unshift(data)
    return data
  }
  
  /**
   * 更新项目
   */
  async function update(id: string, params: UpdateProjectParams) {
    const data = await projectsApi.update(id, params)
    
    // 更新列表中的项目
    const index = projects.value.findIndex(p => p.id === id)
    if (index !== -1) {
      projects.value[index] = data
    }
    
    // 更新当前项目
    if (currentProject.value?.id === id) {
      currentProject.value = data
    }
    
    return data
  }
  
  /**
   * 删除项目
   */
  async function remove(id: string) {
    await projectsApi.delete(id)
    projects.value = projects.value.filter(p => p.id !== id)
    
    if (currentProject.value?.id === id) {
      currentProject.value = null
    }
  }
  
  /**
   * 触发生成
   */
  async function generate(id: string, steps?: string[]) {
    const { task_id } = await projectsApi.generate(id, steps)
    
    // 更新项目状态
    if (currentProject.value?.id === id) {
      currentProject.value.status = 'processing'
    }
    
    return task_id
  }
  
  /**
   * 更新分镜
   */
  async function updateSceneApi(sceneId: string, params: UpdateSceneParams) {
    const updatedScene = await projectsApi.updateScene(sceneId, params)
    
    const index = scenes.value.findIndex(s => s.id === sceneId)
    if (index !== -1) {
      scenes.value[index] = updatedScene
    }
    
    return updatedScene
  }
  
  /**
   * 重排分镜顺序
   */
  async function reorderScenes(projectId: string, sceneIds: string[]) {
    await projectsApi.reorderScenes(projectId, sceneIds)
    
    // 重新排序本地数据
    const reordered = sceneIds
      .map(id => scenes.value.find(s => s.id === id))
      .filter((s): s is Scene => !!s)
      .map((s, index) => ({ ...s, scene_index: index + 1 }))
    
    scenes.value = reordered
  }
  
  /**
   * 重新生成分镜图片
   */
  async function regenerateImage(sceneId: string) {
    const { task_id } = await projectsApi.regenerateImage(sceneId)
    
    // 更新分镜状态
    const index = scenes.value.findIndex(s => s.id === sceneId)
    if (index !== -1) {
      scenes.value[index].status = 'generating'
    }
    
    return task_id
  }
  
  /**
   * 重新生成分镜视频
   */
  async function regenerateVideo(sceneId: string) {
    const { task_id } = await projectsApi.regenerateVideo(sceneId)
    
    // 更新分镜状态
    const index = scenes.value.findIndex(s => s.id === sceneId)
    if (index !== -1) {
      scenes.value[index].status = 'generating'
    }
    
    return task_id
  }
  
  /**
   * 取消任务
   */
  async function cancelTask(taskId: string) {
    await tasksApi.cancel(taskId)
    
    const index = tasks.value.findIndex(t => t.id === taskId)
    if (index !== -1) {
      tasks.value[index].status = 'failed'
    }
  }
  
  /**
   * 重试任务
   */
  async function retryTask(taskId: string) {
    const { task_id } = await tasksApi.retry(taskId)
    return task_id
  }
  
  /**
   * 更新分镜（用于 WebSocket 推送）
   */
  function updateScene(sceneId: string, updates: Partial<Scene>) {
    const index = scenes.value.findIndex(s => s.id === sceneId)
    if (index !== -1) {
      scenes.value[index] = { ...scenes.value[index], ...updates }
    }
  }
  
  /**
   * 更新任务（用于 WebSocket 推送）
   */
  function updateTask(taskId: string, updates: Partial<Task>) {
    const index = tasks.value.findIndex(t => t.id === taskId)
    if (index !== -1) {
      tasks.value[index] = { ...tasks.value[index], ...updates }
    } else {
      tasks.value.push(updates as Task)
    }
  }
  
  /**
   * 添加任务
   */
  function addTask(task: Task) {
    const existing = tasks.value.find(t => t.id === task.id)
    if (!existing) {
      tasks.value.push(task)
    }
  }
  
  /**
   * 清除当前项目状态
   */
  function clearCurrent() {
    currentProject.value = null
    scenes.value = []
    tasks.value = []
  }
  
  /**
   * 重置所有状态
   */
  function reset() {
    projects.value = []
    currentProject.value = null
    scenes.value = []
    tasks.value = []
    pagination.value = {
      page: 1,
      page_size: 20,
      total: 0,
      total_pages: 0,
    }
  }
  
  return {
    // 状态
    projects,
    currentProject,
    scenes,
    tasks,
    loading,
    pagination,
    
    // 计算属性
    isProcessing,
    completedScenes,
    progress,
    runningTask,
    pendingTasks,
    
    // 方法
    fetchProjects,
    fetchProject,
    fetchTasks,
    create,
    update,
    remove,
    generate,
    updateSceneApi,
    reorderScenes,
    regenerateImage,
    regenerateVideo,
    cancelTask,
    retryTask,
    updateScene,
    updateTask,
    addTask,
    clearCurrent,
    reset,
  }
})
