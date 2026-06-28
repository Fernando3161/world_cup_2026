import type { CalibratedProbabilityModel } from "../types";
import type { PairProbability } from "./types";

export function historicalEloProbability(
  ratingA: number,
  ratingB: number,
  calibratedModel: CalibratedProbabilityModel,
): PairProbability {
  const { alpha, beta } = calibratedModel.calibration;
  const ratingDiff = ratingA - ratingB;
  const probabilityA = logistic(alpha + beta * ratingDiff);

  return {
    probabilityA,
    probabilityB: 1 - probabilityA,
  };
}

function logistic(value: number) {
  if (value >= 0) {
    return 1 / (1 + Math.exp(-value));
  }

  const expValue = Math.exp(value);
  return expValue / (1 + expValue);
}
