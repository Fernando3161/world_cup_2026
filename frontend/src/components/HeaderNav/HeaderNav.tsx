interface HeaderNavProps {
  githubUrl: string;
  onOpenAbout: () => void;
  onOpenModel: () => void;
  onOpenSources: () => void;
}

export function HeaderNav({
  githubUrl,
  onOpenAbout,
  onOpenModel,
  onOpenSources,
}: HeaderNavProps) {
  return (
    <header className="site-header" aria-label="Site navigation">
      <div className="site-title-block">
        <p className="eyebrow">Static knockout forecast</p>
        <h1 id="page-title">
          <a className="site-title-link" href="#bracket-title">
            World Cup 2026 Knockout Forecast
          </a>
        </h1>
        <p className="byline">by FPV</p>
      </div>
      <nav className="site-nav" aria-label="Primary navigation">
        <button type="button" onClick={onOpenAbout}>
          About Me
        </button>
        <button type="button" onClick={onOpenModel}>
          Model
        </button>
        <button type="button" onClick={onOpenSources}>
          Data Sources
        </button>
        <a href={githubUrl} target="_blank" rel="noreferrer">
          Github
        </a>
      </nav>
    </header>
  );
}
