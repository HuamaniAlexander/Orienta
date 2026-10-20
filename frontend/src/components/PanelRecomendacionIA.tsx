import { useState } from 'react'
import type { FormEvent } from 'react'
import { useRecurso } from '../hooks/useRecurso'
import { TarjetaCarrera } from './TarjetaCarrera'
import { Icono } from './Icono'
import type { NombreIcono } from './Icono'
import type { Carrera } from '../domain/carrera'
import { urlFuenteSegura } from '../domain/presentacion'

interface Analisis {
  entrenamientoRecomendaciones?: { estado: string; mensaje: string }
  analisisCriterios: {
    clave: string; etiqueta: string; valorIzquierda: string; valorDerecha: string; etiquetaIzquierda: string; etiquetaDerecha: string
    relacion: 'same' | 'different' | 'missing'; explicacion: string
    recomendacion: string; motivo: string; advertencias: string[]
  }[]
  tipoExplicacion: string
  umbralCalidad: number
  calidadAprobada: boolean
  evaluacionesModelos: { nombre: string; accuracy: number; precision_macro: number;
    recall_macro: number; f1_macro: number; validation_distance_to_ideal: number | null }[]
  prediccion: string
  contrasteCatalogo: string
  areas: string[]
  fuentesAreas: (string | null)[]
  coincideCatalogo: boolean
  nombreModelo: string
  versionModelo: string
  metricas: Record<string, number>
  exactitudReferencia: number
  paresEntrenamiento: number
  paresPrueba: number
  limitaciones: string[]
  siguientesPasos: string[]
  recomendaciones: Carrera[]
}
function ResultadoAnalisis({ identificadores, nombres, preferencias }: { identificadores: string[]; nombres: string[]; preferencias: Record<string, string | number> }) {
  const { resultado, reintentar } = useRecurso<Analisis>('/comparaciones/analisis', { idsCarreras: identificadores, preferencias })
  if (resultado.estado === 'loading') return <div className="analysis-loading" role="status"><span className="spinner" />
    <h3>Analizando las alternativas…</h3><p>El modelo está procesando sus características académicas.</p></div>
  if (resultado.estado === 'error') return <div className="analysis-error" role="alert"><Icono nombre="info" />
    <h3>El análisis IA no está disponible</h3><p>Puedes seguir consultando la comparación y sus fuentes.</p>
    <button className="button" onClick={reintentar}>Reintentar análisis</button></div>
  const datos = resultado.datos
  const iconos: Record<string, NombreIcono> = { duration: 'clock', modality: 'screen', location: 'pin',
    cost: 'coins', requirements: 'book', employment: 'briefcase' }
  return <div className="analysis-result">
    <section className="six-criteria-analysis" aria-labelledby="six-criteria-title">
      <div className="analysis-introduction"><p className="eyebrow">LAS DIFERENCIAS QUE IMPORTAN</p>
        <h3 id="six-criteria-title">Seis criterios para tomar una decisión informada</h3>
        <p>Explicación estructurada a partir de las fichas: qué cambia, qué implica y qué conviene confirmar.</p></div>
      {datos.entrenamientoRecomendaciones && <p className="model-limitation" role="status">{datos.entrenamientoRecomendaciones.mensaje}</p>}
      <div className="criterion-analysis-grid">{datos.analisisCriterios.map(elemento =>
        <article key={elemento.clave} className={`criterion-analysis criterion-${elemento.relacion}`}>
          <header><span className="fact-icon"><Icono nombre={iconos[elemento.clave] || 'info'} /></span>
            <h4>{elemento.etiqueta}</h4><span className="criterion-status">{elemento.relacion === 'same'
              ? 'Mismo dato' : elemento.relacion === 'missing' ? 'Falta información' : 'Hay diferencias'}</span></header>
          <dl className="criterion-values"><div><dt>{elemento.etiquetaIzquierda || nombres[0]}</dt><dd>{elemento.valorIzquierda}</dd></div>
            <div><dt>{elemento.etiquetaDerecha || nombres[1]}</dt><dd>{elemento.valorDerecha}</dd></div></dl>
          <p className="criterion-explanation">{elemento.explicacion}</p>
          <div className="criterion-advice"><Icono nombre="compass" /><p><strong>Para decidir</strong>{elemento.recomendacion}</p></div>
          <p className="criterion-reason"><strong>Por qué: </strong>{elemento.motivo}</p>
          {elemento.advertencias.length > 0 && <details className="criterion-caveats"><summary>Condiciones de estos datos</summary>
            <ul>{elemento.advertencias.map((texto, indice) => <li key={indice}>{texto}</li>)}</ul></details>}
        </article>)}</div>
    </section>
    {datos.evaluacionesModelos.length > 0 && <details className="model-audit"><summary><Icono nombre="screen" />Evaluación de los modelos de contraste de áreas</summary>
    <p className="model-limitation">Esta evaluación corresponde al clasificador de áreas, no mide la calidad de las explicaciones de los seis criterios.</p>
    <div className="analysis-outcomes"><article><p className="eyebrow">DATOS DEL CATÁLOGO</p>
      <h3>{datos.contrasteCatalogo}</h3><p>{datos.areas.join(' · ')}</p>
      <div className="analysis-sources">{datos.fuentesAreas.map((valor, i) => {
        const direccion = urlFuenteSegura(valor)
        return direccion ? <a key={i} href={direccion} target="_blank" rel="noopener noreferrer">Fuente: {nombres[i]} <Icono nombre="external" /></a> : <span key={i}>Fuente no registrada</span>
      })}</div></article>
      <article><p className="eyebrow">ESTADO DEL CLASIFICADOR</p><h3>{datos.calidadAprobada ? datos.prediccion : 'No habilitado para orientar decisiones'}</h3>
        <p>{datos.nombreModelo} · v{datos.versionModelo}</p><span className="tag">Clasificador experimental</span></article></div>
    {datos.calidadAprobada && !datos.coincideCatalogo && <p className="model-disagreement" role="status"><Icono nombre="info" />
      El modelo discrepa del catálogo. Conserva las áreas documentadas como referencia.</p>}
    <p className="model-limitation">Este modelo distingue áreas académicas; no evalúa tus aptitudes ni determina qué carrera debes elegir.</p>
    {!datos.calidadAprobada && <p className="model-disagreement"><Icono nombre="info" />No cumple el umbral del {(datos.umbralCalidad * 100).toFixed(0)}% en las cuatro métricas de prueba. Su predicción no se utiliza para recomendar una carrera.</p>}
    {datos.metricas.accuracy <= datos.exactitudReferencia && <p className="model-limitation">En la evaluación, el modelo no superó una referencia básica. Da prioridad a las áreas y fuentes del catálogo.</p>}
    <details className="model-details"><summary>Ver evaluación y limitaciones del modelo</summary>
      <div className="metric-grid">{[['Accuracy', 'accuracy'], ['Precisión macro', 'precision_macro'],
        ['Recall macro', 'recall_macro'], ['F1 macro', 'f1_macro']].map(([etiqueta, clave]) => <div key={clave}>
          <strong>{(100 * datos.metricas[clave]).toFixed(1)}%</strong><span>{etiqueta}</span></div>)}</div>
      <p>Evaluado con {datos.paresPrueba} pares de prueba, separados de los {datos.paresEntrenamiento} pares de entrenamiento por grupos de carreras.</p>
      <p>Referencia de clase mayoritaria: {(100 * datos.exactitudReferencia).toFixed(1)}% de accuracy.
        {datos.metricas.accuracy <= datos.exactitudReferencia ? ' El modelo no supera esta referencia; interpreta su resultado con cautela.' : ''}</p>
      <ul>{datos.limitaciones.map(elemento => <li key={elemento}>{elemento}</li>)}</ul>
      <h4>Comparación de los tres algoritmos</h4>
      <p>Se selecciona la menor distancia a 1 en las cuatro métricas de validación. Los resultados de prueba se reservan para evaluación independiente.</p>
      <div className="algorithm-grid">{datos.evaluacionesModelos.map(modelo => <article key={modelo.nombre}>
        <h5>{modelo.nombre}{modelo.nombre === datos.nombreModelo && <span className="tag">Seleccionado</span>}</h5>
        <dl>{[['Accuracy', modelo.accuracy], ['Precisión macro', modelo.precision_macro],
          ['Recall macro', modelo.recall_macro], ['F1 macro', modelo.f1_macro]].map(([etiqueta, valor]) =>
          <div key={etiqueta}><dt>{etiqueta}</dt><dd>{(Number(valor) * 100).toFixed(1)}%</dd></div>)}</dl>
      </article>)}</div>
    </details>
    </details>
    }
    {datos.recomendaciones.length > 0 && <section className="related-options"><h3>Amplía tus alternativas</h3>
      <p>Opciones relacionadas por similitud de su contenido académico, sin evaluar afinidad personal.</p>
      <div className="career-grid">{datos.recomendaciones.map(c => <TarjetaCarrera key={c.id} carrera={c} />)}</div></section>}
  </div>
}
export function PanelRecomendacionIA({ identificadores, nombres = [] }: { identificadores: string[]; nombres?: string[] }) {
  const [activo, establecerActivo] = useState(false)
  const [preferencias, establecerPreferencias] = useState<Record<string, string | number>>({})
  function analizar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault()
    const valores: Record<string, string | number> = {}
    for (const [clave, valor] of new FormData(evento.currentTarget)) {
      if (typeof valor === 'string' && valor.trim()) {
        valores[clave] = ['budget_pen', 'max_duration_months'].includes(clave) ? Number(valor) : valor.trim()
      }
    }
    establecerPreferencias(valores)
    establecerActivo(true)
  }
  return <section className="analysis-panel" aria-labelledby="analysis-title"><div className="analysis-header">
    <span className="fact-icon"><Icono nombre="sparkles" /></span><div><h2 id="analysis-title">Analiza las dos carreras en detalle</h2>
      <p>Contrasta seis criterios, comprende sus diferencias y revisa recomendaciones concretas para decidir.</p></div>
    </div>
    <form className="analysis-preferences" onSubmit={analizar}>
      <p>Preferencias opcionales para valorar las diferencias. Los modelos aprendidos requieren evaluación aprobada.</p>
      <div className="preferences-grid">
        <label>Presupuesto mensual (S/)<input name="budget_pen" type="number" min="0" step="0.01" /></label>
        <label>Duración máxima (meses)<input name="max_duration_months" type="number" min="1" max="240" step="1" /></label>
        <label>Modalidad preferida<select name="modality"><option value="">Sin preferencia</option><option>Presencial</option><option>Virtual</option><option>Semipresencial</option><option>A distancia</option></select></label>
        <label>Sede o zona preferida<input name="location" maxLength={200} /></label>
        <label>Requisitos que cumples<input name="requirements_met" maxLength={500} /></label>
        <label>Actividades laborales de interés<input name="employment_interests" maxLength={500} /></label>
      </div>
      <button className="button primary" type="submit">{activo ? 'Actualizar análisis' : 'Analizar con IA'} <Icono nombre="arrow" /></button>
    </form>
    {activo && <ResultadoAnalisis key={JSON.stringify(preferencias)} identificadores={identificadores} nombres={nombres} preferencias={preferencias} />}
  </section>
}
