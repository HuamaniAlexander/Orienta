import { useState } from 'react'
import { useResource } from '../application/useResource'
import { CareerCard } from './CareerCard'
import { Icon } from './Icon'
import type { Career } from '../domain/career'
import { safeSourceUrl } from '../domain/presentation'

interface Analysis {
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
function AnalysisResult({ ids }: { ids: string[] }) {
  const { result, retry } = useResource<Analysis>('/comparaciones/analisis', { career_ids: ids })
  if (result.status === 'loading') return <div className="analysis-loading" role="status"><span className="spinner" />
    <h3>Analizando las alternativas…</h3><p>El modelo está procesando sus características académicas.</p></div>
  if (result.status === 'error') return <div className="analysis-error" role="alert"><Icon name="info" />
    <h3>El análisis IA no está disponible</h3><p>Puedes seguir consultando la comparación y sus fuentes.</p>
    <button className="button" onClick={retry}>Reintentar análisis</button></div>
  const data = result.data
  return <div className="analysis-result">
    <div className="analysis-outcomes"><article><p className="eyebrow">DATOS DEL CATÁLOGO</p>
      <h3>{data.catalog_contrast}</h3><p>{data.areas.join(' · ')}</p>
      <div className="analysis-sources">{data.area_sources.map((value, i) => {
        const url = safeSourceUrl(value)
        return url ? <a key={i} href={url} target="_blank" rel="noopener noreferrer">Fuente {i ? 'B' : 'A'} <Icon name="external" /></a> : <span key={i}>Fuente no registrada</span>
      })}</div></article>
      <article><p className="eyebrow">PREDICCIÓN DEL MODELO</p><h3>{data.prediction}</h3>
        <p>{data.model_name} · v{data.model_version}</p><span className="tag">Clasificador experimental</span></article></div>
    {!data.agrees_with_catalog && <p className="model-disagreement" role="status"><Icon name="info" />
      El modelo discrepa del catálogo. Conserva las áreas documentadas como referencia.</p>}
    <p className="model-limitation">Este modelo distingue áreas académicas; no evalúa tus aptitudes ni determina qué carrera debes elegir.</p>
    {data.metrics.accuracy <= data.baseline_accuracy && <p className="model-limitation">En la evaluación, el modelo no superó una referencia básica. Da prioridad a las áreas y fuentes del catálogo.</p>}
    <details className="model-details"><summary>Ver evaluación y limitaciones del modelo</summary>
      <div className="metric-grid">{[['Accuracy', 'accuracy'], ['Precisión macro', 'precision_macro'],
        ['Recall macro', 'recall_macro'], ['F1 macro', 'f1_macro']].map(([label, key]) => <div key={key}>
          <strong>{(100 * data.metrics[key]).toFixed(1)}%</strong><span>{label}</span></div>)}</div>
      <p>Evaluado con {data.test_pairs} pares de prueba, separados de los {data.training_pairs} pares de entrenamiento por grupos de carreras.</p>
      <p>Referencia de clase mayoritaria: {(100 * data.baseline_accuracy).toFixed(1)}% de accuracy.
        {data.metrics.accuracy <= data.baseline_accuracy ? ' El modelo no supera esta referencia; interpreta su resultado con cautela.' : ''}</p>
      <ul>{data.limitations.map(item => <li key={item}>{item}</li>)}</ul>
    </details>
    <section className="next-steps"><h3>Aspectos que conviene revisar</h3><p>Orientaciones basadas en los criterios de la comparación.</p>
      <ul>{data.next_steps.map(item => <li key={item}><Icon name="check" />{item}</li>)}</ul></section>
    {data.recommendations.length > 0 && <section className="related-options"><h3>Amplía tus alternativas</h3>
      <p>Opciones relacionadas por similitud de su contenido académico, sin evaluar afinidad personal.</p>
      <div className="career-grid">{data.recommendations.map(c => <CareerCard key={c.id} career={c} />)}</div></section>}
  </div>
}
export function AnalysisPanel({ ids }: { ids: string[] }) {
  const [active, setActive] = useState(false)
  return <section className="analysis-panel" aria-labelledby="analysis-title"><div className="analysis-header">
    <span className="fact-icon"><Icon name="compass" /></span><div><h2 id="analysis-title">Comprende el contraste con IA</h2>
      <p>Explora el resultado de un modelo entrenado y alternativas con contenido relacionado.</p></div>
    {!active && <button className="button primary" onClick={() => setActive(true)}>Analizar con IA <Icon name="arrow" /></button>}</div>
    {active && <AnalysisResult ids={ids} />}
  </section>
}
