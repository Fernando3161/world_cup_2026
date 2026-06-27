# visual_design.md

# World Cup Knockout Forecast Website — Visual Design Direction

## 1. Purpose

This document defines the visual direction for the public website.

The required aesthetic direction is:

> An editorial, data-rich, Financial Times-inspired visual style.

The website should feel like a serious public forecast product: restrained, credible, typographically strong, and suitable for a newspaper-style data publication.

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
FT-inspired editorial data-publication style
```

not as:

```text
Financial Times clone
Official FT style
FT-branded product
```

---

## 3. Design Intent

The visual style should communicate:

- Seriousness
- Statistical credibility
- Editorial clarity
- Warmth
- Public readability
- Data confidence without betting-site aggressiveness

The website should avoid the visual language of:

- Sports betting platforms
- Flashy gaming dashboards
- Neon analytics products
- Overly corporate SaaS dashboards
- Generic Bootstrap-style cards

The result should feel closer to an analytical newspaper interactive than to a sportsbook or fantasy-football tool.

---

## 4. Colour Direction

The colour palette should use a warm editorial paper base with restrained contrast.

Recommended palette direction:

| Token | Purpose | Suggested value |
|---|---|---:|
| `--color-paper` | Page background | `#FFF1E5` or similar warm paper tone |
| `--color-surface` | Cards and bracket panels | `#FFF8F2` |
| `--color-surface-muted` | Secondary panels | `#F2DFCE` |
| `--color-ink` | Primary text | `#1A1817` |
| `--color-muted` | Secondary text | `#6B625C` |
| `--color-rule` | Hairline borders | `#D8C3B0` |
| `--color-accent` | Links, selected states | `#0D7680` or restrained teal |
| `--color-accent-dark` | Hover/active states | `#0A5E66` |
| `--color-danger` | Validation/error | `#B00020` or muted red |
| `--color-success` | Official completion/success | `#00572C` or muted green |

The palette must pass accessibility contrast checks for text and interactive controls.

The warm background is part of the editorial direction, but the app must not use the FT logo or imply FT endorsement.

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

Recommended structure:

1. Masthead-style application header
2. Short standfirst explaining the forecast
3. Model/method controls
4. Full bracket visualization
5. Champion probability summary
6. Methodology notes
7. Data source notes

The layout should use:

- Clear vertical rhythm
- Fine rules and borders
- Moderate spacing
- Compact but readable bracket cards
- Data tables or ranked lists where appropriate
- Minimal decoration

The design should avoid heavy shadows, gradients, glassmorphism, and loud animation.

---

## 7. Bracket Component Style

Match cards should be compact and data-rich.

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
| Model winner | Subtle emphasis, not aggressive |
| User override | Clear label or icon plus styling; not color-only |
| Official locked result | Stronger editorial marker such as `Final` or `Official` |
| Unresolved | Muted placeholder treatment |
| Eliminated | Reduced emphasis, but still readable |

The bracket must remain readable on mobile, even if the mobile layout becomes stacked rather than bracket-shaped.

---

## 8. Champion Summary Style

The top champion summary should feel like a newspaper data box.

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

1. The app clearly resembles an editorial data publication rather than a betting site.
2. The page uses a warm paper-like background.
3. Typography has a serious editorial hierarchy.
4. Probability values use clear, stable numeric formatting.
5. The bracket is readable on desktop and mobile.
6. User overrides and official locks are visually distinct.
7. The model toggle is clear once both models exist.
8. No FT trademarks, logos, content, or proprietary fonts are used without license.
9. The app passes basic accessibility checks.
10. The design remains calm, restrained, and credible.

---

## 14. Guidance for Coding Agents

Coding agents must implement the visual style through reusable CSS tokens and components.

Do not hard-code one-off colours inside React components.

Do not add a heavy UI framework to achieve the visual style.

Do not import or commit proprietary fonts.

Do not use the FT logo.

Do not name the product in a way that implies Financial Times affiliation.

If a coding agent is uncertain whether an asset is licensed, it must not include it.

The correct approach is to build an original interface inspired by the editorial qualities of the Financial Times: warm paper tone, disciplined typography, restrained rules, compact data hierarchy, and high trust.
