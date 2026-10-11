import React, { useState, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Globe2 } from 'lucide-react';

// Fix broken Leaflet default icons in Vite bundling
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
});

// Default active Mapbox token (loaded via VITE_MAP_API_KEY)
const DEFAULT_MAPBOX_KEY = '';

export const MapView = ({ routes = [], height = '450px' }) => {
  // Default center: Tamil Nadu center (Trichy coordinates)
  const defaultCenter = [10.7905, 78.7047];

  // Active Map API Key & Tile URL
  const apiKey = import.meta.env.VITE_MAP_API_KEY || DEFAULT_MAPBOX_KEY;
  const customTileUrl = import.meta.env.VITE_MAP_TILE_URL;

  // Mapbox & provider style definitions
  const MAP_STYLES = useMemo(() => {
    if (apiKey && apiKey.startsWith('pk.')) {
      const darkUrl = customTileUrl
        ? customTileUrl.replace('{apiKey}', apiKey).replace('{accessToken}', apiKey)
        : `https://api.mapbox.com/styles/v1/mapbox/dark-v11/tiles/256/{z}/{x}/{y}@2x?access_token=${apiKey}`;

      return {
        dark: {
          name: 'Dark HD',
          url: darkUrl,
          attribution: '&copy; <a href="https://www.mapbox.com/about/maps/">Mapbox</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        },
        navigation: {
          name: 'Navigation Night',
          url: `https://api.mapbox.com/styles/v1/mapbox/navigation-night-v1/tiles/256/{z}/{x}/{y}@2x?access_token=${apiKey}`,
          attribution: '&copy; <a href="https://www.mapbox.com/about/maps/">Mapbox</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        },
        satellite: {
          name: 'Satellite',
          url: `https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v12/tiles/256/{z}/{x}/{y}@2x?access_token=${apiKey}`,
          attribution: '&copy; <a href="https://www.mapbox.com/about/maps/">Mapbox</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        },
      };
    }

    return {
      carto: {
        name: 'Dark Carto',
        url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      },
      osm: {
        name: 'OpenStreetMap',
        url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      },
    };
  }, [apiKey, customTileUrl]);

  const [activeStyleKey, setActiveStyleKey] = useState(
    apiKey && apiKey.startsWith('pk.') ? 'dark' : 'carto'
  );

  const currentStyle = MAP_STYLES[activeStyleKey] || Object.values(MAP_STYLES)[0];
  const isMapbox = currentStyle?.url?.includes('mapbox.com');

  return (
    <div style={{ height, width: '100%' }} className="relative overflow-hidden rounded-xl border border-slate-800 shadow-2xl group">
      {/* Floating Mapbox Provider Badge & Style Switcher */}
      <div className="absolute top-3 left-3 z-[1000] flex items-center gap-2 bg-slate-900/85 backdrop-blur-md px-3 py-1.5 rounded-lg border border-slate-700/60 shadow-lg pointer-events-auto">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
        </span>
        <span className="text-[11px] font-semibold text-slate-200 tracking-wide flex items-center gap-1.5">
          <Globe2 className="w-3.5 h-3.5 text-blue-400" />
          {isMapbox ? 'Mapbox HD Vector' : 'OpenStreetMap'}
        </span>
      </div>

      {/* Style Toggle Pills */}
      {Object.keys(MAP_STYLES).length > 1 && (
        <div className="absolute top-3 right-3 z-[1000] flex items-center gap-1 bg-slate-900/85 backdrop-blur-md p-1 rounded-lg border border-slate-700/60 shadow-lg pointer-events-auto">
          {Object.entries(MAP_STYLES).map(([key, style]) => (
            <button
              key={key}
              type="button"
              onClick={() => setActiveStyleKey(key)}
              className={`px-2.5 py-1 text-[11px] font-medium rounded-md transition-all ${
                activeStyleKey === key
                  ? 'bg-blue-600 text-white shadow-sm shadow-blue-500/30'
                  : 'text-slate-300 hover:text-white hover:bg-slate-800/80'
              }`}
            >
              {style.name}
            </button>
          ))}
        </div>
      )}

      <MapContainer
        center={defaultCenter}
        zoom={7}
        scrollWheelZoom={true}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          key={activeStyleKey}
          attribution={currentStyle.attribution}
          url={currentStyle.url}
          subdomains="abcd"
          maxZoom={19}
          tileSize={256}
          eventHandlers={{
            tileerror: (e) => {
              console.warn('Tile load failed, attempting fallback URL', e);
              if (activeStyleKey !== 'osm') {
                setActiveStyleKey('osm');
              }
            },
          }}
        />

        {routes.map((route, idx) => {
          const origin = route.origin_coords;
          const dest = route.dest_coords;
          const pickup = route.pickup_coords;
          const dropoff = route.dropoff_coords;

          const polyline = [origin, pickup, dropoff, dest].filter(Boolean);

          return (
            <React.Fragment key={route.match_id || idx}>
              {origin && (
                <Marker position={origin}>
                  <Popup>
                    <div className="text-slate-900 font-medium">
                      <strong>Origin:</strong> {route.origin}
                    </div>
                  </Popup>
                </Marker>
              )}
              {dest && (
                <Marker position={dest}>
                  <Popup>
                    <div className="text-slate-900 font-medium">
                      <strong>Destination:</strong> {route.destination}
                    </div>
                  </Popup>
                </Marker>
              )}
              {pickup && (
                <Marker position={pickup}>
                  <Popup>
                    <div className="text-slate-900 font-medium">
                      <strong>Pickup:</strong> {route.pickup}
                    </div>
                  </Popup>
                </Marker>
              )}
              {dropoff && (
                <Marker position={dropoff}>
                  <Popup>
                    <div className="text-slate-900 font-medium">
                      <strong>Dropoff:</strong> {route.dropoff}
                    </div>
                  </Popup>
                </Marker>
              )}
              {polyline.length > 1 && (
                <Polyline
                  positions={polyline}
                  color={route.score > 80 ? '#10b981' : '#3b82f6'}
                  weight={4}
                  dashArray={route.detour_km > 30 ? '6, 8' : null}
                />
              )}
            </React.Fragment>
          );
        })}
      </MapContainer>
    </div>
  );
};
