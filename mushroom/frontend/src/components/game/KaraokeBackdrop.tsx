// EP02(노래방/룸카페) 씬용 장식 배경 - 실제 사진 대신 SVG/CSS로 표현한 룸 분위기
export default function KaraokeBackdrop() {
  return (
    <div className="vn-backdrop" aria-hidden="true">
      <div className="vn-spotlight vn-spotlight--a" />
      <div className="vn-spotlight vn-spotlight--b" />

      <svg
        className="vn-disco-ball"
        viewBox="0 0 64 64"
        width="52"
        height="52"
      >
        <defs>
          <radialGradient id="vnDiscoGradient" cx="35%" cy="30%" r="70%">
            <stop offset="0%" stopColor="#FFFFFF" />
            <stop offset="55%" stopColor="#C9C2FF" />
            <stop offset="100%" stopColor="#8567C9" />
          </radialGradient>
        </defs>

        <line x1="32" y1="0" x2="32" y2="8" stroke="#C9C2FF" strokeWidth="2" />
        <circle cx="32" cy="26" r="18" fill="url(#vnDiscoGradient)" />

        <g stroke="#EDEBFF" strokeOpacity="0.5" strokeWidth="0.6">
          <path d="M14 26 H50" />
          <path d="M17 18 H47" />
          <path d="M17 34 H47" />
          <path d="M22 12 V40" />
          <path d="M32 8.5 V43.5" />
          <path d="M42 12 V40" />
        </g>
      </svg>

      <span className="vn-note vn-note--a">♪</span>
      <span className="vn-note vn-note--b">♫</span>
      <span className="vn-note vn-note--c">♪</span>
    </div>
  );
}
