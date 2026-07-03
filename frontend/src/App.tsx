import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Layout from './components/Layout'
import Home from './pages/Home'
import Exploration from './pages/Exploration'
import Athletes from './pages/Athletes'
import Predictions from './pages/Predictions'
import Annotations from './pages/Annotations'
import Generations from './pages/Generations'
import Multisource from './pages/Multisource'

const qc = new QueryClient({
  defaultOptions: { queries: { staleTime: 5 * 60 * 1000, retry: 1 } },
})

export default function App() {
  return (
    <QueryClientProvider client={qc}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/exploration" element={<Exploration />} />
            <Route path="/athletes" element={<Athletes />} />
            <Route path="/predictions" element={<Predictions />} />
            <Route path="/annotations" element={<Annotations />} />
            <Route path="/generations" element={<Generations />} />
            <Route path="/multisource" element={<Multisource />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
