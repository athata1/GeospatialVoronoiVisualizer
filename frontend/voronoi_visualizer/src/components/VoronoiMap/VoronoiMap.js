import React, { useEffect, useRef, useState } from 'react'
import {MapContainer, TileLayer} from 'react-leaflet'
import { useGraph } from '../../contexts/GraphContext'
import axios from 'axios'
import L from 'leaflet'

import 'leaflet/dist/leaflet.css'
import './VoronoiMap.css'

export default function VoronoiMap() {

    const [position, setPosition] = useState({lat:51.505, lng:-0.09})
    const mapRef = useRef()

    const {search, data} = useGraph()
    

    useEffect(() => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(success, error);
        } else {
            console.log("Geolocation not supported");
        }

    }, [])

    function success(position) {
        const latitude = position.coords.latitude;
        const longitude = position.coords.longitude;
        console.log(`Latitude: ${latitude}, Longitude: ${longitude}`);
        setPosition({lat: latitude, lng: longitude})
        mapRef.current.setView(new L.LatLng(parseFloat(latitude), parseFloat(longitude)), 13);
        axios.get(`http://127.0.0.1:5000/voronoi?long=${latitude}&lat=${longitude}&search=dunkin`)
     }

    function error() {
        console.log("Unable to retrieve your location");
    }

    return (
        <div className='voronoi-map'>
            <MapContainer center={position} zoom={13} ref={mapRef}>
                <TileLayer
                url='https://api.maptiler.com/maps/basic-v2/256/{z}/{x}/{y}.png?key=3yNtRIKapPB7eHfBDiUx'
                attribution='<a href="https://www.maptiler.com/copyright/" target="_blank">&copy; MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">&copy; OpenStreetMap contributors</a>'
                />
            </MapContainer>
        </div>
    )
}
