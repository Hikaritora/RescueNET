/**
 * MapPicker - Reusable Leaflet map picker for location input
 *
 * Usage:
 *   new MapPicker('map', 'id_lat', 'id_lng', {
 *       defaultLat: 51.1079,
 *       defaultLng: 17.0385,
 *       zoom: 13,
 *       draggable: true,
 *       interactive: true
 *   });
 */

class MapPicker {
    constructor(mapElementId, latInputId, lngInputId, options = {}) {
        this.mapEl = document.getElementById(mapElementId);
        this.latInput = document.getElementById(latInputId);
        this.lngInput = document.getElementById(lngInputId);

        // Default configuration
        this.options = {
            defaultLat: 51.1079,
            defaultLng: 17.0385,
            zoom: 13,
            tileLayer: 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
            attribution: '© CARTO',
            draggable: true,
            interactive: true,
            ...options
        };

        this.map = null;
        this.marker = null;

        // Initialize if all required elements exist
        if (this.mapEl && this.latInput && this.lngInput) {
            this.init();
        }
    }

    /**
     * Parse coordinate from input (handles both . and , as decimal separator)
     */
    parseCoordinate(value) {
        if (!value) return NaN;
        return parseFloat(String(value).replace(',', '.'));
    }

    /**
     * Update input fields with coordinates
     */
    setCoords(lat, lng) {
        if (this.latInput) this.latInput.value = lat.toFixed(6);
        if (this.lngInput) this.lngInput.value = lng.toFixed(6);
    }

    /**
     * Get current marker position
     */
    getCoords() {
        if (!this.marker) return null;
        const pos = this.marker.getLatLng();
        return { lat: pos.lat, lng: pos.lng };
    }

    /**
     * Initialize the map and marker
     */
    init() {

        // Parse initial coordinates from inputs
        const initialLat = this.parseCoordinate(this.latInput.value);
        const initialLng = this.parseCoordinate(this.lngInput.value);
        const hasInitialCoords = !isNaN(initialLat) && !isNaN(initialLng)
                              && initialLat !== 0 && initialLng !== 0;

        // Determine starting position
        const startLat = hasInitialCoords ? initialLat : this.options.defaultLat;
        const startLng = hasInitialCoords ? initialLng : this.options.defaultLng;

        // Create map
        this.map = L.map(this.mapEl).setView([startLat, startLng], this.options.zoom);

        // Add tile layer
        L.tileLayer(this.options.tileLayer, {
            attribution: this.options.attribution
        }).addTo(this.map);

        // Create marker
        this.marker = L.marker([startLat, startLng], {
            draggable: this.options.draggable
        }).addTo(this.map);

        // Update coordinates on marker drag
        if (this.options.draggable) {
            this.marker.on('dragend', () => {
                const pos = this.marker.getLatLng();
                this.setCoords(pos.lat, pos.lng);
            });
        }

        // Handle map click to place marker
        if (this.options.interactive) {
            this.map.on('click', (e) => {
                this.marker.setLatLng(e.latlng);
                this.setCoords(e.latlng.lat, e.latlng.lng);
            });
        }

        // Listen for manual input changes to update marker position
        this.latInput.addEventListener('change', () => this.syncInputToMarker());
        this.lngInput.addEventListener('change', () => this.syncInputToMarker());

        // Set initial coordinates if not already present
        if (!hasInitialCoords) {
            this.setCoords(startLat, startLng);
        }

        // Trigger map resize after a brief delay to ensure proper rendering
        setTimeout(() => this.map.invalidateSize(), 150);
    }

    /**
     * Sync manually-edited input fields back to the marker on the map
     */
    syncInputToMarker() {
        const lat = this.parseCoordinate(this.latInput.value);
        const lng = this.parseCoordinate(this.lngInput.value);

        if (!isNaN(lat) && !isNaN(lng) && lat !== 0 && lng !== 0) {
            this.marker.setLatLng([lat, lng]);
            this.map.setView([lat, lng], this.options.zoom);
        }
    }

    /**
     * Update marker position programmatically
     */
    setMarkerPosition(lat, lng) {
        if (!this.marker || !this.map) return;
        this.marker.setLatLng([lat, lng]);
        this.map.setView([lat, lng], this.options.zoom);
        this.setCoords(lat, lng);
    }

    /**
     * Remove marker from map
     */
    removeMarker() {
        if (this.marker) {
            this.map.removeLayer(this.marker);
            this.marker = null;
        }
    }

    /**
     * Destroy the map
     */
    destroy() {
        if (this.map) {
            this.map.remove();
            this.map = null;
        }
        this.marker = null;
    }
}

/**
 * FormMapPicker - Enhanced version for form-based resource/incident addition
 * Handles both initial setup and click-to-place functionality
 */
class FormMapPicker extends MapPicker {
    constructor(mapElementId, latInputId, lngInputId, options = {}) {
        super(mapElementId, latInputId, lngInputId, options);
    }

    /**
     * Initialize with click-to-place if no marker initially set
     */
    init() {
        super.init();

        // If no initial coordinates, hide marker until user clicks
        if (!this.hasInitialCoords) {
            this.map.removeLayer(this.marker);
            this.marker = null;
        }
    }

    get hasInitialCoords() {
        const lat = this.parseCoordinate(this.latInput.value);
        const lng = this.parseCoordinate(this.lngInput.value);
        return !isNaN(lat) && !isNaN(lng) && lat !== 0 && lng !== 0;
    }
}

