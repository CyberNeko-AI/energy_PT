const BASE = '/api';

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`请求失败: ${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}
