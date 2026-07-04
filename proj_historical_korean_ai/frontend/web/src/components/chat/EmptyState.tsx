interface EmptyStateProps {
  title: string;
  description?: string;
}

/** Centered placeholder for "no session" / "no messages". */
export default function EmptyState({ title, description }: EmptyStateProps) {
  return (
    <div className="empty-state">
      <div className="empty-icon" aria-hidden>
        ᄒᆞ
      </div>
      <h2>{title}</h2>
      {description ? <p>{description}</p> : null}
    </div>
  );
}
