import { operationsRequest } from "./client";

export interface MediaAsset { id: number; image: string; title: string; tags: string[]; created_at: string; }

export const listMediaAssets = (query = "") => operationsRequest<{ results: MediaAsset[] }>(`media-assets${query ? `?q=${encodeURIComponent(query)}` : ""}`);
export const uploadMediaAsset = (image: File, title: string, tags: string) => {
  const formData = new FormData();
  formData.append("image", image);
  formData.append("title", title);
  formData.append("tags", tags);
  return operationsRequest<MediaAsset>("media-assets", { method: "POST", body: formData });
};
export const updateMediaAsset = (id: number, title: string, tags: string[]) => operationsRequest<MediaAsset>(`media-assets/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ title, tags }) });
