import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import QuestoesFormatadas from './components/QuestoesFormatadas'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/questoes-formatadas" element={<QuestoesFormatadas />} />
      </Routes>
    </Router>
  )
}

export default App

