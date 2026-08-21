import { operationsRequest } from "./client";

export interface ProductDeparture { id?: number; label: string; start_date?: string; end_date?: string; vessel_id?: number | null; consultation_status: string; }
export interface ItineraryDay { id?: number; day_number: number; source_range?: string; title: string; description: string; accommodation?: string; meals?: string; }
export interface ProductImage { id: number; image: string; alt_text: string; sort_order: number; }
export interface ProductInput {
  title: string; slug: string; subtitle?: string; summary?: string; season?: string; duration_days?: number | null;
  vessel?: string; departure_city?: string; tags?: string[]; highlights?: string[]; included?: string[]; excluded?: string[];
  suitable_for?: string[]; notices?: string[]; status: string; sort_order?: number; destination_id: number; vessel_ids?: number[];
  activity_ids?: number[];
  departures?: ProductDeparture[]; itinerary_days?: ItineraryDay[];
}
export interface Product extends ProductInput { id: number; published_at?: string | null; hero_image?: string; images?: ProductImage[]; }
export const listProducts = () => operationsRequest<{ results: Product[] }>("products");
export const getProduct = (id: string) => operationsRequest<Product>(`products/${id}`);
export const createProduct = (data: ProductInput) => operationsRequest<Product>("products", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) });
export const updateProduct = (id: number, data: Partial<ProductInput>) => operationsRequest<Product>(`products/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) });
export const deleteProduct = (id: number) => operationsRequest<void>(`products/${id}`, { method: "DELETE" });
export const listVesselOptions = () => operationsRequest<{ results: Array<{ id: number; name: string }> }>("vessel-options");
export const uploadProductHero = (id: number, image: File) => {
  const formData = new FormData();
  formData.append("image", image);
  return operationsRequest<Product>(`products/${id}/hero-image`, { method: "POST", body: formData });
};
export const uploadProductImage = (id: number, image: File, altText: string) => {
  const formData = new FormData();
  formData.append("image", image);
  formData.append("alt_text", altText);
  return operationsRequest<ProductImage>(`products/${id}/images`, { method: "POST", body: formData });
};
export const deleteProductImage = (id: number, imageId: number) => operationsRequest<void>(`products/${id}/images/${imageId}`, { method: "DELETE" });
