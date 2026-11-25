import type { ChangeEvent } from "react";

interface PredictiveInputProps {
  value: string;
  onChange: (value: string) => void;
  isLoading: boolean;
}

export function PredictiveInput({ value, onChange, isLoading }: PredictiveInputProps) {
  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    onChange(e.target.value);
  };

  return (
    <div className="predictive-input-wrapper">
      <input
        type="text"
        className="predictive-input"
        value={value}
        onChange={handleChange}
        placeholder="Busca o pregunta sobre electrónica en El Corte Inglés..."
        aria-label="Petición a ShopIA"
        autoComplete="off"
        autoFocus
      />
      {isLoading && <span className="predictive-indicator" aria-hidden="true" />}
    </div>
  );
}
