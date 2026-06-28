import type { TournamentData } from "../types";
import { historicalEloProbability } from "./historicalElo";
import { ratingDifferenceProbability } from "./simpleElo";
import type { PairProbability } from "./types";

export function resolveSelectedModelId(
  tournamentData: TournamentData,
  requestedModelId = tournamentData.models.default_model_id,
) {
  return isProbabilityModelAvailable(tournamentData, requestedModelId)
    ? requestedModelId
    : tournamentData.models.default_model_id;
}

export function getSelectableProbabilityModels(tournamentData: TournamentData) {
  return tournamentData.models.available_models.filter((model) =>
    isProbabilityModelAvailable(tournamentData, model.model_id),
  );
}

export function isProbabilityModelAvailable(
  tournamentData: TournamentData,
  modelId: string,
) {
  const metadata = tournamentData.models.available_models.find((model) => model.model_id === modelId);
  if (!metadata?.is_available) {
    return false;
  }

  if (modelId === "simple_elo") {
    return true;
  }

  return Boolean(tournamentData.models.calibrated_models?.[modelId]);
}

export function calculateRatingProbability(
  ratingA: number,
  ratingB: number,
  tournamentData: TournamentData,
  selectedModelId: string,
): PairProbability {
  const modelId = resolveSelectedModelId(tournamentData, selectedModelId);

  if (modelId === "simple_elo") {
    return ratingDifferenceProbability(ratingA, ratingB);
  }

  const calibratedModel = tournamentData.models.calibrated_models?.[modelId];
  if (calibratedModel) {
    return historicalEloProbability(ratingA, ratingB, calibratedModel);
  }

  return ratingDifferenceProbability(ratingA, ratingB);
}
