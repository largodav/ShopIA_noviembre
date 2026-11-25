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
