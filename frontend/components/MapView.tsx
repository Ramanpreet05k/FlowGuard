"use client";

import { MapContainer, TileLayer, Marker, Polyline, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { useEffect } from 'react';

interface Hotzone {
  id: number;
  latitude: number;
  longitude: number;
  total_cis: number;
  vehicle_count: number;
}

interface MapViewProps {
  hotzones: Hotzone[];
  route: Hotzone[];
  selectedZone: Hotzone | null; // NEW: The map now knows which zone was clicked
}

// NEW: A tiny helper component that controls the Leaflet camera
function MapController({ selectedZone }: { selectedZone: Hotzone | null }) {
  const map = useMap();
  
  useEffect(() => {
    if (selectedZone) {
      // Fly to the coordinates with a slick 1.5-second animation at zoom level 16
      map.flyTo([selectedZone.latitude, selectedZone.longitude], 16, {
        duration: 1.5,
      });
    }
  }, [selectedZone, map]);

  return null; // This component is invisible, it just moves the camera
}

export default function MapView({ hotzones, route, selectedZone }: MapViewProps) {
  useEffect(() => {
    delete (L.Icon.Default.prototype as any)._getIconUrl;
    L.Icon.Default.mergeOptions({
      iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
      iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
      shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
    });
  }, []);

  const routeCoordinates: [number, number][] = route.map(point => [point.latitude, point.longitude]);

  const createHotzoneIcon = (cis: number) => {
    const size = Math.max(15, Math.min(cis / 1000, 50)); 
    return L.divIcon({
      className: 'custom-icon', 
      html: `<div style="
        width: ${size}px; 
        height: ${size}px; 
        background-color: rgba(239, 68, 68, 0.8); 
        border-radius: 50%; 
        box-shadow: 0 0 15px rgba(239, 68, 68, 0.9);
        border: 2px solid white;
        transition: all 0.3s ease;
      "></div>`,
      iconSize: [size, size],
      iconAnchor: [size / 2, size / 2], 
    });
  };

  return (
    <div className="w-full h-full relative z-0">
      <MapContainer 
        center={[12.9716, 77.5946]} 
        zoom={12} 
        style={{ height: '100%', width: '100%', background: '#0f172a' }} 
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />

        {/* Drop the camera controller into the map */}
        <MapController selectedZone={selectedZone} />

        {hotzones.map((zone) => (
          <Marker 
            key={`marker-${zone.id}`}
            position={[zone.latitude, zone.longitude]}
            icon={createHotzoneIcon(zone.total_cis)}
          />
        ))}

        {routeCoordinates.length > 0 && (
          <Polyline 
            positions={routeCoordinates} 
            color="#3b82f6" 
            weight={4}
            dashArray="10, 10" 
            opacity={0.8}
          />
        )}
      </MapContainer>

      <div className="absolute bottom-6 right-6 bg-slate-900/90 border border-slate-700 p-4 rounded-lg shadow-xl text-xs text-slate-300 z-[1000]">
        <div className="flex items-center gap-2 mb-2">
          <div className="w-3 h-3 bg-red-500 rounded-full shadow-[0_0_8px_rgba(239,68,68,0.8)]"></div>
          <span>Critical Hotzone (Size = CIS)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-1 border-b-2 border-blue-500 border-dashed"></div>
          <span>Optimized Dispatch Route</span>
        </div>
      </div>
    </div>
  );
}