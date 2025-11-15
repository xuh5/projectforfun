import './SkeletonLoader.css';

interface SkeletonLoaderProps {
  width?: string;
  height?: string;
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular';
}

export default function SkeletonLoader({
  width,
  height,
  className = '',
  variant = 'text',
}: SkeletonLoaderProps) {
  const style: React.CSSProperties = {};
  if (width) style.width = width;
  if (height) style.height = height;

  return (
    <span
      className={`skeleton skeleton-${variant} ${className}`}
      style={style}
      aria-hidden="true"
    />
  );
}

export function SkeletonCompanyPage() {
  return (
    <main className="company-page">
      <div className="company-shell">
        <section className="company-hero skeleton-section">
          <div>
            <SkeletonLoader width="120px" height="28px" className="skeleton-badge" />
            <SkeletonLoader width="300px" height="48px" className="skeleton-title" />
            <SkeletonLoader width="100%" height="80px" className="skeleton-description" />
          </div>
          <div className="skeleton-metrics">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="skeleton-metric">
                <SkeletonLoader width="80px" height="16px" />
                <SkeletonLoader width="100px" height="24px" />
              </div>
            ))}
          </div>
        </section>

        <section className="company-content-grid">
          <article className="company-overview skeleton-section">
            <SkeletonLoader width="200px" height="28px" className="skeleton-header" />
            <div className="skeleton-metadata">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="skeleton-metadata-item">
                  <SkeletonLoader width="120px" height="16px" />
                  <SkeletonLoader width="150px" height="20px" />
                </div>
              ))}
            </div>
          </article>

          <article className="company-stock skeleton-section">
            <SkeletonLoader width="200px" height="28px" className="skeleton-header" />
            <SkeletonLoader width="100%" height="200px" variant="rectangular" className="skeleton-chart" />
          </article>
        </section>

        <section className="company-connections skeleton-section">
          <SkeletonLoader width="250px" height="28px" className="skeleton-header" />
          <div className="skeleton-connections">
            {[1, 2, 3].map((i) => (
              <div key={i} className="skeleton-connection-card">
                <SkeletonLoader width="100%" height="120px" variant="rectangular" />
              </div>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}

