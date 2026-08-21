import { operationsRequest } from "./client";

export interface ActivityImage { id: number; image: string; alt_text: string; sort_order: number; }
export interface ActivityInput { title: string; content?: string; destination_id: number; status: "draft" | "published"; sort_order?: number; }
export interface Activity extends ActivityInput { id: number; hero_image?: string; images?: ActivityImage[]; }
export const listActivities = () => operationsRequest<{ results: Activity[] }>("activities");
export const getActivity = (id: string) => operationsRequest<Activity>(`activities/${id}`);
export const createActivity = (data: ActivityInput) => operationsRequest<Activity>("activities", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) });
export const updateActivity = (id: number, data: Partial<ActivityInput>) => operationsRequest<Activity>(`activities/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) });
export const deleteActivity = (id: number) => operationsRequest<void>(`activities/${id}`, { method: "DELETE" });
export const uploadActivityHero = (id: number, image: File) => { const body = new FormData(); body.append("image", image); return operationsRequest<Activity>(`activities/${id}/hero-image`, { method: "POST", body }); };
export const uploadActivityImage = (id: number, image: File, altText: string) => { const body = new FormData(); body.append("image", image); body.append("alt_text", altText); return operationsRequest<ActivityImage>(`activities/${id}/images`, { method: "POST", body }); };
export const deleteActivityImage = (id: number, imageId: number) => operationsRequest<void>(`activities/${id}/images/${imageId}`, { method: "DELETE" });
