interface SoundToggleProps {
  enabled: boolean;
  onToggle: () => void;
}

export default function SoundToggle({ enabled, onToggle }: SoundToggleProps) {
  return (
    <button
      type="button"
      className="sound-toggle"
      onClick={onToggle}
      aria-pressed={enabled}
      aria-label={enabled ? "효과음 끄기" : "효과음 켜기"}
      title={enabled ? "효과음 끄기" : "효과음 켜기"}
    >
      <span aria-hidden="true">{enabled ? "🔊" : "🔇"}</span>
      <span className="sound-toggle-label">효과음</span>
    </button>
  );
}
