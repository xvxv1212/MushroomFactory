interface InstagramDMHeaderProps {
  username: string;
}

// EP03 인스타그램 DM 연출용 - 실제 DM 앱 상단 바 느낌
export default function InstagramDMHeader({
  username,
}: InstagramDMHeaderProps) {
  return (
    <div className="ig-dm-header">
      <span className="ig-dm-back" aria-hidden="true">
        ‹
      </span>

      <span className="ig-dm-avatar">{username.charAt(0)}</span>

      <div className="ig-dm-info">
        <span className="ig-dm-username">{username}</span>
        <span className="ig-dm-status">활동 중</span>
      </div>
    </div>
  );
}
