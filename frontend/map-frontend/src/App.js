import React, { useState, useEffect, useMemo } from "react";
import {
  GoogleMap,
  LoadScript,
  Marker,
  InfoWindow,
} from "@react-google-maps/api";
import axios from "axios";

const containerStyle = {
  width: '100%',
  height: '100vh'
};

function getColorByScore(score) {
  if (score <= 0) return '#00FF00';
  if (score <= 4) return '#7CFC00';
  if (score <= 9) return '#228B22';
  if (score <= 13) return '#006400';
  if (score <= 18) return '#FFFF00';
  if (score <= 22) return '#FFD700';
  if (score <= 27) return '#FFFACD';
  if (score <= 40) return '#FFA07A';
  if (score <= 60) return '#FF4500';
  return '#8B0000';
}

function App() {
  const [markers, setMarkers] = useState([]);
  const [activeMarker, setActiveMarker] = useState(null);

  // Default center coordinates (NYC City Hall)
  const center = useMemo(() => ({ lat: 40.7128, lng: -74.0060 }), []);

  useEffect(() => {
    async function fetchBusinessesAndCoordinates() {
      try {
        const response = await fetch('http://localhost:50000/businesses');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const businesses = await response.json();
        const results = await Promise.all(
            businesses.map(async (biz) => {
              if (biz.latitude !== 0 && biz.longitude !== 0) {
                return {
                  lat: biz.latitude,
                  lng: biz.longitude,
                  ...biz // merge in your business metadata
                };
              } else {
                // Need to fetch coordinates from the Google Maps geocoding API
                const geocodeUrl = `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(biz.address)}&key=${process.env.REACT_APP_GOOGLE_MAPS_API_KEY}`;
                const response = await axios.get(geocodeUrl);
                const data = response.data;
                if (data.status === 'OK') {
                  const location = data.results[0].geometry.location;
                  return {
                    lat: location.lat,
                    lng: location.lng,
                    ...biz // merge in your business metadata
                  };
                } else {
                  console.error(`Failed to geocode ${biz.address}: ${data.status}`);
                  return null;
                }
              }
            })
        );
        setMarkers(results.filter(Boolean));
      } catch (error) {
        console.error("Error fetching geocodes:", error);
      }
    }

    fetchBusinessesAndCoordinates().then(r => {
        console.log("Fetched businesses and coordinates:", r);
    })
  }, []);

  const handleActiveMarker = (markerIndex) => {
    if (markerIndex === activeMarker) {
      return;
    }
    setActiveMarker(markerIndex);
  };

  return (
      <LoadScript googleMapsApiKey={process.env.REACT_APP_GOOGLE_MAPS_API_KEY}>
        <GoogleMap
            mapContainerStyle={containerStyle}
            zoom={11}
            onClick={() => setActiveMarker(null)} // close info window when clicking on map
            center={center}
            options={{
              mapTypeControl: true,
              streetViewControl: true,
              zoomControl: true,
              fullscreenControl: true,
            }}
        >
          {markers.map((marker, idx) => (
              <Marker
                  key={idx}
                  position={{lat: marker.lat, lng: marker.lng}}
                  label={`${idx + 1}`}
                  title={marker.name}
                  onClick={() => handleActiveMarker(idx)}
                  icon={{ 
                    path: window.google?.maps?.SymbolPath?.CIRCLE,
                    scale: 12,
                    fillColor: getColorByScore(marker.score),
                    fillOpacity: 1,
                    strokeWeight: 1,
                    strokeColor: 'white',
                  }}
              >
                {activeMarker === idx ? (
                    <InfoWindow onCloseClick={() => setActiveMarker(null)}>
                      <div>
                        <h3>{marker.name}</h3>
                        <p><strong>Address:</strong> {marker.unit ? `${marker.unit}, ` : ""}{marker.address}</p>
                        <p><strong>Violation:</strong> {marker.violationSummary}</p>
                        <p><strong>Violation Count:</strong>{marker.violationCount}</p>
                        <p><strong>Grade History:</strong>{marker.grade}</p>
                        <p><strong>Average Score Over Time:</strong>{marker.score}</p>
                        <p><strong>Cuisine:</strong>{marker.cuisineDescription}</p>
                        <p><strong>Last Inspection Date:</strong> {marker.inspectionDate}</p>
                        <p><strong>Latitude:</strong> {marker.lat}</p>
                        <p><strong>Longitude:</strong> {marker.lng}</p>
                      </div>
                    </InfoWindow>
                ) : null}
              </Marker>
          ))}
        </GoogleMap>
      </LoadScript>
  );
}

export default App;
