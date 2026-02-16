/**
 * BuffetGPT API client
 */

// Use relative path for proxy (Vite dev + Docker nginx)
const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

export async function analyzeBuffetImage(file, options = {}) {
  const formData = new FormData();
  formData.append('image', file);
  formData.append('goal', options.goal || 'enjoyment_first');
  if (options.calorie_limit) formData.append('calorie_limit', options.calorie_limit);
  if (options.allergies?.length) formData.append('allergies', options.allergies.join(','));
  if (options.dietary_filters?.length) formData.append('dietary_filters', options.dietary_filters.join(','));

  const res = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Analysis failed');
  }
  return res.json();
}

export async function analyzeManualDishes(dishes, options = {}) {
  const res = await fetch(`${API_BASE}/strategy/manual`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      dishes,
      goal: options.goal || 'enjoyment_first',
      calorie_limit: options.calorie_limit,
      allergies: options.allergies || [],
      dietary_filters: options.dietary_filters || [],
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Strategy generation failed');
  }
  return res.json();
}

export async function healthCheck() {
  const res = await fetch(`${API_BASE}/health`);
  return res.ok ? res.json() : null;
}
