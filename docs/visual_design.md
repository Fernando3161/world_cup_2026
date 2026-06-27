# visual_design.md

# World Cup Knockout Forecast Website — Visual Design Direction

## 1. Purpose

This document defines the visual direction for the public website.

The original Stage 4-6 aesthetic direction was:

> An editorial, data-rich, Financial Times-inspired visual style.

That direction is now superseded for the public MVP by Visual Design v2.

The required Visual Design v2 direction is:

> A premium football analytics dashboard with a light page shell and a dark bracket-first tournament canvas.

The website should still feel serious, credible, typographically disciplined, and suitable for public analysis. It should no longer feel like a quiet newspaper page where the bracket arrives after ceremonial whitespace. The bracket is the product and must become the immediate visual hero.

This is an aesthetic direction, not a request to copy the Financial Times brand identity.

---

## 2. Legal and Brand Boundaries

The project must not present itself as a Financial Times product.

The project must not use:

- The Financial Times name as a product name
- The FT logo
- Financial Times trademarks
- FT proprietary fonts unless the project owner has a valid license
- FT content, headlines, articles, imagery, or data unless separately licensed
- Exact FT branding in a way that implies endorsement, partnership, or affiliation

The implementation should be described as:

```text
premium football analytics dashboard
```

not as:

```text
Financial Times clone
Official FT style
FT-branded product
FIFA clone
betting product
```

The project must not use FIFA logos, competition marks, proprietary football imagery, betting-brand patterns, or design choices that imply official affiliation.

---

## 3. Design Intent

The Visual Design v2 style should communicate:

- Seriousness
- Statistical credibility
- Analytical clarity
- Premium football context
- Public readability
- Data confidence without betting-site aggressiveness

The website should avoid the visual language of:

- Sports betting platforms
- Flashy gaming dashboards
- Neon analytics products
- Overly corporate SaaS dashboards
- Generic pastel SaaS dashboards
- Childish sports-broadcast graphics
- FIFA or broadcaster clones

The result should feel closer to a polished football analytics product than to a sportsbook, fantasy-football toy, or empty editorial landing page.

### 3.1 Rationale For V2

Visual Design v1 was too restrained for this product. The MVP is functionally useful but the FT-inspired warm-paper treatment made the page feel too empty, quiet, and unattractive. The bracket is the main product surface, so the first viewport must make the tournament tree prominent immediately.

---

## 4. Colour Direction

The colour palette should use a light page shell around a dark bracket canvas. It should be stronger than v1, but still controlled and professional.

Recommended Visual Design v2 palette direction:

| Token | Purpose | Suggested value |
|---|---|---:|
| `--color-page` | Light outer page shell | `#F4F7FB` or similar cool off-white |
| `--color-panel` | Dark bracket canvas | `#07111F`, `#0B1220`, or dark navy |
| `--color-node` | Match node surface on dark canvas | `#101C2E` or deep slate |
| `--color-node-light` | Light cards outside bracket | `#FFFFFF` or near-white |
| `--color-ink` | Primary shell text | `#111827` |
| `--color-panel-ink` | Primary text on dark panel | `#F8FAFC` |
| `--color-muted` | Secondary shell text | `#64748B` |
| `--color-panel-muted` | Secondary text on dark panel | `#94A3B8` |
| `--color-line` | Bracket connector lines | `#475569` or muted slate |
| `--color-accent` | Selected winners/user picks | restrained teal/green |
| `--color-gold` | Final/champion-path emphasis | controlled gold/amber |
| `--color-loser` | Eliminated/losing state | grey, desaturated, lower opacity |
| `--color-danger` | Validation/error | `#B00020` or muted red |
| `--color-success` | Official completion/success | `#00572C` or muted green |

The palette must pass accessibility contrast checks for text and interactive controls.

Avoid excessive beige, pastel SaaS styling, over-bright neon colors, sportsbook red/green aggression, and harsh pure black/white contrast.

---

## 5. Typography Direction

The typography should be editorial and data-oriented.

Recommended approach:

- Use a serif typeface for major headlines and editorial sections.
- Use a highly readable sans-serif typeface for UI controls, labels, match cards, and compact data.
- Use tabular numbers where possible for probabilities and rankings.
- Use strong but restrained typographic hierarchy.

