import './Disclaimer.css'

// Texto fijo del aviso (ficha ACO-031, sección 8). ACO-052 y ACO-033 lo
// importan para comprobar que el aviso está visible (T-21).
export const DISCLAIMER_TEXT =
  'ACOMPAS te ayuda a entender tu documentación, pero no diagnostica ni sustituye al médico. Consulta siempre con tu equipo oncológico.'

// Va en el slot disclaimer de AppShell (ACO-017), que pone el pie «Aviso legal».
export function Disclaimer() {
  return <p className="disclaimer">{DISCLAIMER_TEXT}</p>
}
