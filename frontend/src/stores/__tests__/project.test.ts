/**
 * Project Store 单元测试
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useProjectStore } from '@/stores/project'
import { createMockProject, createMockScene, resetAllMocks } from '@/test'

// Mock API 模块
vi.mock('@/api', () => ({
  projectsApi: {
    list: vi.fn(),
    detail: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    generate: vi.fn(),
    getScenes: vi.fn(),
    updateScene: vi.fn(),
    reorderScenes: vi.fn(),
    regenerateImage: vi.fn(),
    regenerateVideo: vi.fn(),
  },
  tasksApi: {
    list: vi.fn(),
    detail: vi.fn(),
    cancel: vi.fn(),
    retry: vi.fn(),
  },
}))

import { projectsApi, tasksApi } from '@/api'

describe('Project Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    resetAllMocks()
    vi.clearAllMocks()
  })

  describe('初始状态', () => {
    it('应该有正确的初始状态', () => {
      const store = useProjectStore()

      expect(store.projects).toEqual([])
      expect(store.currentProject).toBeNull()
      expect(store.scenes).toEqual([])
      expect(store.tasks).toEqual([])
      expect(store.loading).toBe(false)
    })
  })

  describe('fetchProjects', () => {
    it('应该获取项目列表', async () => {
      const store = useProjectStore()
      const mockProjects = [
        createMockProject({ id: '1', title: 'Project 1' }),
        createMockProject({ id: '2', title: 'Project 2' }),
      ]

      vi.mocked(projectsApi.list).mockResolvedValueOnce({
        items: mockProjects,
        pagination: { page: 1, page_size: 20, total: 2, total_pages: 1 },
      })

      await store.fetchProjects()

      expect(store.projects).toEqual(mockProjects)
      expect(store.pagination.total).toBe(2)
    })

    it('获取项目时应该显示加载状态', async () => {
      const store = useProjectStore()

      vi.mocked(projectsApi.list).mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve({
          items: [],
          pagination: { page: 1, page_size: 20, total: 0, total_pages: 0 },
        }), 100))
      )

      const promise = store.fetchProjects()
      expect(store.loading).toBe(true)

      await promise
      expect(store.loading).toBe(false)
    })
  })

  describe('fetchProject', () => {
    it('应该获取单个项目详情', async () => {
      const store = useProjectStore()
      const mockProject = createMockProject({ id: 'test-id' })
      const mockScenes = [
        createMockScene({ id: 'scene-1', scene_index: 1 }),
        createMockScene({ id: 'scene-2', scene_index: 2 }),
      ]

      vi.mocked(projectsApi.detail).mockResolvedValueOnce({
        ...mockProject,
        scenes: mockScenes,
      })

      vi.mocked(tasksApi.list).mockResolvedValueOnce([])

      await store.fetchProject('test-id')

      expect(store.currentProject).toMatchObject({ id: 'test-id' })
      expect(store.scenes).toEqual(mockScenes)
    })
  })

  describe('create', () => {
    it('应该创建新项目', async () => {
      const store = useProjectStore()
      const newProject = createMockProject({ title: 'New Project' })

      vi.mocked(projectsApi.create).mockResolvedValueOnce(newProject)

      const result = await store.create({
        title: 'New Project',
        story_text: 'Once upon a time...',
      })

      expect(result).toEqual(newProject)
      expect(store.projects).toContainEqual(newProject)
    })
  })

  describe('update', () => {
    it('应该更新项目', async () => {
      const store = useProjectStore()
      const existingProject = createMockProject({ id: 'test-id', title: 'Old Title' })
      const updatedProject = { ...existingProject, title: 'New Title' }

      store.projects = [existingProject]

      vi.mocked(projectsApi.update).mockResolvedValueOnce(updatedProject)

      await store.update('test-id', { title: 'New Title' })

      expect(store.projects[0].title).toBe('New Title')
    })

    it('应该更新当前项目', async () => {
      const store = useProjectStore()
      const existingProject = createMockProject({ id: 'test-id', title: 'Old Title' })
      const updatedProject = { ...existingProject, title: 'New Title' }

      store.currentProject = existingProject

      vi.mocked(projectsApi.update).mockResolvedValueOnce(updatedProject)

      await store.update('test-id', { title: 'New Title' })

      expect(store.currentProject?.title).toBe('New Title')
    })
  })

  describe('remove', () => {
    it('应该删除项目', async () => {
      const store = useProjectStore()
      const project1 = createMockProject({ id: 'project-1' })
      const project2 = createMockProject({ id: 'project-2' })

      store.projects = [project1, project2]

      vi.mocked(projectsApi.delete).mockResolvedValueOnce(undefined)

      await store.remove('project-1')

      expect(store.projects).toHaveLength(1)
      expect(store.projects[0].id).toBe('project-2')
    })

    it('删除当前项目时应该清除 currentProject', async () => {
      const store = useProjectStore()
      const project = createMockProject({ id: 'test-id' })

      store.projects = [project]
      store.currentProject = project

      vi.mocked(projectsApi.delete).mockResolvedValueOnce(undefined)

      await store.remove('test-id')

      expect(store.currentProject).toBeNull()
    })
  })

  describe('generate', () => {
    it('应该触发项目生成', async () => {
      const store = useProjectStore()
      const project = createMockProject({ id: 'test-id', status: 'draft' })

      store.currentProject = project

      vi.mocked(projectsApi.generate).mockResolvedValueOnce({ task_id: 'task-123' })

      const taskId = await store.generate('test-id')

      expect(taskId).toBe('task-123')
      expect(store.currentProject?.status).toBe('processing')
    })
  })

  describe('updateScene', () => {
    it('应该更新场景状态', () => {
      const store = useProjectStore()
      const scene = createMockScene({ id: 'scene-1', status: 'pending' })

      store.scenes = [scene]

      store.updateScene('scene-1', { status: 'completed', image_url: 'http://example.com/image.jpg' })

      expect(store.scenes[0].status).toBe('completed')
      expect(store.scenes[0].image_url).toBe('http://example.com/image.jpg')
    })
  })

  describe('progress', () => {
    it('应该计算正确的进度', () => {
      const store = useProjectStore()
      store.scenes = [
        createMockScene({ status: 'completed' }),
        createMockScene({ status: 'completed' }),
        createMockScene({ status: 'pending' }),
        createMockScene({ status: 'pending' }),
      ]

      expect(store.progress).toBe(50)
    })

    it('没有场景时进度应该为 0', () => {
      const store = useProjectStore()
      store.scenes = []

      expect(store.progress).toBe(0)
    })
  })

  describe('clearCurrent', () => {
    it('应该清除当前项目状态', () => {
      const store = useProjectStore()
      store.currentProject = createMockProject()
      store.scenes = [createMockScene()]
      store.tasks = [{
        id: 'task-1',
        project_id: 'p1',
        scene_id: null,
        type: 'storyboard',
        status: 'completed',
        progress: 100,
        progress_message: null,
        error_message: null,
        created_at: '',
      }]

      store.clearCurrent()

      expect(store.currentProject).toBeNull()
      expect(store.scenes).toEqual([])
      expect(store.tasks).toEqual([])
    })
  })

  describe('cancelTask', () => {
    it('应该取消任务', async () => {
      const store = useProjectStore()
      store.tasks = [{
        id: 'task-1',
        project_id: 'p1',
        scene_id: null,
        type: 'image',
        status: 'running',
        progress: 50,
        progress_message: null,
        error_message: null,
        created_at: '',
      }]

      vi.mocked(tasksApi.cancel).mockResolvedValueOnce(undefined)

      await store.cancelTask('task-1')

      expect(store.tasks[0].status).toBe('failed')
    })
  })
})
