export type CardType = "product" | "comparison" | "suggestion" | "status";

export interface InfoCard {
  id: string;
  type: CardType;
  title: string;
  subtitle?: string;
  summary: string;
  price?: string;
  category?: string;
  sourceUrl?: string;
  tags?: string[];
}

export interface PredictResponse {
  query: string;
  version: string;
  ollamaActive?: boolean;
  model?: string | null;
  offline?: boolean;
  cards: InfoCard[];
}

export interface LocalModel {
  name: string;
  size_gb?: number | null;
  family?: string | null;
  parameter_size?: string | null;
  quantization?: string | null;
}

export interface ModelsResponse {
  reachable: boolean;
  selected_model: string;
  models: LocalModel[];
}

export interface BackendHostInfo {
  os: string;
  name: string;
}

export interface BackendHealth {
  status: string;
  service: string;
  version: string;
  host?: BackendHostInfo;
  auth_enabled?: boolean;
  ollama?: {
    url?: string;
    reachable: boolean;
    selected_model?: string;
    available_models_count?: number;
  };
  web_push_configured?: boolean;
}

export interface SyncQueueItem {
  id: string;
  kind: "search" | "model";
  query?: string;
  model?: string;
  createdAt: number;
}
