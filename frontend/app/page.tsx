"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, Map as MapIcon, ShieldAlert, Activity, Crosshair } from "lucide-react";
import dynamic from 'next/dynamic';

const MapView = dynamic(() => import('../components/MapView'), { ssr: false });

interface Hotzone {
  id: number;
  latitude: number;
  longitude: number;
  total_cis: number;
  vehicle_count: number;
}

export default function FlowGuardDashboard() {
  const [hotzones, setHotzones] = useState<Hotzone[]>([]);
  const [route, setRoute] = useState<Hotzone[]>([]); 
  const [loading, setLoading] = useState(true);
  
  // NEW: State to track which cluster the user clicked
  const [selectedZone, setSelectedZone] = useState<Hotzone | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [hotzonesRes, routeRes] = await Promise.all([
          fetch("http://127.0.0.1:8000/api/hotzones"),
          fetch("http://127.0.0.1:8000/api/routes")
        ]);

        const hotzonesData = await hotzonesRes.json();
        const routeData = await routeRes.json();

        setHotzones(hotzonesData.hotzones);
        setRoute(routeData.optimized_route);
        setLoading(false);
      } catch (error) {
        console.error("Failed to fetch data:", error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="flex h-screen w-full bg-slate-950 text-slate-100 font-sans overflow-hidden">
      
      {/* LEFT SIDEBAR */}
      <div className="w-1/3 h-full bg-slate-900 border-r border-slate-800 flex flex-col shadow-2xl z-10 relative">
        <div className="p-6 border-b border-slate-800">
          <div className="flex items-center gap-3 mb-2">
            <ShieldAlert className="w-8 h-8 text-blue-500" />
            <h1 className="text-2xl font-bold tracking-tight text-white">FlowGuard</h1>
          </div>
          <p className="text-sm text-slate-400">Predictive Congestion & ROI Engine</p>
        </div>

        <div className="p-6 grid grid-cols-2 gap-4 border-b border-slate-800 bg-slate-800/30">
          <div className="flex flex-col">
            <span className="text-xs text-slate-400 uppercase font-semibold tracking-wider">Active Hotzones</span>
            <span className="text-3xl font-bold text-white mt-1">
              {loading ? "..." : hotzones.length}
            </span>
          </div>
          <div className="flex flex-col">
            <span className="text-xs text-slate-400 uppercase font-semibold tracking-wider">Max Network CIS</span>
            <span className="text-3xl font-bold text-red-400 mt-1">
              {loading || hotzones.length === 0 ? "..." : Math.round(hotzones[0].total_cis)}
            </span>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          <h2 className="text-sm text-slate-400 uppercase font-semibold tracking-wider mb-4 flex items-center gap-2">
            <Activity className="w-4 h-4" />
            Critical Spillover Nodes
          </h2>

          {loading ? (
            <div className="animate-pulse space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-20 bg-slate-800 rounded-lg w-full"></div>
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              {hotzones.slice(0, 10).map((zone, index) => (
                <div 
                  key={zone.id} 
                  // NEW: Add the onClick handler to trigger the map movement
                  onClick={() => setSelectedZone(zone)}
                  // NEW: Add a visual highlight if the card is currently selected
                  className={`bg-slate-800/50 border p-4 rounded-lg hover:bg-slate-800 transition-colors cursor-pointer group ${
                    selectedZone?.id === zone.id ? 'border-blue-500 shadow-[0_0_15px_rgba(59,130,246,0.2)]' : 'border-slate-700'
                  }`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-bold text-white flex items-center gap-2">
                      <span className="flex items-center justify-center w-5 h-5 rounded-full bg-slate-700 text-xs text-slate-300">
                        {index + 1}
                      </span>
                      Cluster {zone.id}
                    </span>
                    <span className="bg-red-500/20 text-red-400 text-xs font-bold px-2 py-1 rounded border border-red-500/30">
                      CIS: {zone.total_cis}
                    </span>
                  </div>
                  <div className="flex justify-between items-center text-xs text-slate-400">
                    <span>{zone.vehicle_count} Vehicles</span>
                    
                    {/* NEW: A cool crosshair icon appears when you hover over the card */}
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity text-blue-400">
                      <Crosshair className="w-3 h-3" />
                      <span>Locate</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="flex-1 h-full relative bg-slate-950 z-0">
        {!loading && hotzones.length > 0 ? (
           <MapView hotzones={hotzones} route={route} selectedZone={selectedZone} />
        ) : (
           <div className="flex h-full items-center justify-center">
              <div className="text-center">
                 <MapIcon className="w-16 h-16 mx-auto mb-4 opacity-50 animate-pulse text-slate-500" />
                 <p className="text-slate-500 animate-pulse font-medium">Initializing Geospatial Engine...</p>
              </div>
           </div>
        )}
      </div>

    </div>
  );
}