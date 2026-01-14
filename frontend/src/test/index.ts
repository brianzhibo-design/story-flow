/**
 * 测试工具统一导出
 */

// 工具函数
export {
  generateId,
  resetIdCounter,
  createMockUser,
  createMockProject,
  createMockScene,
  createMockTask,
  createTestRouter,
  createTestPinia,
  mountComponent,
  shallowMountComponent,
  flushPromises,
  wait,
  waitFor,
  expectElementExists,
  expectElementNotExists,
  expectTextContent,
  typeInput,
  clickElement,
  submitForm,
} from './utils'

// API Mocks
export {
  mockAuthApi,
  mockProjectsApi,
  mockTasksApi,
  mockQuotaApi,
  apiMocks,
  resetAllMocks,
  mockApiError,
  mockLoggedInUser,
  mockLoggedOutUser,
} from './mocks/api'

