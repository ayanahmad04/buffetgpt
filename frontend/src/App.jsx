import { useState } from 'react'
import { ImageUpload } from './components/ImageUpload'
import { ManualInput } from './components/ManualInput'
import { StrategyResults } from './components/StrategyResults'
import { GoalSelector } from './components/GoalSelector'

const MODES = { image: 'image', manual: 'manual' }

export default function App() {
  const [mode, setMode] = useState(MODES.image)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [goal, setGoal] = useState('enjoyment_first')
  const [calorieLimit, setCalorieLimit] = useState(2000)
  const [filters, setFilters] = useState({ allergies: [], dietary: [] })

  const runAnalysis = async (fn) => {
    setError(null)
    setResult(null)
    setLoading(true)
    try {
      const data = await fn({
        goal,
        calorie_limit: calorieLimit,
        allergies: filters.allergies,
        dietary_filters: filters.dietary,
      })
      setResult(data)
    } catch (e) {
      setError(e.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-stone-50 to-orange-50">
      {/* Header */}
      <header className="border-b border-stone-200/80 bg-white/70 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 py-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="font-display text-2xl sm:text-3xl font-bold text-buffet-800 tracking-tight">
              BuffetGPT
            </h1>
            <p className="text-sm text-stone-500 mt-0.5">
              AI-powered buffet eating strategy
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setMode(MODES.image)}
              className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
                mode === MODES.image
                  ? 'bg-buffet-500 text-white shadow-md'
                  : 'bg-stone-100 text-stone-600 hover:bg-stone-200'
              }`}
            >
              📷 Upload Image
            </button>
            <button
              onClick={() => setMode(MODES.manual)}
              className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
                mode === MODES.manual
                  ? 'bg-buffet-500 text-white shadow-md'
                  : 'bg-stone-100 text-stone-600 hover:bg-stone-200'
              }`}
            >
              ✏️ Manual List
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-8">
        {/* Goal & filters */}
        <section className="mb-8 animate-fade-in">
          <GoalSelector
            goal={goal}
            onGoalChange={setGoal}
            calorieLimit={calorieLimit}
            onCalorieLimitChange={setCalorieLimit}
            filters={filters}
            onFiltersChange={setFilters}
          />
        </section>

        {/* Input area */}
        <section className="mb-10">
          {mode === MODES.image ? (
            <ImageUpload
              onAnalyze={runAnalysis}
              loading={loading}
              disabled={loading}
            />
          ) : (
            <ManualInput
              onAnalyze={runAnalysis}
              loading={loading}
              disabled={loading}
            />
          )}
        </section>

        {error && (
          <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 animate-slide-up">
            {error}
          </div>
        )}

        {result && (
          <StrategyResults data={result} className="animate-slide-up" />
        )}
      </main>

      <footer className="border-t border-stone-200/80 mt-16 py-6 text-center text-sm text-stone-500">
        BuffetGPT — Computer vision, nutrition science & stomach physics
      </footer>
    </div>
  )
}
