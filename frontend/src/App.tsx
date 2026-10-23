import { AppShell } from './components/layout/AppShell.tsx'

const navItems = [{ id: 'conversation', label: 'Conversación' }]

function App() {
  return (
    <AppShell navItems={navItems} activeNavId="conversation">
      <p>Contenido de prueba</p>
    </AppShell>
  )
}

export default App
