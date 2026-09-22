import { Fragment, useEffect, useMemo, useState } from "react";

import DietPillPhoto from "./DietPillPhoto";
import DietReviewPhoto from "./DietReviewPhoto";
import type { DialogueMessage } from "../../data/episode01stages";


interface InstagramBubbleProps {
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
// (NPCBubble.tsx와 동일한 이유 - 화자별 독립 타이머는 병렬 진행이 됨)
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

// EP03 인스타그램 DM 연출용 - 상단에 상대 계정명이 이미 나오므로
// 말풍선마다 이름을 반복하지 않는, 실제 DM에 가까운 모양입니다.
export default function InstagramBubble({ messages }: InstagramBubbleProps) {
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
        const visibleInGroup = Math.min(
          group.items.length,
          Math.max(0, visibleCount - start)
        );

        const isTypingHere =
          visibleCount < messages.length &&
          visibleCount >= start &&
          visibleCount < start + group.items.length;

        return (
          <div className="ig-message" key={index}>
            {group.items.slice(0, visibleInGroup).map((item, itemIndex) => {
              if (item.image === "product" || item.image === "review") {
                const Photo =
                  item.image === "product" ? DietPillPhoto : DietReviewPhoto;

                return (
                  <Fragment key={itemIndex}>
                    <div className="ig-bubble ig-bubble--image">
                      <Photo />
                    </div>
                    <div className="ig-bubble">{item.text}</div>
                  </Fragment>
                );
              }

              return (
                <div className="ig-bubble" key={itemIndex}>
                  {item.text}
                </div>
              );
            })}

            {isTypingHere && (
              <div className="ig-bubble ig-bubble--typing">
                <span className="typing-dot" />
                <span className="typing-dot" />
                <span className="typing-dot" />
              </div>
            )}
          </div>
        );
      })}
    </>
  );
}
