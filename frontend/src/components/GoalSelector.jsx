import { useState } from 'react'

const GOALS = [
  { id: 'enjoyment_first', label: 'Enjoyment First', icon: '🎯', desc: 'Balance satiety & variety' },
  { id: 'fat_loss', label: 'Fat Loss', icon: '🔥', desc: 'High protein, low calorie density' },
  { id: 'muscle_gain', label: 'Muscle Gain', icon: '💪', desc: 'Prioritize protein & carbs' },
  { id: 'blood_sugar', label: 'Blood Sugar Control', icon: '📊', desc: 'Low glycemic, high fiber' },
]

export function GoalSelector({ goal, onGoalChange, calorieLimit, onCalorieLimitChange, filters, onFiltersChange }) {
  const [showFilters, setShowFilters] = useState(false)

  return (
    <div className="rounded-2xl bg-white/80 backdrop-blur border border-stone-200/80 shadow-sm p-6">
      <h2 className="font-display font-semibold text-stone-800 mb-4">Your Goal</h2>
      <div className="flex flex-wrap gap-2 mb-6">
        {GOALS.map((g) => (
          <button
            key={g.id}
            onClick={() => onGoalChange(g.id)}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
              goal === g.id
                ? 'bg-buffet-500 text-white shadow-md'
                : 'bg-stone-100 text-stone-600 hover:bg-stone-200'
            }`}
          >
            <span>{g.icon}</span>
            <span>{g.label}</span>
          </button>
        ))}
      </div>

      <div className="flex flex-wrap items-center gap-6">
        <label className="flex items-center gap-2">
          <span className="text-sm text-stone-600">Calorie limit</span>
          <input
            type="number"
            value={calorieLimit}
            onChange={(e) => onCalorieLimitChange(Number(e.target.value) || 2000)}
            className="w-24 px-3 py-1.5 rounded-lg border border-stone-200 text-sm"
            min={800}
            max={4000}
            step={100}
          />
        </label>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="text-sm text-buffet-600 hover:text-buffet-700 font-medium"
        >
          {showFilters ? '−' : '+'} Allergies & Dietary
        </button>
      </div>

      {showFilters && (
        <div className="mt-4 pt-4 border-t border-stone-100 flex flex-wrap gap-4">
          <label className="flex flex-col gap-1">
            <span className="text-xs text-stone-500">Allergies (comma-separated)</span>
            <input
              type="text"
              placeholder="e.g. nuts, shellfish"
              value={filters.allergies.join(', ')}
              onChange={(e) =>
                onFiltersChange({
                  ...filters,
                  allergies: e.target.value.split(',').map((s) => s.trim()).filter(Boolean),
                })
              }
              className="px-3 py-1.5 rounded-lg border border-stone-200 text-sm w-48"
            />
          </label>
          <label className="flex flex-col gap-1">
            <span className="text-xs text-stone-500">Dietary</span>
            <select
              value={filters.dietary[0] || ''}
              onChange={(e) =>
                onFiltersChange({
                  ...filters,
                  dietary: e.target.value ? [e.target.value] : [],
                })
              }
              className="px-3 py-1.5 rounded-lg border border-stone-200 text-sm"
            >
              <option value="">None</option>
              <option value="vegan">Vegan</option>
              <option value="vegetarian">Vegetarian</option>
              <option value="halal">Halal</option>
            </select>
          </label>
        </div>
      )}
    </div>
  )
}
