'use client';

interface Insight {
  id: number;
  type: 'alert' | 'warning' | 'info' | 'success' | 'tip' | string;
  title: string;
  description: string;
  action?: string;
  amount?: number;
  category?: string;
  priority: number;
}

interface Props {
  insight: Insight;
  onDismiss?: (id: number) => void;
  onAction?: (insight: Insight) => void;
}

const typeStyles: Record<string, { border: string; icon: JSX.Element; badge: string }> = {
  alert:   { border: 'border-red-500',    icon: <span>⚠️</span>, badge: 'bg-red-100 text-red-800' },
  warning: { border: 'border-yellow-500', icon: <span>⚠️</span>, badge: 'bg-yellow-100 text-yellow-800' },
  info:    { border: 'border-blue-500',   icon: <span>✨</span>, badge: 'bg-blue-100 text-blue-800' },
  success: { border: 'border-green-500',  icon: <span>✅</span>, badge: 'bg-green-100 text-green-800' },
  tip:     { border: 'border-purple-500', icon: <span>💡</span>, badge: 'bg-purple-100 text-purple-800' },
};

export default function InsightCard({ insight, onDismiss, onAction }: Props) {
  const style = typeStyles[insight.type] || typeStyles.info;
  const formatCurrency = (n: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(n);

  return (
    <div className={`relative bg-white shadow-sm hover:shadow-md transition-shadow rounded-xl p-5 border-l-4 ${style.border}`}>
      <button className="absolute right-2 top-2 text-gray-400 hover:text-gray-600 rounded-full w-7 h-7 flex items-center justify-center hover:bg-gray-100" onClick={() => onDismiss?.(insight.id)}>×</button>
      <div className="flex items-start gap-3">
        <div className="text-xl">{style.icon}</div>
        <div className="flex-1">
          <div className="font-semibold text-gray-900 text-base leading-6">{insight.title}</div>
          <div className="text-gray-700 mt-1 leading-6">{insight.description}</div>
          <div className="mt-2 flex flex-wrap gap-2 items-center">
            {typeof insight.amount === 'number' && (
              <span className={`text-xs px-2 py-1 rounded-full ${style.badge}`}>{formatCurrency(insight.amount)}</span>
            )}
            {insight.category && (
              <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-800">{insight.category}</span>
            )}
          </div>
          {/* Action button intentionally hidden per request */}
        </div>
      </div>
    </div>
  );
}


