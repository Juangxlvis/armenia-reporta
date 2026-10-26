import * as L from 'leaflet';

declare global {
  interface Window {
    L: typeof L;
  }
}

window.L = L;
