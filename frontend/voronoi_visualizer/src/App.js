import './App.css';

import { BrowserRouter, Routes, Route } from "react-router-dom";

import VoronoiGraph from './pages/VoronoiGraph/VoronoiGraph';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path='/' element={<VoronoiGraph/>}/>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
