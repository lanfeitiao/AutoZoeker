import React, { useEffect, useState } from 'react';

// Define the car type based on the new JSON fields
interface CarListing {
  name: string;
  price: string;      // for display
  priceNum: number;   // for sorting
  year: number;
  mileage: string;    // for display
  mileageNum: number; // for sorting
  place: string;
  url: string;
  plate: string;
  apkExpiry?: string;
  finnikUrl?: string;
}

const App: React.FC = () => {
  const [cars, setCars] = useState<CarListing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortField, setSortField] = useState<'mileageNum' | 'priceNum'>('mileageNum');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

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

  // Helper to get price as number
  const getPriceNumber = (car: CarListing) => {
    if (!car.price) return 0;
    // Remove non-digit characters (except comma and dot)
    const cleaned = car.price.replace(/[^\d.,]/g, '').replace(',', '.');
    return parseFloat(cleaned) || 0;
  };

  // Sort cars by selected field and order
  const sortedCars = [...cars].sort((a, b) => {
    let aValue = a[sortField] || 0;
    let bValue = b[sortField] || 0;
    if (sortOrder === 'asc') {
      return aValue - bValue;
    } else {
      return bValue - aValue;
    }
  });

  if (loading) return <div className="notion-loading">Loading...</div>;
  if (error) return <div className="notion-error">Error: {error}</div>;

  return (
    <div className="notion-root">
      <header className="notion-header">
        <h1>🚗 AutoZoeker</h1>
        <p className="notion-subtitle">Second-hand Cars in the Netherlands</p>
      </header>
      {/* Filter/Sort Bar */}
      <div style={{ marginBottom: 24, display: 'flex', gap: 16, alignItems: 'center' }}>
        <label>
          Sort by:
          <select
            value={sortField}
            onChange={e => setSortField(e.target.value as 'mileageNum' | 'priceNum')}
            style={{ marginLeft: 8 }}
          >
            <option value="mileageNum">Mileage</option>
            <option value="priceNum">Price</option>
          </select>
        </label>
        <label>
          Order:
          <select
            value={sortOrder}
            onChange={e => setSortOrder(e.target.value as 'asc' | 'desc')}
            style={{ marginLeft: 8 }}
          >
            <option value="asc">Ascending</option>
            <option value="desc">Descending</option>
          </select>
        </label>
      </div>
      <div className="notion-table-container">
        <table className="notion-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Mileage</th>
              <th>Price</th>
              <th>Year</th>
              <th>Place</th>
              <th>Plate</th>
              <th>APK Expiry</th>
              <th>Finnik</th>
            </tr>
          </thead>
          <tbody>
            {sortedCars.map((car, idx) => (
              <tr key={car.url || idx} className="notion-table-row">
                <td>
                  {car.url && car.name ? (
                    <a href={car.url} target="_blank" rel="noopener noreferrer">{car.name}</a>
                  ) : car.name ? car.name : 'N/A'}
                </td>
                <td className="right-align">{car.mileage ? car.mileage + ' km' : 'N/A'}</td>
                <td>{car.price ? `€${car.price}` : 'N/A'}</td>
                <td>{car.year ? car.year : 'N/A'}</td>
                <td>{car.place ? car.place : 'N/A'}</td>
                <td>{car.plate ? car.plate : 'N/A'}</td>
                <td>{car.apkExpiry ? car.apkExpiry : 'N/A'}</td>
                <td>
                  {car.finnikUrl ? (
                    <a href={car.finnikUrl} target="_blank" rel="noopener noreferrer">View</a>
                  ) : 'N/A'}
                </td>
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
          max-width: 900px;
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
          text-align: center !important;
        }
        .notion-table-row:not(:last-child) td {
          border-bottom: 1px solid #ececec;
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
        .right-align {
          text-align: right !important;
        }
      `}</style>
    </div>
  );
};

export default App;
