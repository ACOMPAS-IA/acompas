// Evento de sesión caducada (ACO-019, P3). No guarda estado: solo notifica
// a la capa de autenticación. La deduplicación vive en useAuthSession.
export const SESSION_EXPIRED_EVENT = 'acompas:session-expired'

export function notifySessionExpired(): void {
  window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT))
}
