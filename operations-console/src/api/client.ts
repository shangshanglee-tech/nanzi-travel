const csrfToken = document.querySelector<HTMLMetaElement>('meta[name="csrf-token"]')?.content ?? "";

export class OperationsApiError extends Error {
  constructor(message: string, public readonly status: number) {
    super(message);
  }
}

export async function operationsRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Accept", "application/json");
  if (options.method && options.method !== "GET") {
    headers.set("X-CSRFToken", csrfToken);
  }

  const response = await fetch(`/api/admin/v1/${path}`, {
    credentials: "same-origin",
    ...options,
    headers
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new OperationsApiError(body.detail ?? "请求未能完成", response.status);
  }
  return response.status === 204 ? (undefined as T) : response.json() as Promise<T>;
}
