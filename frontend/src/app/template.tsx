'use client';

export default function Template({ children }: { children: React.ReactNode }) {
  return (
    <div className="transition-opacity duration-200 ease-in-out">
      {children}
    </div>
  );
}
