import type { Episode } from "../../types/episode";

interface EpisodeCardProps {
  episode: Episode;
  onStart: (episodeId: string) => void;
}

function EpisodeCard({
  episode,
  onStart,
}: EpisodeCardProps) {
  return (
    <article className="episode-card">
      <h2>{episode.title}</h2>

      <p>{episode.description}</p>

      <div>
        <span>{episode.totalStages}단계</span>
        <span>{episode.estimatedTime}</span>
      </div>

      <button
        onClick={() => onStart(episode.id)}
        disabled={episode.status === "locked"}
      >
        시작하기
      </button>
    </article>
  );
}

export default EpisodeCard;