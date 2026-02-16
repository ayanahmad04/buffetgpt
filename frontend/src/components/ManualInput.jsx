import { useState } from 'react'
import { analyzeManualDishes } from '../api'

const DEFAULT_DISHES = [
  { name: 'Mixed Salad', estimated_grams: 80 },
  { name: 'Grilled Chicken', estimated_grams: 150 },
  { name: 'Rice', estimated_grams: 120 },
  { name: 'Soup', estimated_grams: 200 },
  { name: 'Dessert', estimated_grams: 80 },
]

export function ManualInput({ onAnalyze, loading, disabled }) {
  const [dishes, setDishes] = useState(DEFAULT_DISHES)

  const addDish = () => {
    setDishes([...dishes, { name: '', estimated_grams: 100 }])
  }

  const updateDish = (i, field, value) => {
    const next = [...dishes]
    next[i] = { ...next[i], [field]: field === 'estimated_grams' ? Number(value) || 100 : value }
    setDishes(next)
  }

  const removeDish = (i) => {
    setDishes(dishes.filter((_, j) => j !== i))
  }

  const handleSubmit = async () => {
    const valid = dishes.filter((d) => d.name.trim())
    if (!valid.length) return
    await onAnalyze((opts) =>
      analyzeManualDishes(
        valid.map((d) => ({ name: d.name.trim(), estimated_grams: d.estimated_grams })),
        opts
      )
    )
  }

  return (
    <div className="rounded-2xl bg-white/80 backdrop-blur border border-stone-200/80 shadow-sm p-8">
      <h2 className="font-display font-semibold text-stone-800 mb-2">Manual Dish List</h2>
      <p className="text-sm text-stone-500 mb-6">
        Enter the dishes you see at the buffet. We&apos;ll build your strategy.
      </p>

      <div className="space-y-3 max-h-64 overflow-y-auto">
        {dishes.map((d, i) => (
          <div key={i} className="flex gap-3 items-center">
            <input
              type="text"
              placeholder="Dish name"
              value={d.name}
              onChange={(e) => updateDish(i, 'name', e.target.value)}
              className="flex-1 px-4 py-2.5 rounded-lg border border-stone-200 text-sm"
            />
            <input
              type="number"
              placeholder="g"
              value={d.estimated_grams}
              onChange={(e) => updateDish(i, 'estimated_grams', e.target.value)}
              className="w-20 px-3 py-2.5 rounded-lg border border-stone-200 text-sm"
              min={20}
              max={500}
            />
            <button
              onClick={() => removeDish(i)}
              className="p-2 text-stone-400 hover:text-red-500"
              title="Remove"
            >
              ×
            </button>
          </div>
        ))}
      </div>

      <div className="flex gap-3 mt-6">
        <button
          onClick={addDish}
          className="px-4 py-2 rounded-lg border border-stone-200 text-stone-600 hover:bg-stone-50 text-sm"
        >
          + Add dish
        </button>
        <button
          onClick={handleSubmit}
          disabled={disabled || !dishes.some((d) => d.name.trim())}
          className="px-6 py-3 rounded-xl bg-buffet-500 text-white font-semibold hover:bg-buffet-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          {loading ? 'Generating…' : 'Get Strategy'}
        </button>
      </div>
    </div>
  )
}
