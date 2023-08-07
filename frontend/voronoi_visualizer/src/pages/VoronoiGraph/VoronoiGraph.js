import React from 'react'
import VoronoiMap from '../../components/VoronoiMap/VoronoiMap'
import VoronoiOptions from '../../components/VoronoiOptions/VoronoiOptions'
import { GraphProvider } from '../../contexts/GraphContext'

import './VoronoiGraph.css'

export default function VoronoiGraph() {
  return (
    <GraphProvider>
      <div className='voronoi-graph'>
        <VoronoiMap />
        <VoronoiOptions />
      </div>
    </GraphProvider>
  )
}
