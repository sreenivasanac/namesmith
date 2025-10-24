import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export const BRAND_NAME = "Namesmith";
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

export function buildApiUrl(path: string): string {
  return `${API_BASE_URL.replace(/\/$/, "")}/${path.replace(/^\//, "")}`;
}
