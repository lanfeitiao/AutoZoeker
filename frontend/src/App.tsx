import React, { useEffect, useState } from 'react';

interface CarListing {
  name: string;
  price: string;      
  priceNum: number;   
  year: number;
  mileage: string;    
  mileageNum: number; 
  place: string;
  url: string;
  plate: string;
  apkExpiry?: string;
  finnikUrl?: string;
  estimatedPrice?: number;
  llmScore?: number;
  llmSummary?: string;
}

function stripMarkdown(text: string) {
  // Remove **bold**, *italic*, and trailing dots/colons
  return text.replace(/[*_`]+/g, '').replace(/[.:]+$/, '').trim();
}

function parseLLMSummary(summary: string) {
  if (!summary) return [];
  // Split only at the start of the string or after a newline
  const parts = summary.split(/(?:^|\n)(?=\d+\.\s)/g).map(s => s.trim()).filter(Boolean);
  return parts.map(part => {
    // Match: 5. **Final Recommendation**: or 5. Final Recommendation:
    const match = part.match(/^(\d+)\.\s*([*`_]*[^:]+[*`_]*):?\s*(.*)$/);
    if (match) {
      return {
        number: match[1],
        heading: stripMarkdown(match[2]),
        content: match[3].trim(),
      };
    }
    return { heading: '', content: part };
  });
}

const App: React.FC = () => {
  const [cars, setCars] = useState<CarListing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortField, setSortField] = useState<'mileageNum' | 'priceNum' | 'estimatedPrice'  | 'llmScore'>('mileageNum');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [selectedCar, setSelectedCar] = useState<CarListing | null>(null);

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
    <div className="notion-root-container">
      <div className={`notion-root${selectedCar ? ' with-panel' : ''}`}>
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
              onChange={e => setSortField(e.target.value as 'mileageNum' | 'priceNum' | 'estimatedPrice'  | 'llmScore')}
              style={{ marginLeft: 8 }}
            >
              <option value="mileageNum">Mileage</option>
              <option value="priceNum">Price</option>
              <option value="estimatedPrice">Estimated Price</option>
              <option value="llmScore">LLM Score</option>

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
                <th>Estimated Price</th>
                <th>Year</th>
                <th>Plate</th>
                <th>APK Expiry</th>
                <th>Finnik</th>
                <th>Place</th>
                <th>LLM Score</th>
                <th>LLM Summary</th>
              </tr>
            </thead>
            <tbody>
              {sortedCars.map((car, idx) => (
                <tr key={car.url || idx} className="notion-table-row" style={{ cursor: 'pointer' }} onClick={() => setSelectedCar(car)}>
                  <td>
                    {car.url && car.name ? (
                      <a href={car.url} target="_blank" rel="noopener noreferrer" onClick={e => e.stopPropagation()}>{car.name}</a>
                    ) : car.name ? car.name : 'N/A'}
                  </td>
                  <td className="right-align">{car.mileage ? car.mileage + ' km' : 'N/A'}</td>
                  <td>{car.price ? `€${car.price}` : 'N/A'}</td>
                  <td>{typeof car.estimatedPrice === 'number' ? `€${car.estimatedPrice.toLocaleString('nl-NL', { maximumFractionDigits: 0 })}` : 'N/A'}</td>
                  <td>{car.year ? car.year : 'N/A'}</td>
                  <td>{car.plate ? car.plate : 'N/A'}</td>
                  <td>{car.apkExpiry ? car.apkExpiry : 'N/A'}</td>
                  <td>
                    {car.finnikUrl ? (
                      <a href={car.finnikUrl} target="_blank" rel="noopener noreferrer" onClick={e => e.stopPropagation()}>View</a>
                    ) : 'N/A'}
                  </td>
                  <td>{car.place ? car.place : 'N/A'}</td>
                  <td>{car.llmScore ? car.llmScore : 'N/A'}</td>
                  <td>
                    <button onClick={e => { e.stopPropagation(); setSelectedCar(car); }}>LLM Summary</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      {selectedCar && (
        <div className="side-panel gaspedaal-panel" onClick={e => e.stopPropagation()}>
          <div className="side-panel-header">
            <h2>{selectedCar.name}</h2>
            <button className="side-panel-close" onClick={() => setSelectedCar(null)}>×</button>
          </div>
          <div className="side-panel-content">
            <div><strong>Price:</strong> {selectedCar.price}</div>
            <div><strong>Mileage:</strong> {selectedCar.mileage}</div>
            <div><strong>LLM Score:</strong> {selectedCar.llmScore}</div>
            <div style={{ marginTop: 24 }}>
              <h3>LLM Summary</h3>
              {selectedCar.llmSummary ? (
                <div className="llm-summary">
                  {parseLLMSummary(selectedCar.llmSummary).map((section, idx) => (
                    <div key={idx} style={{ marginBottom: '1.5em' }}>
                      <h4 style={{ marginBottom: '0.3em' }}>
                        {section.number ? `${section.number}. ` : ''}{section.heading}
                      </h4>
                      <p style={{ marginLeft: '1em' }}>{section.content}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <div>No LLM summary available for this car.</div>
              )}
            </div>
          </div>
        </div>
      )}
      <style>{`
        .notion-root-container {
          display: flex;
          flex-direction: row;
          width: 100%;
        }
        .notion-root {
          max-width: 1200px;
          margin: 40px auto;
          padding: 32px;
          background: #fff;
          border-radius: 16px;
          box-shadow: 0 4px 24px rgba(0,0,0,0.07);
          font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
          width: 100%;
          transition: max-width 0.3s, width 0.3s;
          flex-basis: 100%;
        }
        .notion-root.with-panel {
          max-width: none;
          width: 75%;
          flex-basis: 75%;
          margin-right: 0;
        }
        .gaspedaal-panel {
          background: #f7fafd;
          border-top-left-radius: 18px;
          border-bottom-left-radius: 18px;
          box-shadow: -4px 0 32px rgba(0,0,0,0.10);
          padding: 0;
          min-width: 350px;
          max-width: 480px;
          width: 25%;
          display: flex;
          flex-direction: column;
          height: auto;
          max-height: 80vh;
          overflow-y: auto;
          z-index: 1000;
          margin: 40px 32px 40px 0;
        }
        .side-panel-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 24px 28px 12px 28px;
          border-bottom: 1px solid #e3e7ee;
          background: #f7fafd;
          border-top-left-radius: 18px;
        }
        .side-panel-header h2 {
          font-size: 1.3rem;
          font-weight: 600;
          margin: 0;
        }
        .side-panel-close {
          font-size: 1.7rem;
          background: none;
          border: none;
          color: #888;
          cursor: pointer;
          border-radius: 50%;
          width: 36px;
          height: 36px;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: background 0.2s;
        }
        .side-panel-close:hover {
          background: #e3e7ee;
          color: #222;
        }
        .side-panel-content {
          padding: 28px;
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
