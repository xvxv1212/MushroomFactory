interface DialogueMessage {
  sender: string;
  text: string;
}

interface SceneDialogueProps {
  message: DialogueMessage;
  onAdvance: () => void;
}

// 비주얼노벨처럼 한 줄씩 보여주는 대사창. 클릭하면 다음 대사로 넘어갑니다.
export default function SceneDialogue({
  message,
  onAdvance,
}: SceneDialogueProps) {
  return (
    <button
      type="button"
      className="vn-line vn-line--advance"
      onClick={onAdvance}
    >
      <span className="vn-line-name">{message.sender}</span>
      <p className="vn-line-text">{message.text}</p>
      <span className="vn-advance-hint" aria-hidden="true">
        ▸
      </span>
    </button>
  );
}
