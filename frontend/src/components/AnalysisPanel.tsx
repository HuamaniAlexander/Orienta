import { useState } from 'react'
import type { FormEvent } from 'react'
import { useResource } from '../application/useResource'
import { CareerCard } from './CareerCard'
import { Icon } from './Icon'
import type { IconName } from './Icon'
import type { Career } from '../domain/career'
import { safeSourceUrl } from '../domain/presentation'

interface Analysis {
  recommendation_training?: { status: string; message: string }
  criteria_analysis: {
    key: string; label: string; left_value: string; right_value: string; left_label: string; right_label: string
    relationship: 'same' | 'different' | 'missing'; explanation: string
    recommendation: string; reason: string; caveats: string[]
  }[]
  explanation_kind: string
  quality_target: number
  quality_approved: boolean
  model_evaluations: { name: string; accuracy: number; precision_macro: number;
    recall_macro: number; f1_macro: number; validation_distance_to_ideal: number | null }[]
  prediction: string
  catalog_contrast: string
  areas: string[]
  area_sources: (string | null)[]
  agrees_with_catalog: boolean
  model_name: string
  model_version: string
  metrics: Record<string, number>
  baseline_accuracy: number
  training_pairs: number
  test_pairs: number
  limitations: string[]
  next_steps: string[]
  recommendations: Career[]
}
function AnalysisResult({ ids, names, preferences }: { ids: string[]; names: string[]; preferences: Record<string, string | number> }) {
  const { result, retry } = useResource<Analysis>('/comparaciones/analisis', { career_ids: ids, preferences })
  if (result.status === 'loading') return <div className="analysis-loading" role="status"><span className="spinner" />
    <h3>Analizando las alternativas…</h3><p>El modelo está procesando sus características académicas.</p></div>
  if (result.status === 'error') return <div className="analysis-error" role="alert"><Icon name="info" />
    <h3>El análisis IA no está disponible</h3><p>Puedes seguir consultando la comparación y sus fuentes.</p>
    <button className="button" onClick={retry}>Reintentar análisis</button></div>
  const data = result.data
  const icons: Record<string, IconName> = { duration: 'clock', modality: 'screen', location: 'pin',
    cost: 'coins', requirements: 'book', employment: 'briefcase' }
  return <div className="analysis-result">
    <section className="six-criteria-analysis" aria-labelledby="six-criteria-title">
      <div className="analysis-introduction"><p className="eyebrow">LAS DIFERENCIAS QUE IMPORTAN</p>
        <h3 id="six-criteria-title">Seis criterios para tomar una decisión informada</h3>
        <p>Explicación estructurada a partir de las fichas: qué cambia, qué implica y qué conviene confirmar.</p></div>
      {data.recommendation_training && <p className="model-limitation" role="status">{data.recommendation_training.message}</p>}
      <div className="criterion-analysis-grid">{data.criteria_analysis.map(item =>
        <article key={item.key} className={`criterion-analysis criterion-${item.relationship}`}>
          <header><span className="fact-icon"><Icon name={icons[item.key] || 'info'} /></span>
            <h4>{item.label}</h4><span className="criterion-status">{item.relationship === 'same'
              ? 'Mismo dato' : item.relationship === 'missing' ? 'Falta información' : 'Hay diferencias'}</span></header>
          <dl className="criterion-values"><div><dt>{item.left_label || names[0]}</dt><dd>{item.left_value}</dd></div>
            <div><dt>{item.right_label || names[1]}</dt><dd>{item.right_value}</dd></div></dl>
          <p className="criterion-explanation">{item.explanation}</p>
          <div className="criterion-advice"><Icon name="compass" /><p><strong>Para decidir</strong>{item.recommendation}</p></div>
          <p className="criterion-reason"><strong>Por qué: </strong>{item.reason}</p>
          {item.caveats.length > 0 && <details className="criterion-caveats"><summary>Condiciones de estos datos</summary>
            <ul>{item.caveats.map((text, index) => <li key={index}>{text}</li>)}</ul></details>}
        </article>)}</div>
    </section>
    <details className="model-audit"><summary><Icon name="screen" />Evaluación de los modelos de contraste de áreas</summary>
    <p className="model-limitation">Esta evaluación corresponde al clasificador de áreas, no mide la calidad de las explicaciones de los seis criterios.</p>
    <div className="analysis-outcomes"><article><p className="eyebrow">DATOS DEL CATÁLOGO</p>
      <h3>{data.catalog_contrast}</h3><p>{data.areas.join(' · ')}</p>
      <div className="analysis-sources">{data.area_sources.map((value, i) => {
        const url = safeSourceUrl(value)
        return url ? <a key={i} href={url} target="_blank" rel="noopener noreferrer">Fuente: {names[i]} <Icon name="external" /></a> : <span key={i}>Fuente no registrada</span>
      })}</div></article>
      <article><p className="eyebrow">ESTADO DEL CLASIFICADOR</p><h3>{data.quality_approved ? data.prediction : 'No habilitado para orientar decisiones'}</h3>
        <p>{data.model_name} · v{data.model_version}</p><span className="tag">Clasificador experimental</span></article></div>
    {data.quality_approved && !data.agrees_with_catalog && <p className="model-disagreement" role="status"><Icon name="info" />
      El modelo discrepa del catálogo. Conserva las áreas documentadas como referencia.</p>}
    <p className="model-limitation">Este modelo distingue áreas académicas; no evalúa tus aptitudes ni determina qué carrera debes elegir.</p>
    {!data.quality_approved && <p className="model-disagreement"><Icon name="info" />No cumple el umbral del {(data.quality_target * 100).toFixed(0)}% en las cuatro métricas de prueba. Su predicción no se utiliza para recomendar una carrera.</p>}
    {data.metrics.accuracy <= data.baseline_accuracy && <p className="model-limitation">En la evaluación, el modelo no superó una referencia básica. Da prioridad a las áreas y fuentes del catálogo.</p>}
    <details className="model-details"><summary>Ver evaluación y limitaciones del modelo</summary>
      <div className="metric-grid">{[['Accuracy', 'accuracy'], ['Precisión macro', 'precision_macro'],
        ['Recall macro', 'recall_macro'], ['F1 macro', 'f1_macro']].map(([label, key]) => <div key={key}>
          <strong>{(100 * data.metrics[key]).toFixed(1)}%</strong><span>{label}</span></div>)}</div>
      <p>Evaluado con {data.test_pairs} pares de prueba, separados de los {data.training_pairs} pares de entrenamiento por grupos de carreras.</p>
      <p>Referencia de clase mayoritaria: {(100 * data.baseline_accuracy).toFixed(1)}% de accuracy.
        {data.metrics.accuracy <= data.baseline_accuracy ? ' El modelo no supera esta referencia; interpreta su resultado con cautela.' : ''}</p>
      <ul>{data.limitations.map(item => <li key={item}>{item}</li>)}</ul>
      <h4>Comparación de los tres algoritmos</h4>
      <p>Se selecciona la menor distancia a 1 en las cuatro métricas de validación. Los resultados de prueba se reservan para evaluación independiente.</p>
      <div className="algorithm-grid">{data.model_evaluations.map(model => <article key={model.name}>
        <h5>{model.name}{model.name === data.model_name && <span className="tag">Seleccionado</span>}</h5>
        <dl>{[['Accuracy', model.accuracy], ['Precisión macro', model.precision_macro],
          ['Recall macro', model.recall_macro], ['F1 macro', model.f1_macro]].map(([label, value]) =>
          <div key={label}><dt>{label}</dt><dd>{(Number(value) * 100).toFixed(1)}%</dd></div>)}</dl>
      </article>)}</div>
    </details>
    </details>
    {data.recommendations.length > 0 && <section className="related-options"><h3>Amplía tus alternativas</h3>
      <p>Opciones relacionadas por similitud de su contenido académico, sin evaluar afinidad personal.</p>
      <div className="career-grid">{data.recommendations.map(c => <CareerCard key={c.id} career={c} />)}</div></section>}
  </div>
}
export function AnalysisPanel({ ids, names = [] }: { ids: string[]; names?: string[] }) {
  const [active, setActive] = useState(false)
  const [preferences, setPreferences] = useState<Record<string, string | number>>({})
  function analyze(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const values: Record<string, string | number> = {}
    for (const [key, value] of new FormData(event.currentTarget)) {
      if (typeof value === 'string' && value.trim()) {
        values[key] = ['budget_pen', 'max_duration_months'].includes(key) ? Number(value) : value.trim()
      }
    }
    setPreferences(values)
    setActive(true)
  }
  return <section className="analysis-panel" aria-labelledby="analysis-title"><div className="analysis-header">
    <span className="fact-icon"><Icon name="sparkles" /></span><div><h2 id="analysis-title">Analiza las dos carreras en detalle</h2>
      <p>Contrasta seis criterios, comprende sus diferencias y revisa recomendaciones concretas para decidir.</p></div>
    </div>
    <form className="analysis-preferences" onSubmit={analyze}>
      <p>Preferencias opcionales para valorar las diferencias. Los modelos aprendidos requieren evaluación aprobada.</p>
      <div className="preferences-grid">
        <label>Presupuesto mensual (S/)<input name="budget_pen" type="number" min="0" step="0.01" /></label>
        <label>Duración máxima (meses)<input name="max_duration_months" type="number" min="1" max="240" step="1" /></label>
        <label>Modalidad preferida<select name="modality"><option value="">Sin preferencia</option><option>Presencial</option><option>Virtual</option><option>Semipresencial</option><option>A distancia</option></select></label>
        <label>Sede o zona preferida<input name="location" maxLength={200} /></label>
        <label>Requisitos que cumples<input name="requirements_met" maxLength={500} /></label>
        <label>Actividades laborales de interés<input name="employment_interests" maxLength={500} /></label>
      </div>
      <button className="button primary" type="submit">{active ? 'Actualizar análisis' : 'Analizar con IA'} <Icon name="arrow" /></button>
    </form>
    {active && <AnalysisResult key={JSON.stringify(preferences)} ids={ids} names={names} preferences={preferences} />}
  </section>
}
