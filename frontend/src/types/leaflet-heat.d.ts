import * as L from 'leaflet';

declare module 'leaflet' {
  interface HeatLayerOptions {
    minOpacity?: number;
    maxZoom?: number;
    radius?: number;
    blur?: number;
    gradient?: Record<string, string>;
    max?: number;
  }

  function heatLayer(
    latlngs: L.LatLngExpression[],
    options?: HeatLayerOptions,
  ): L.Layer;
}

declare module 'leaflet.heat';
