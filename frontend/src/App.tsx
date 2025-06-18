import React, { useEffect, useState } from 'react';

// Define the car type
interface CarListing {
  name: string;
  url: string;
  mileage: number;
  price: number;
  roadValue: number;
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
        console.log(data);
        setCars(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="notion-loading">Loading...</div>;
  if (error) return <div className="notion-error">Error: {error}</div>;

  return (
    <div className="notion-root">
      <header className="notion-header">
        <h1>🚗 AutoZoeker</h1>
        <p className="notion-subtitle">Second-hand Cars in the Netherlands</p>
      </header>
      <div className="notion-table-container">
        <table className="notion-table">
          <thead>
            <tr>
              <th>Name</th>
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
            </tr>
          </thead>
          <tbody>
            {cars.map((car, idx) => (
              <tr key={car.url || idx} className="notion-table-row">
                <td>
                  {car.url && car.name ? (
                    <a href={car.url} target="_blank" rel="noopener noreferrer">{car.name}</a>
                  ) : car.name ? car.name : 'N/A'}
                </td>
                <td>{car.mileage ? car.mileage.toLocaleString() : 'N/A'}</td>
                <td>{car.price ? `€${car.price.toLocaleString()}` : 'N/A'}</td>
                <td>{car.roadValue ? `€${car.roadValue.toLocaleString()}` : 'N/A'}</td>
                <td>{car.dealer ? car.dealer : 'N/A'}</td>
                <td>{car.phone ? car.phone : 'N/A'}</td>
                <td>{car.rdw ? 'Yes' : 'No'}</td>
                <td>{car.bovag ? 'Yes' : 'No'}</td>
                <td>{car.plate ? car.plate : 'N/A'}</td>
                <td>{car.year ? car.year : 'N/A'}</td>
                <td>{car.apkExpiry ? car.apkExpiry : 'N/A'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <style>{`
        body {
          background: #f6f7f9;
        }
        .notion-root {
          max-width: 1200px;
          margin: 40px auto;
          padding: 32px;
          background: #fff;
          border-radius: 16px;
          box-shadow: 0 4px 24px rgba(0,0,0,0.07);
          font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
        }
        .notion-header {
          margin-bottom: 32px;
        }
        .notion-header h1 {
          font-size: 2.5rem;
          font-weight: 700;
          margin: 0 0 8px 0;
        }
        .notion-subtitle {
          color: #888;
          font-size: 1.1rem;
          margin: 0;
        }
        .notion-table-container {
          overflow-x: auto;
        }
        .notion-table {
          width: 100%;
          border-collapse: separate;
          border-spacing: 0;
          background: #fafbfc;
          border-radius: 12px;
          box-shadow: 0 1px 4px rgba(0,0,0,0.03);
        }
        .notion-table th, .notion-table td {
          padding: 12px 16px;
          text-align: left;
        }
        .notion-table th {
          background: #f3f4f6;
          font-weight: 600;
          color: #444;
        }
        .notion-table tr {
          border-bottom: 1px solid #ececec;
        }
        .notion-table tr:last-child {
          border-bottom: none;
        }
        .notion-table td {
          background: #fff;
          border-right: 1px solid #f3f4f6;
        }
        .notion-table td:last-child {
          border-right: none;
        }
        .notion-table a {
          color: #2d7ff9;
          text-decoration: none;
          font-weight: 500;
        }
        .notion-table a:hover {
          text-decoration: underline;
        }
        .notion-loading, .notion-error {
          text-align: center;
          margin-top: 80px;
          font-size: 1.3rem;
          color: #888;
        }
        .notion-table-row:not(:last-child) td {
          border-bottom: 1px solid #ececec;
        }
        @media (max-width: 800px) {
          .notion-root {
            padding: 8px;
          }
          .notion-header h1 {
            font-size: 2rem;
          }
          .notion-table th, .notion-table td {
            padding: 8px 6px;
            font-size: 0.95rem;
          }
        }
      `}</style>
    </div>
  );
};

export default App;
