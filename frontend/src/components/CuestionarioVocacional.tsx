import { useRef, useState, useEffect } from 'react'
import { useRecurso } from '../hooks/useRecurso'
import { consultarApi } from '../adapters/api'
import { Icono } from './Icono'
import type { Cuestionario, ResultadoVocacional } from '../domain/vocacional'

function participanteAnonimo() {
  try {
    const anterior = sessionStorage.getItem('orienta-participante')
    if (anterior && /^[0-9a-f-]{36}$/i.test(anterior)) return anterior
    const nuevo = crypto.randomUUID(); sessionStorage.setItem('orienta-participante', nuevo); return nuevo
  } catch { return crypto.randomUUID() }
}

function FormularioVocacional({ cuestionario, identificadores, cerrar }: {
  cuestionario: Cuestionario; identificadores: string[]; cerrar: () => void
}) {
  const [paso, establecerPaso] = useState(0)
  const [respuestas, establecerRespuestas] = useState<Record<string, string>>({})
  const [presupuesto, establecerPresupuesto] = useState('')
  const [duracion, establecerDuracion] = useState('')
  const [modalidad, establecerModalidad] = useState('')
  const [eleccion, establecerEleccion] = useState('')
  const [consentimiento, establecerConsentimiento] = useState(false)
  const [mayorEdad, establecerMayorEdad] = useState(false)
  const [resultado, establecerResultado] = useState<ResultadoVocacional | null>(null)
  const [cargando, establecerCargando] = useState(false)
  const [error, establecerError] = useState('')
  const [yaAnalizado, establecerYaAnalizado] = useState(false)
  const captura = useRef(crypto.randomUUID())
  const controlador = useRef<AbortController | null>(null)
  const titulo = useRef<HTMLHeadingElement>(null)
  useEffect(() => {
    titulo.current?.focus({ preventScroll: true })
    titulo.current?.closest('.cuestionario-vocacional,.resultado-vocacional')?.scrollIntoView?.({ block: 'start' })
  }, [paso, resultado])
  useEffect(() => () => controlador.current?.abort(), [])
  const pregunta = cuestionario.preguntas[paso]
  const ultima = paso === cuestionario.preguntas.length - 1

  async function enviar() {
    establecerError('')
    const presupuestoNumero = presupuesto === '' ? undefined : Number(presupuesto)
    const duracionNumero = duracion === '' ? undefined : Number(duracion)
    if (presupuestoNumero !== undefined && (!Number.isFinite(presupuestoNumero) || presupuestoNumero < 0 || presupuestoNumero > 100000)
      || duracionNumero !== undefined && (!Number.isInteger(duracionNumero) || duracionNumero < 1 || duracionNumero > 240)) {
      establecerError('Revisa el presupuesto y la duración: deben estar dentro de los límites indicados.'); return
    }
    if (consentimiento && !yaAnalizado && (!mayorEdad || !eleccion)) {
      establecerError('Para aportar datos confirma que eres mayor de edad y declara tu elección independiente. También puedes continuar sin aportar datos.'); return
    }
    const cuerpo = { idsProgramas: identificadores, version: cuestionario.version, respuestas,
      preferencias: { presupuestoMaximo: presupuestoNumero, duracionMaxima: duracionNumero, modalidadPreferida: modalidad || undefined },
      captura: consentimiento && !yaAnalizado ? { idRegistro: captura.current, idParticipante: participanteAnonimo(),
        eleccion, consentimiento: true, mayorEdad: true } : undefined }
    controlador.current?.abort(); const actual = new AbortController(); controlador.current = actual
    establecerCargando(true)
    try {
      const datos = await consultarApi<ResultadoVocacional>('/v1/recomendaciones', actual.signal, cuerpo)
      if (!actual.signal.aborted) { establecerResultado(datos); establecerYaAnalizado(true) }
    } catch {
      if (!actual.signal.aborted) establecerError('No se pudo completar el análisis. Tus respuestas se conservan; vuelve a intentarlo.')
    } finally { if (!actual.signal.aborted) establecerCargando(false) }
  }

  if (resultado) return <section className="resultado-vocacional" aria-live="polite">
    <span className="etiqueta-seccion"><Icono nombre="sparkles" /> ORIENTA IA</span>
    <h3 ref={titulo} tabIndex={-1}>{resultado.estado === 'recomendacion' ? 'Tu recomendación personalizada'
      : resultado.estado === 'afinidad_similar' ? 'Ambas opciones presentan afinidad similar'
      : resultado.estado === 'informacion_insuficiente' ? 'Necesitamos conocer mejor tus preferencias'
      : resultado.estado === 'sin_interes' ? 'Puedes ampliar tu búsqueda' : 'Modelo de preferencias pendiente'}</h3>
    {resultado.recomendada && <p className="carrera-recomendada">{cuestionario.programas.find(p => p.id === resultado.recomendada)?.nombre}</p>}
    <p>{resultado.explicacion}</p>
    {resultado.factores.length > 0 && <div className="factores-vocacionales"><h4>Factores que favorecen la recomendación</h4>
      <ul>{resultado.factores.map(f => <li key={f.factor}><Icono nombre="check" />{f.descripcion}</li>)}</ul></div>}
    {resultado.factoresContrarios.length > 0 && <div className="factores-vocacionales"><h4>Qué favorece a la otra alternativa</h4>
      <ul>{resultado.factoresContrarios.map(f => <li key={f.factor}>{f.descripcion}</li>)}</ul></div>}
    {resultado.incertidumbres.map((aviso, indice) => <p className="nota-procedencia" key={indice}>{aviso}</p>)}
    {resultado.modelo && <details><summary>Modelo y significado del resultado</summary><p>{resultado.modelo.algoritmo} · {resultado.modelo.version}</p><p>{resultado.modelo.significadoMargen}</p></details>}
    {resultado.idRegistro && <p className="confirmacion-captura">Tu elección quedó registrada para revisión. Código: {resultado.idRegistro}. Conserva este código si solicitas retirar tu aporte.</p>}
    <p className="nota-procedencia">{cuestionario.aviso}</p>
    <div className="acciones-cuestionario"><button className="button primary" onClick={() => { establecerResultado(null); establecerPaso(0) }}>Modificar respuestas</button><button className="button" onClick={cerrar}>Volver a la comparación</button></div>
  </section>

  return <form className="cuestionario-vocacional" onSubmit={evento => { evento.preventDefault(); if (respuestas[pregunta.id]) { if (ultima) void enviar(); else establecerPaso(paso + 1) } }}>
    <div className="cabecera-cuestionario"><span className="etiqueta-seccion">{pregunta.seccion}</span><button className="button" type="button" disabled={cargando} onClick={cerrar}>Cerrar cuestionario</button></div>
    <p className="contador-pregunta">Pregunta {paso + 1} de {cuestionario.preguntas.length}</p>
    <progress max={cuestionario.preguntas.length} value={paso + (respuestas[pregunta.id] ? 1 : 0)} aria-label="Progreso del cuestionario" />
    <h3 ref={titulo} tabIndex={-1}>{pregunta.texto}</h3>
    {pregunta.contexto && <p className="contexto-pregunta">{pregunta.contexto}</p>}
    <fieldset disabled={cargando}><legend className="sr-only">{pregunta.texto}</legend>
      {pregunta.opciones.map(opcion => <label className={`opcion-vocacional ${respuestas[pregunta.id] === opcion.id ? 'elegida' : ''}`} key={opcion.id}>
        <input type="radio" name={pregunta.id} value={opcion.id} checked={respuestas[pregunta.id] === opcion.id} onChange={() => { establecerRespuestas({ ...respuestas, [pregunta.id]: opcion.id }); captura.current = crypto.randomUUID() }} />
        <span>{opcion.texto}</span>{respuestas[pregunta.id] === opcion.id && <Icono nombre="check" />}</label>)}
    </fieldset>
    {ultima && <div className="preferencias-vocacionales"><h4>Condiciones opcionales</h4><p>No solicitamos nombre, correo, edad ni otros datos personales.</p>
      <div className="preferences-grid"><label>Presupuesto máximo mensual (S/)<input type="number" min="0" max="100000" value={presupuesto} step="0.01" onChange={e => { establecerPresupuesto(e.target.value); captura.current = crypto.randomUUID() }} /></label>
        <label>Tiempo máximo de estudio (meses)<input type="number" min="1" max="240" value={duracion} onChange={e => { establecerDuracion(e.target.value); captura.current = crypto.randomUUID() }} /></label>
        <label>Modalidad preferida<select value={modalidad} onChange={e => { establecerModalidad(e.target.value); captura.current = crypto.randomUUID() }}><option value="">Sin preferencia</option><option>Presencial</option><option>Semipresencial</option><option>Virtual</option></select></label></div>
      {!yaAnalizado && <details className="consentimiento-captura"><summary>Aportar voluntariamente al entrenamiento</summary>
        <p>Solo personas mayores de edad. Tu aporte guarda respuestas, ofertas comparadas y elección con un identificador aleatorio; se revisará antes de entrenar. No es obligatorio y no cambia el acceso al análisis.</p>
        <label className="casilla-consentimiento"><input type="checkbox" checked={consentimiento} onChange={e => establecerConsentimiento(e.target.checked)} />Autorizo usar mis respuestas y mi elección para entrenar y evaluar ORIENTA.</label>
        {consentimiento && <><label className="casilla-consentimiento"><input type="checkbox" checked={mayorEdad} onChange={e => establecerMayorEdad(e.target.checked)} />Confirmo que tengo 18 años o más.</label>
          <label>Antes de ver un resultado, ¿qué opción elegirías?<select value={eleccion} onChange={e => { establecerEleccion(e.target.value); captura.current = crypto.randomUUID() }}><option value="">Elige una respuesta independiente</option>{cuestionario.programas.map(p => <option value={p.id} key={p.id}>{p.nombre} · {p.institucion}</option>)}<option value="ambas">Ambas</option><option value="ninguna">Ninguna</option><option value="incierto">No estoy seguro</option></select></label></>}
      </details>}
    </div>}
    {error && <p className="error-cuestionario" role="alert">{error}</p>}
    <div className="acciones-cuestionario"><button className="button" type="button" disabled={paso === 0 || cargando} onClick={() => establecerPaso(paso - 1)}>Anterior</button><button className="button primary" type="submit" disabled={!respuestas[pregunta.id] || cargando}>{cargando ? 'Analizando…' : ultima ? 'Analizar mis respuestas' : 'Siguiente'}</button></div>
  </form>
}

