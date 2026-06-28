import type { PairProbability } from "./types";

export function ratingDifferenceProbability(ratingA: number, ratingB: number): PairProbability {
  const probabilityA = 1 / (1 + 10 ** ((ratingB - ratingA) / 400));
  return {
    probabilityA,
    probabilityB: 1 - probabilityA,
  };
}
