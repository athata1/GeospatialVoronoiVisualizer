import React, { useState } from 'react'
import { useGraph } from '../../contexts/GraphContext'

import './VoronoiOptions.css'

export default function VoronoiOptions() {

    const [options] = useState(['Hospital', 'EMT', 'Cafe', 'Restaurant', 'Dunkin', 'Gym'])
    const { search, setSearch } = useGraph()
  return (
    <div className='voronoi-options'>
        <div className='voronoi-options-title'>
            <div className='voronoi-title'>
                Select Search Type
            </div>
        </div>
        {options.map((option) => {
            return <button className={`voronoi-option ${search === option ? 'selected' : ''}`} onClick={() => {setSearch(option)}}>
                {option}
            </button>
        })}
    </div>
  )
}