function CargarCuestionario({ identificadores, cerrar }: { identificadores: string[]; cerrar: () => void }) {
  const parametros = new URLSearchParams(); identificadores.forEach(id => parametros.append('idsProgramas', id))
  const { resultado, reintentar } = useRecurso<Cuestionario>(`/v1/cuestionario/comparativo?${parametros}`)
  if (resultado.estado === 'loading') return <p role="status">Preparando las preguntas para tus dos carreras…</p>
  if (resultado.estado === 'error') return <div role="alert"><p>No se pudo preparar el cuestionario.</p><button className="button" onClick={reintentar}>Reintentar</button><button className="button" onClick={cerrar}>Cerrar</button></div>
  return <FormularioVocacional cuestionario={resultado.datos} identificadores={identificadores} cerrar={cerrar} />
}

export function CuestionarioVocacional({ identificadores }: { identificadores: string[] }) {
  const [iniciado, establecerIniciado] = useState(false)
  const [abierto, establecerAbierto] = useState(false)
  return <section className="panel-vocacional" aria-labelledby="titulo-vocacional"><div className="introduccion-vocacional"><span className="etiqueta-seccion"><Icono nombre="sparkles" /> MI ORIENTACIÓN</span>
    <h2 id="titulo-vocacional">Descubre qué carrera se adapta mejor a ti</h2><p>Diez preguntas sobre tus intereses, preferencias y las carreras que elegiste. Sin crear una cuenta.</p></div>
    <button className="button primary" onClick={() => { establecerIniciado(true); establecerAbierto(!abierto) }}>{abierto ? 'Ocultar cuestionario' : 'Analizar con IA'} <Icono nombre="arrow" /></button>
    <div hidden={!abierto}>{iniciado && <CargarCuestionario identificadores={identificadores} cerrar={() => establecerAbierto(false)} />}</div>
  </section>
}