Recommended open or system alternatives:

| Use | Preferred open/system option |
|---|---|
| Headlines | `Source Serif 4`, `Georgia`, `Libre Baskerville`, or `Lora` |
| Body/editorial text | `Georgia` or `Source Serif 4` |
| UI labels and controls | `Source Sans 3`, `Inter`, `Arial`, or system sans-serif |
| Probabilities/table figures | Sans-serif with `font-variant-numeric: tabular-nums` |

Do not commit proprietary FT fonts to the repository.

Do not include licensed font files unless the license is explicit and documented.

---

## 6. Layout Direction

The layout should resemble an editorial data feature.

Recommended Visual Design v2 structure:

1. Compact top navigation
2. Compact title/byline/status strip
3. Compact model/scenario/champion summary controls
4. Large dark bracket panel visible in the first desktop viewport
5. Footer and supporting notes below the primary bracket view

The layout should use:

- Clear vertical rhythm
- Compact top spacing
- Minimal ceremonial whitespace before the bracket
- Compact but readable bracket cards
- A polished knockout-tree bracket panel as the page hero
- Data tables or ranked lists only where they support the main bracket

The design should avoid heavy shadows, gradients, glassmorphism, and loud animation.

The bracket must be prominently visible in the first desktop viewport. The landing view must not show mostly empty space or large controls before the bracket.

### 6.1 Stage 6.3 / Visual Design V2.1 Refinement

Visual Design v2.1 tightens the first-page hierarchy:

1. Title / nav row
2. Bracket
3. Model status, scenario controls, champion summary, and reset controls
4. Additional explanations
5. Footer

The bracket must appear immediately after the title/header area. Secondary analytical panels are important, but they must not push the bracket downward or make the landing view feel like a dashboard where the main visual object is delayed.

The first impression should be that this is a World Cup knockout bracket forecast. The page should not open with large boxes, control panels, or summary cards above the bracket.

---

## 7. Bracket Component Style

Match cards should be compact and data-rich, but the tournament-tree structure has priority over per-card detail.

Each match card should show:

- Round label or implied round position
- Team flag
- Team short name or full name depending on available width
- Advancement probability
- Winner state
- Selection source where relevant

Visual states must include:

| State | Visual treatment |
|---|---|
| Model winner | Highlight, stronger border, accent edge, or brighter text |
| User override | Clear accent treatment plus accessible label; not color-only |
| Official locked result | Stronger editorial marker such as `Final` or `Official` |
| Unresolved | Muted placeholder treatment |
| Eliminated/loser | Desaturated, greyed, or lower opacity, but still readable |

The bracket must remain readable on mobile, even if the mobile layout becomes stacked rather than bracket-shaped.

Country labels in bracket nodes must not wrap mid-word. If full names do not fit, compact nodes should use flag plus FIFA-style three-letter code plus probability, for example `POR 64%`. Full names can appear in accessible labels, title text, or detail states.

Do not use large textual `WIN` labels inside team names. Winner and loser states should be communicated visually through highlight, opacity, borders, and accent marks.

### 7.1 Flag Rendering

The public MVP should render flags from local static SVG assets, not emoji glyphs. This avoids operating-system differences where emoji flags may render as regional letters.

When `flag_mode = "asset"`, the UI must render the local image path stored in `flag_value`, for example `/flags/arg.svg`. These assets must be served from the frontend public folder and must not be remote runtime URLs.

When `flag_mode = "emoji"`, the UI may render the actual emoji string stored in `flag_value`, but this is fallback behavior rather than the preferred public display mode.

If a flag image is unavailable or fails to load, the UI may use a graceful fallback such as a FIFA-style code or short name. Team labels may still use FIFA-style three-letter codes for compact names.

---

## 8. Champion Summary Style

The top champion summary should feel like a compact sports-data summary, not a betting widget.

Recommended presentation:

- Ranked list of top four teams
- Large probability figures
- Small explanatory captions
- Optional small horizontal bars
- Clear model-mode label

The summary must not look like betting odds.

Avoid language such as:

```text
Best bets
Lock of the day
Guaranteed winner
```

Use probabilistic language such as:

