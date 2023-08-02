import React from 'react'
import VoronoiMap from '../../components/VoronoiMap/VoronoiMap'
import { GraphProvider } from '../../contexts/GraphContext'

import './VoronoiGraph.css'

export default function VoronoiGraph() {
  return (
    <GraphProvider>
      <div className='voronoi-graph'>
        <VoronoiMap />
      </div>
    </GraphProvider>
  )
}
