import { operationsRequest } from "./client";

export interface Destination {
  id: number;
  name: string;
  slug: string;
}

export type DestinationInput = Omit<Destination, "id">;

export async function listDestinations() {
  return operationsRequest<{ results: Destination[] }>("destinations");
}

export async function createDestination(data: DestinationInput) {
  return operationsRequest<Destination>("destinations", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
}

export async function updateDestination(id: number, data: Partial<DestinationInput>) {
  return operationsRequest<Destination>(`destinations/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
}

export async function deleteDestination(id: number) {
  return operationsRequest<void>(`destinations/${id}`, { method: "DELETE" });
}
