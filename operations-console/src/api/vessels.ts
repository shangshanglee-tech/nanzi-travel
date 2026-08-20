import { operationsRequest } from "./client";

export interface VesselInput {
  slug: string; name: string; official_name?: string; summary?: string; intro_zh?: string; operator_name?: string;
  card_tone?: string; capacity?: number | null; year_built?: number | null; year_refurbished?: number | null;
  content_status: "draft" | "published"; is_active: boolean; show_cabins: boolean; show_deck_plans: boolean; sort_order?: number;
  is_hybrid: boolean; has_science_center: boolean; has_wifi: boolean; has_stabilization_system: boolean;
  restaurant_count: number; bar_count: number; has_fitness_center: boolean; heated_pool_count: number;
  has_infinity_pool: boolean; has_sauna: boolean; has_executive_lounge: boolean;
}

export interface Vessel extends VesselInput { id: number; card_image?: string; published_at?: string | null; }

export const listVessels = () => operationsRequest<{ results: Vessel[] }>("vessels");
export const getVessel = (id: string) => operationsRequest<Vessel>(`vessels/${id}`);
export const updateVessel = (id: number, data: Partial<VesselInput>) => operationsRequest<Vessel>(`vessels/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) });
export const uploadVesselCardImage = (id: number, image: File) => {
  const formData = new FormData();
  formData.append("image", image);
  return operationsRequest<Vessel>(`vessels/${id}/card-image`, { method: "POST", body: formData });
};
