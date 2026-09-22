import { useCallback, useEffect, useRef, useState } from "react";

type SoundKind = "tap" | "transition" | "feedback" | "complete";

const STORAGE_KEY = "manyang_sound_enabled";

export default function useGameSound() {
  const [enabled, setEnabled] = useState(() => {
    if (typeof window === "undefined") {
      return true;
    }

    return window.localStorage.getItem(STORAGE_KEY) !== "off";
  });

  const contextRef = useRef<AudioContext | null>(null);

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, enabled ? "on" : "off");
  }, [enabled]);

  const play = useCallback(
    (kind: SoundKind) => {
      if (!enabled || typeof window === "undefined") {
        return;
      }

      try {
        const AudioContextClass =
          window.AudioContext ||
          (window as typeof window & { webkitAudioContext?: typeof AudioContext })
            .webkitAudioContext;

        if (!AudioContextClass) {
          return;
        }

        const context = contextRef.current ?? new AudioContextClass();
        contextRef.current = context;

        if (context.state === "suspended") {
          void context.resume();
        }

        const now = context.currentTime;
        const oscillator = context.createOscillator();
        const gain = context.createGain();

        const settings: Record<
          SoundKind,
          { start: number; end: number; duration: number; volume: number; type: OscillatorType }
        > = {
          tap: {
            start: 520,
            end: 620,
            duration: 0.07,
            volume: 0.035,
            type: "sine",
          },
          transition: {
            start: 360,
            end: 520,
            duration: 0.16,
            volume: 0.045,
            type: "triangle",
          },
          feedback: {
            start: 620,
            end: 820,
            duration: 0.18,
            volume: 0.05,
            type: "sine",
          },
          complete: {
            start: 660,
            end: 990,
            duration: 0.24,
            volume: 0.055,
            type: "triangle",
          },
        };

        const sound = settings[kind];

        oscillator.type = sound.type;
        oscillator.frequency.setValueAtTime(sound.start, now);
        oscillator.frequency.exponentialRampToValueAtTime(
          sound.end,
          now + sound.duration
        );

        gain.gain.setValueAtTime(0.0001, now);
        gain.gain.exponentialRampToValueAtTime(sound.volume, now + 0.018);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + sound.duration);

        oscillator.connect(gain);
        gain.connect(context.destination);

        oscillator.start(now);
        oscillator.stop(now + sound.duration + 0.02);
      } catch {
        // 사운드가 지원되지 않거나 브라우저 정책으로 차단되어도
        // 학습 흐름은 그대로 진행되도록 조용히 무시합니다.
      }
    },
    [enabled]
  );

  const toggle = useCallback(() => {
    setEnabled((prev) => !prev);
  }, []);

  return { enabled, toggle, play };
}
