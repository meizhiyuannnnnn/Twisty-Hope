// 通用 API 响应类型
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

// 分页响应
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
