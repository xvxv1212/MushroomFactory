export interface Stage {
  stageId: string;
  title: string;
  npcMessages: string[];
  question: string;
  nextStage: string | null;
}

export interface Episode {
  id: string;
  title: string;
  description: string;

  totalStages: number;
  estimatedTime: string;

  status: "available" | "locked" | "completed";

  episodeId?: string;
  stages?: Stage[];
}
