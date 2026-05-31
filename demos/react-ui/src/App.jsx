import ThemeToggle from './components/ThemeToggle'
import RoutingTable from './components/RoutingTable'

export default function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Polestar Playbox — Model Router</h1>
        <ThemeToggle />
      </header>

      <main className="app-main">
        <RoutingTable />
      </main>

      <footer className="app-footer">
        <p>Edit this app with the Kilo Code react-frontend role (gpt-5.2, fallback gpt-5.4-mini).</p>
      </footer>
    </div>
  )
}
