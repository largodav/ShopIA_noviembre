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
  cards: InfoCard[];
}
