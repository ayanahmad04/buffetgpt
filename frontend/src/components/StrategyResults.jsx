/**
 * StrategyResults - Renders full eating strategy from API response
 */

function PhaseCard({ phase }) {
  if (!phase?.items?.length) return null
  return (
    <div className="rounded-xl border border-stone-200 bg-white p-5">
      <h3 className="font-display font-semibold text-stone-800 mb-3 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-buffet-400" />
        {phase.phase_name}
      </h3>
      <ul className="space-y-2">
        {phase.items.map((item, i) => (
          <li key={i} className="flex justify-between items-start text-sm">
            <div>
              <span className="font-medium text-stone-700">{item.dish_name}</span>
              <span className="text-stone-500 ml-2">
                {item.portion_grams}g · {item.calories} cal
              </span>
              {item.reason && (
                <p className="text-xs text-stone-400 mt-0.5">{item.reason}</p>
              )}
            </div>
            <span className="text-xs text-stone-500 font-mono">
              P{item.protein} C{item.carbs} F{item.fat}
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}

export function StrategyResults({ data, className = '' }) {
  const { detected_dishes, nutrition_summary, stomach_simulation, strategy, explanation, confidence_overall } = data

  const phases = strategy?.phases ?? []
  const skip = strategy?.skip ?? []
  const totalCal = strategy?.total_calories ?? 0
  const fullness = (strategy?.fullness_score ?? 0) * 100

  return (
    <div className={`space-y-8 ${className}`}>
      {/* Summary cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="rounded-xl bg-white border border-stone-200 p-4">
          <p className="text-xs text-stone-500 uppercase tracking-wider">Total Calories</p>
          <p className="text-2xl font-display font-bold text-buffet-600">{totalCal}</p>
        </div>
        <div className="rounded-xl bg-white border border-stone-200 p-4">
          <p className="text-xs text-stone-500 uppercase tracking-wider">Fullness</p>
          <div className="mt-1 h-2 bg-stone-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-stomach-mid rounded-full transition-all"
              style={{ width: `${fullness}%` }}
            />
          </div>
          <p className="text-sm font-medium text-stone-700 mt-1">{fullness.toFixed(0)}%</p>
        </div>
        <div className="rounded-xl bg-white border border-stone-200 p-4">
          <p className="text-xs text-stone-500 uppercase tracking-wider">Detected</p>
          <p className="text-2xl font-display font-bold text-stone-700">{detected_dishes?.length ?? 0}</p>
          <p className="text-xs text-stone-500">dishes</p>
        </div>
        <div className="rounded-xl bg-white border border-stone-200 p-4">
          <p className="text-xs text-stone-500 uppercase tracking-wider">Confidence</p>
          <p className="text-2xl font-display font-bold text-stone-700">
            {(confidence_overall * 100).toFixed(0)}%
          </p>
        </div>
      </div>

      {/* Explanation */}
      <div className="rounded-xl bg-buffet-50/50 border border-buffet-200/50 p-5">
        <h3 className="font-display font-semibold text-stone-800 mb-2">Strategy</h3>
        <p className="text-stone-700 leading-relaxed">{explanation}</p>
      </div>

      {/* Eating phases */}
      <div>
        <h2 className="font-display font-semibold text-stone-800 mb-4">Eating Order</h2>
        <div className="grid sm:grid-cols-2 gap-4">
          {phases.map((phase, i) => (
            <PhaseCard key={i} phase={phase} />
          ))}
        </div>
      </div>

      {/* Skip list */}
      {skip.length > 0 && (
        <div className="rounded-xl border border-stone-200 bg-stone-50/50 p-5">
          <h3 className="font-display font-semibold text-stone-700 mb-2">Skip or minimize</h3>
          <div className="flex flex-wrap gap-2">
            {skip.map((s, i) => (
              <span
                key={i}
                className="px-3 py-1 rounded-full bg-stone-200/80 text-stone-600 text-sm"
              >
                {s.name}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Detected dishes list */}
      {detected_dishes?.length > 0 && (
        <details className="rounded-xl border border-stone-200 bg-white">
          <summary className="px-5 py-4 cursor-pointer font-medium text-stone-700">
            Detected dishes ({detected_dishes.length})
          </summary>
          <div className="px-5 pb-4 flex flex-wrap gap-2">
            {detected_dishes.map((d, i) => (
              <span
                key={i}
                className="px-3 py-1 rounded-lg bg-stone-100 text-stone-600 text-sm"
              >
                {d.name} ({d.estimated_grams}g)
              </span>
            ))}
          </div>
        </details>
      )}

      {/* Nutrition summary */}
      {nutrition_summary && Object.keys(nutrition_summary).length > 0 && (
        <details className="rounded-xl border border-stone-200 bg-white">
          <summary className="px-5 py-4 cursor-pointer font-medium text-stone-700">
            Nutrition summary
          </summary>
          <div className="px-5 pb-4 grid grid-cols-2 sm:grid-cols-3 gap-2 text-sm">
            {Object.entries(nutrition_summary).map(([k, v]) => (
              <div key={k} className="flex justify-between">
                <span className="text-stone-500">{k.replace(/_/g, ' ')}</span>
                <span className="font-mono text-stone-700">{v}</span>
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  )
}
