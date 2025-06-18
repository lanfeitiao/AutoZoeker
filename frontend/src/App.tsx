import React, { useEffect, useState } from 'react';

// Define the car type
interface CarListing {
  name: string;
  status: string;
  url: string;
  mileage: number;
  price: number;
  roadValue: number;
  notes: string;
  phone: string;
  dealer: string;
  rdw: boolean;
  bovag: boolean;
  plate: string;
  year: number;
  apkExpiry: string;
}

const App: React.FC = () => {
  const [cars, setCars] = useState<CarListing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/cars')
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch car data');
        return res.json();
      })
      .then((data) => {
        setCars(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div style={{ padding: 24 }}>
      <h1>AutoZoeker - Second-hand Cars in NL</h1>
      <table border={1} cellPadding={6} cellSpacing={0}>
        <thead>
          <tr>
            <th>Name</th>
            <th>Status</th>
            <th>Mileage</th>
            <th>Price</th>
            <th>Road Value</th>
            <th>Dealer</th>
            <th>Phone</th>
            <th>RDW</th>
            <th>Bovag</th>
            <th>Plate</th>
            <th>Year</th>
            <th>APK Expiry</th>
            <th>Notes</th>
          </tr>
        </thead>
        <tbody>
          {cars.map((car) => (
            <tr key={car.plate}>
              <td><a href={car.url} target="_blank" rel="noopener noreferrer">{car.name}</a></td>
              <td>{car.status}</td>
              <td>{car.mileage}</td>
              <td>{car.price}</td>
              <td>{car.roadValue}</td>
              <td>{car.dealer}</td>
              <td>{car.phone}</td>
              <td>{car.rdw ? 'Yes' : 'No'}</td>
              <td>{car.bovag ? 'Yes' : 'No'}</td>
              <td>{car.plate}</td>
              <td>{car.year}</td>
              <td>{car.apkExpiry}</td>
              <td>{car.notes}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default App;
