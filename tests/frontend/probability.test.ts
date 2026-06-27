import { describe, expect, it } from "vitest";

import { ratingDifferenceProbability } from "../../frontend/src/domain/probability/simpleElo";

describe("ratingDifferenceProbability", () => {
  it("returns 50/50 for equal ratings", () => {
    const probabilities = ratingDifferenceProbability(1800, 1800);

    expect(probabilities.probabilityA).toBeCloseTo(0.5, 12);
    expect(probabilities.probabilityB).toBeCloseTo(0.5, 12);
  });

  it("gives the higher-rated team the higher probability", () => {
    const probabilities = ratingDifferenceProbability(1900, 1700);

    expect(probabilities.probabilityA).toBeGreaterThan(probabilities.probabilityB);
  });

  it("returns probabilities that sum to 1", () => {
    const probabilities = ratingDifferenceProbability(1640, 1725);

    expect(probabilities.probabilityA + probabilities.probabilityB).toBeCloseTo(1, 12);
  });
});

