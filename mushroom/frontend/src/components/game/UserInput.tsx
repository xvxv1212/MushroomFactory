import { useState } from "react";

import { containsProfanity } from "../../utils/profanity";


interface UserInputProps {
  onSubmit: (message: string) => void;
  onChange?: (value: string) => void;
  disabled?: boolean;
  placeholder?: string;
}


export default function UserInput({
  onSubmit,
  onChange,
  disabled = false,
  placeholder = "내 생각을 직접 말해보세요...",
}: UserInputProps) {

  const [message, setMessage] =
    useState("");


  // 현재 입력에 욕설이 있는지
  const hasProfanity =
    containsProfanity(message);


  // 실제 전송 가능 여부
  const canSend =
    message.trim().length > 0 &&
    !hasProfanity &&
    !disabled;


  const handleChange = (
    value: string
  ) => {

    setMessage(value);

    onChange?.(value);
  };


  const handleSubmit = () => {

    const trimmedMessage =
      message.trim();


    // 빈 값
    if (!trimmedMessage) {
      return;
    }


    // 서버 통신 중 등 외부 비활성화 상태
    if (disabled) {
      return;
    }


    // 욕설 포함
    if (
      containsProfanity(
        trimmedMessage
      )
    ) {
      return;
    }


    onSubmit(
      trimmedMessage
    );


    setMessage("");

    onChange?.("");
  };


  const handleKeyDown = (
    e:
      React.KeyboardEvent<
        HTMLTextAreaElement
      >
  ) => {

    if (
      e.key === "Enter" &&
      !e.shiftKey
    ) {

      e.preventDefault();


      // 욕설이 있으면 Enter로도 전송 불가
      if (!canSend) {
        return;
      }


      handleSubmit();
    }
  };


  return (
    <div className="dm-composer-wrapper">

      {/* 욕설 입력 안내 */}
      {hasProfanity && (
        <div
          className="chat-input-warning"
          role="alert"
        >
          공격적인 표현 대신 자신의 생각과 행동을
          문장으로 표현해 주세요.
        </div>
      )}


      <div className="dm-composer">

        <textarea
          className={
            hasProfanity
              ? "dm-composer-input dm-composer-input--warning"
              : "dm-composer-input"
          }

          value={message}

          disabled={disabled}

          placeholder={placeholder}

          onChange={
            (e) =>
              handleChange(
                e.target.value
              )
          }

          onKeyDown={
            handleKeyDown
          }

          rows={1}
        />


        <button
          type="button"

          className="dm-composer-send"

          onClick={
            handleSubmit
          }

          disabled={
            !canSend
          }

          aria-label="전송"
        >
          ➤
        </button>

      </div>
    </div>
  );
}