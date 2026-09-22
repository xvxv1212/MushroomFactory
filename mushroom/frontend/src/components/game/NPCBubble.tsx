import { Fragment, useEffect, useMemo, useState } from "react";

import LoosePillPhoto from "./LoosePillPhoto";
import type { DialogueMessage } from "../../data/episode01stages";


interface NPCBubbleProps {
  messages: DialogueMessage[];
}

interface MessageGroup {
  sender: string;
  items: DialogueMessage[];
}

function groupMessages(messages: DialogueMessage[]): MessageGroup[] {
  const groups: MessageGroup[] = [];

  messages.forEach((message) => {
    const lastGroup = groups[groups.length - 1];

    if (lastGroup && lastGroup.sender === message.sender) {
      lastGroup.items.push(message);
    } else {
      groups.push({ sender: message.sender, items: [message] });
    }
  });

  return groups;
}

const TYPING_DELAY_MS = 700;

// 화자가 여러 명이어도 대사 전체를 하나의 순서로 이어서 공개합니다.
// (화자별로 따로 타이머를 두면 서로 다른 화자가 동시에 "타이핑 중"이
// 되어버려서, 대화가 한 줄씩 이어지는 느낌이 안 남)
function useSequentialReveal(totalCount: number) {
  const [visibleCount, setVisibleCount] = useState(
    Math.min(1, totalCount)
  );

  useEffect(() => {
    if (visibleCount >= totalCount) {
      return;
    }

    const timer = setTimeout(() => {
      setVisibleCount((count) => count + 1);
    }, TYPING_DELAY_MS);

    return () => clearTimeout(timer);
  }, [visibleCount, totalCount]);

  return visibleCount;
}

// groups 각각이 flat한 messages 배열의 몇 번째 인덱스에서 시작하는지
// 미리 계산해둡니다. (렌더 콜백 안에서 변수를 누적 재할당하면 안 되므로
// useMemo 안에서 한 번에 계산)
function withStartIndex(groups: MessageGroup[]) {
  let consumed = 0;

  return groups.map((group) => {
    const start = consumed;
    consumed += group.items.length;
    return { group, start };
  });
}

export default function NPCBubble({ messages }: NPCBubbleProps) {
  const groups = useMemo(
    () => groupMessages(messages),
    [messages]
  );

  const groupsWithStart = useMemo(
    () => withStartIndex(groups),
    [groups]
  );

  const visibleCount = useSequentialReveal(messages.length);

  return (
    <>
      {groupsWithStart.map(({ group, start }, index) => {
        // 아직 이 화자 차례가 안 됐으면(=이전 화자가 아직 다 안
        // 끝났으면) 프로필(아바타+이름) 자체를 그리지 않습니다.
        // 그래야 "프로필 등장 → 대사 → 대사 → 다음 프로필 등장"처럼
        // 화자가 바뀌는 순간에만 새 프로필이 나타나는 것처럼 보입니다.
        if (visibleCount < start) {
          return null;
        }

        const visibleInGroup = Math.min(
          group.items.length,
          Math.max(0, visibleCount - start)
        );

        const isTypingHere =
          visibleCount < messages.length &&
          visibleCount >= start &&
          visibleCount < start + group.items.length;

        return (
          <div className="npc-message" key={index}>
            <div className="npc-avatar">{group.sender.charAt(0)}</div>

            <div className="npc-message-content">
              <span className="npc-name">{group.sender}</span>

              <div className="npc-bubble-group">
                {group.items.slice(0, visibleInGroup).map((item, itemIndex) => (
                  <Fragment key={itemIndex}>
                    {item.image === "pill" && (
                      <div className="npc-bubble npc-bubble--image">
                        <LoosePillPhoto />
                      </div>
                    )}

                    {item.text.trim() && (
                      <div className="npc-bubble">
                        {item.text}
                      </div>
                    )}
                  </Fragment>
                ))}

                {isTypingHere && (
                  <div className="npc-bubble npc-bubble--typing">
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </>
  );
}
