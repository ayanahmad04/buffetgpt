import { useState, useRef } from 'react'
import { analyzeBuffetImage } from '../api'

export function ImageUpload({ onAnalyze, loading, disabled }) {
  const [preview, setPreview] = useState(null)
  const [file, setFile] = useState(null)
  const inputRef = useRef(null)

  const handleFile = (e) => {
    const f = e.target.files?.[0]
    if (!f || !f.type.startsWith('image/')) return
    setFile(f)
    const reader = new FileReader()
    reader.onload = () => setPreview(reader.result)
    reader.readAsDataURL(f)
  }

  const handleSubmit = async () => {
    if (!file) return
    await onAnalyze((opts) => analyzeBuffetImage(file, opts))
    setFile(null)
    setPreview(null)
  }

  return (
    <div className="rounded-2xl bg-white/80 backdrop-blur border border-stone-200/80 shadow-sm p-8">
      <h2 className="font-display font-semibold text-stone-800 mb-2">Upload Buffet Image</h2>
      <p className="text-sm text-stone-500 mb-6">
        Take or upload a photo of the buffet. We&apos;ll detect dishes and build your strategy.
      </p>

      <div
        onClick={() => inputRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all ${
          preview
            ? 'border-buffet-300 bg-buffet-50/50'
            : 'border-stone-200 hover:border-buffet-300 hover:bg-stone-50'
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          onChange={handleFile}
          className="hidden"
        />
        {preview ? (
          <div className="space-y-4">
            <img
              src={preview}
              alt="Preview"
              className="max-h-48 max-w-full mx-auto rounded-lg object-contain"
            />
            <p className="text-sm text-stone-600">{file?.name}</p>
          </div>
        ) : (
          <div className="text-stone-400">
            <div className="text-4xl mb-2">📷</div>
            <p className="font-medium text-stone-500">Click to select image</p>
            <p className="text-xs mt-1">JPEG, PNG</p>
          </div>
        )}
      </div>

      <div className="flex gap-3 mt-6">
        <button
          onClick={handleSubmit}
          disabled={disabled || !file}
          className="px-6 py-3 rounded-xl bg-buffet-500 text-white font-semibold hover:bg-buffet-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          {loading ? 'Analyzing…' : 'Analyze Buffet'}
        </button>
        {preview && (
          <button
            onClick={() => { setFile(null); setPreview(null) }}
            disabled={disabled}
            className="px-4 py-3 rounded-xl border border-stone-200 text-stone-600 hover:bg-stone-50"
          >
            Clear
          </button>
        )}
      </div>
    </div>
  )
}
