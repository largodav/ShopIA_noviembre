import type { InfoCard } from "../../types/shopia";

interface InfoCardsProps {
  cards: InfoCard[];
}

export function InfoCards({ cards }: InfoCardsProps) {
  if (cards.length === 0) return null;

  return (
    <section className="cards-grid" aria-live="polite" aria-label="Resultados predictivos">
      {cards.map((card) => (
        <article key={card.id} className="info-card">
          <div className="info-card-header">
            <div>
              <h2 className="info-card-title">{card.title}</h2>
              {card.subtitle && <p className="info-card-subtitle">{card.subtitle}</p>}
            </div>
            {card.price && <span className="info-card-price">{card.price}</span>}
          </div>
          <p className="info-card-summary">{card.summary}</p>
          {card.tags && card.tags.length > 0 && (
            <div className="info-card-tags">
              {card.tags.map((tag) => (
                <span key={tag} className="info-card-tag">
                  {tag}
                </span>
              ))}
            </div>
          )}
        </article>
      ))}
    </section>
  );
}
