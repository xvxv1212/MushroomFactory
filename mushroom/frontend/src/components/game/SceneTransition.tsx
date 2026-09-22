interface SceneTransitionProps {
  step: number;
  title: string;
  location: string;
}

export default function SceneTransition({
  step,
  title,
  location,
}: SceneTransitionProps) {
  return (
    <div className="scene-transition" role="status" aria-live="polite">
      <div className="scene-transition-card">
        <span className="scene-transition-step">STEP {step}</span>
        <strong>{title}</strong>
        <span className="scene-transition-location">📍 {location}</span>
      </div>
    </div>
  );
}