```text
Most likely champions
Title probability
Forecast probability
Model estimate
```

---

## 9. Model Toggle Style

When both models exist, the model toggle must be visually clear and editorially restrained.

The two model modes are:

- `simple_elo`
- `historical_elo`

The UI labels may be:

```text
Simple Elo
Historically informed Elo
```

The selected model must be clear through more than color alone.

The method notes must update when the selected model changes.

---

## 10. Motion and Interaction

Motion should be minimal.

Allowed motion:

- Small hover transitions
- Subtle expanding method notes
- Smooth but quick bracket updates

Avoid:

- Confetti
- Sportsbook-style flashing odds
- Auto-playing animations
- Distracting transitions

Forecast updates should feel stable and analytical.

---

## 11. CSS Architecture

The frontend should use custom CSS with design tokens.

Recommended files:

```text
frontend/src/styles/tokens.css
frontend/src/styles/global.css
frontend/src/styles/typography.css
frontend/src/styles/layout.css
frontend/src/styles/components.css
```

The CSS should define tokens for:

- Colour
- Font families
- Font sizes
- Spacing
- Border/rule widths
- Border radii
- Focus outlines
- Z-index, if needed

Components should consume tokens instead of hard-coded colour and spacing values.

---

## 12. Accessibility Requirements

The visual design must preserve accessibility.

Requirements:

- Sufficient text contrast
- Keyboard-visible focus states
- No meaning conveyed by color alone
- Readable probabilities and labels
- Responsive layout
- Accessible labels for controls
- Screen-reader-friendly model toggle

Aesthetic similarity must never override accessibility.

---

## 13. Acceptance Criteria

The visual design is acceptable when:

1. The app clearly resembles a professional football analytics product rather than a betting site.
2. The page uses a light shell around a dark bracket canvas.
3. The bracket appears before secondary analytical panels.
4. Probability values use clear, stable numeric formatting.
5. The bracket is readable on desktop and mobile.
6. User overrides and official locks are visually distinct.
7. The model toggle is clear once both models exist.
8. No FT trademarks, logos, content, or proprietary fonts are used without license.
9. The app passes basic accessibility checks.
10. The design remains calm, analytical, and credible.

---

## 14. Guidance for Coding Agents

Coding agents must implement the visual style through reusable CSS tokens and components.

Do not hard-code one-off colours inside React components.

Do not add a heavy UI framework to achieve the visual style.

Do not import or commit proprietary fonts.

Do not use the FT logo.

Do not name the product in a way that implies Financial Times affiliation.

If a coding agent is uncertain whether an asset is licensed, it must not include it.

The correct Visual Design v2 approach is to build an original premium football analytics interface: light shell, compact controls, dark bracket canvas, polished knockout-tree structure, disciplined typography, controlled accents, and high trust.

Do not return to the v1 warm-paper editorial layout unless the project explicitly reverses this design decision.

---

## 15. Visual Design V2 Acceptance Criteria

The Visual Design v2 implementation is acceptable when:

1. The first desktop viewport prominently shows the bracket.
2. The bracket appears immediately after the title/header area.
3. Model controls, scenario status, champion summary, and explanatory panels sit below the bracket or otherwise do not push it downward.
4. The page avoids large empty ceremonial whitespace before the bracket.
5. The bracket is presented as a polished tournament-tree diagram.
6. The bracket sits inside a dark, premium bracket canvas/panel.
7. The page shell around the bracket remains light and professional.
8. Winner/loser state is conveyed visually, not through large textual `WIN` labels.
9. Winners are highlighted and losers are greyed, desaturated, or lower opacity.
10. Country labels in compact bracket nodes do not wrap mid-word.
11. Compact bracket nodes use FIFA-style codes when full names do not fit.
12. Public MVP flags render as local SVG images from `frontend/public/flags`, with graceful text fallback if an asset is unavailable.
13. Color accents are controlled: dark navy/charcoal, off-white, gold/amber for final/champion emphasis, teal/green for selected winners, muted slate for lines, and grey for losing states.
14. The design avoids betting aesthetics, FIFA cloning, childish sports graphics, excessive beige, excessive whitespace, and pastel SaaS styling.
15. Functionality remains unchanged.
