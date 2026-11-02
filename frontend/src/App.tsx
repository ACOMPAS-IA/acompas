import { AppShell } from './components/layout/AppShell.tsx'
import { Disclaimer } from './components/disclaimer/Disclaimer.tsx'

const navItems = [{ id: 'conversation', label: 'Conversación' }]

function App() {
  return (
    <AppShell
      navItems={navItems}
      activeNavId="conversation"
      disclaimer={<Disclaimer />}
    >
      <p>Contenido de prueba</p>
    </AppShell>
  )
}

export default App
