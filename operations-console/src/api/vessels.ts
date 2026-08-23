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
export interface VesselPageBlockImage { id: number; image: string; sort_order: number; }
export interface VesselPageBlock { id: number; block_type: "heading" | "card"; title: string; image: string; body: string; sort_order: number; additional_images: VesselPageBlockImage[]; }
export interface Cabin { id: number; name: string; official_code?: string; official_name?: string; category?: string; size_sqm?: string | number | null; bed_layout?: string; view_type?: string; summary?: string; description_zh?: string; description_en?: string; max_guests?: number | null; deck?: string; amenities?: string[]; display_tags?: string[]; is_accessible: boolean; is_visible: boolean; highlights?: string[]; image?: string; sort_order: number; }
export interface CabinGroup { id: number; slug: string; title_zh: string; title_en?: string; is_visible: boolean; sort_order: number; cabin_ids: number[]; }
export interface DeckPlan { id: number; title: string; image: string; sort_order: number; }

export const listVessels = () => operationsRequest<{ results: Vessel[] }>("vessels");
export const createVessel = (data: Partial<VesselInput>) => operationsRequest<Vessel>("vessels", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) });
export const getVessel = (id: string) => operationsRequest<Vessel>(`vessels/${id}`);
export const updateVessel = (id: number, data: Partial<VesselInput>) => operationsRequest<Vessel>(`vessels/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) });
export const uploadVesselCardImage = (id: number, image: File) => {
  const formData = new FormData();
  formData.append("image", image);
  return operationsRequest<Vessel>(`vessels/${id}/card-image`, { method: "POST", body: formData });
};
export const useVesselCardMediaAsset = (id: number, assetId: number) => operationsRequest<Vessel>(`vessels/${id}/card-image`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ asset_id: assetId }) });
export const listVesselPageBlocks = (id: number) => operationsRequest<{ results: VesselPageBlock[] }>(`vessels/${id}/page-blocks`);
export const createVesselPageBlock = (id: number, input: Pick<VesselPageBlock, "block_type" | "title" | "body">, image?: File, assetId?: number) => {
  const formData = new FormData(); formData.append("block_type", input.block_type); formData.append("title", input.title); formData.append("body", input.body ?? ""); if (image) formData.append("image", image); if (assetId) formData.append("asset_id", String(assetId));
  return operationsRequest<VesselPageBlock>(`vessels/${id}/page-blocks`, { method: "POST", body: formData });
};
export const updateVesselPageBlock = (id: number, blockId: number, input: Partial<Pick<VesselPageBlock, "block_type" | "title" | "body">>) => operationsRequest<VesselPageBlock>(`vessels/${id}/page-blocks/${blockId}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(input) });
export const deleteVesselPageBlock = (id: number, blockId: number) => operationsRequest<void>(`vessels/${id}/page-blocks/${blockId}`, { method: "DELETE" });
export const reorderVesselPageBlocks = (id: number, ids: number[]) => operationsRequest<{ results: VesselPageBlock[] }>(`vessels/${id}/page-blocks/order`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ids }) });
export const uploadVesselPageBlockImage = (id: number, blockId: number, image: File) => { const formData = new FormData(); formData.append("image", image); return operationsRequest<VesselPageBlockImage>(`vessels/${id}/page-blocks/${blockId}/images`, { method: "POST", body: formData }); };
export const useVesselPageBlockMediaAsset = (id: number, blockId: number, assetId: number) => operationsRequest<VesselPageBlockImage>(`vessels/${id}/page-blocks/${blockId}/images`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ asset_id: assetId }) });
export const deleteVesselPageBlockImage = (id: number, blockId: number, imageId: number) => operationsRequest<void>(`vessels/${id}/page-blocks/${blockId}/images/${imageId}`, { method: "DELETE" });
export const listCabins = (id: number) => operationsRequest<{ results: Cabin[] }>(`vessels/${id}/cabins`);
export const createCabin = (id: number, data: Omit<Partial<Cabin>, "id" | "image" | "sort_order">) => operationsRequest<Cabin>(`vessels/${id}/cabins`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) });
export const updateCabin = (id: number, cabinId: number, data: Omit<Partial<Cabin>, "id" | "image" | "sort_order">) => operationsRequest<Cabin>(`vessels/${id}/cabins/${cabinId}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) });
export const deleteCabin = (id: number, cabinId: number) => operationsRequest<void>(`vessels/${id}/cabins/${cabinId}`, { method: "DELETE" });
export const uploadCabinImage = (id: number, cabinId: number, image: File) => { const formData = new FormData(); formData.append("image", image); return operationsRequest<Cabin>(`vessels/${id}/cabins/${cabinId}/image`, { method: "POST", body: formData }); };
export const useCabinMediaAsset = (id: number, cabinId: number, assetId: number) => operationsRequest<Cabin>(`vessels/${id}/cabins/${cabinId}/image`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ asset_id: assetId }) });
export const listCabinGroups = (id: number) => operationsRequest<{ results: CabinGroup[] }>(`vessels/${id}/cabin-groups`);
export const createCabinGroup = (id: number, data: Omit<Partial<CabinGroup>, "id" | "sort_order">) => operationsRequest<CabinGroup>(`vessels/${id}/cabin-groups`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) });
export const listDeckPlans = (id: number) => operationsRequest<{ results: DeckPlan[] }>(`vessels/${id}/deck-plans`);
export const createDeckPlan = (id: number, title: string, image: File) => { const formData = new FormData(); formData.append("title", title); formData.append("image", image); return operationsRequest<DeckPlan>(`vessels/${id}/deck-plans`, { method: "POST", body: formData }); };
export const deleteDeckPlan = (id: number, deckId: number) => operationsRequest<void>(`vessels/${id}/deck-plans/${deckId}`, { method: "DELETE" });
