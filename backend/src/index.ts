import express from 'express';
import cors from 'cors';
import sqlite3 from 'sqlite3';
import path from 'path';

const app = express();
app.use(cors());
app.use(express.json());

const DB_PATH = path.join(__dirname, '../../scraper/cars.db');

function toCamelCase(obj: any) {
  const newObj: any = {};
  for (const key in obj) {
    const camelKey = key.replace(/_([a-z])/g, (_, g1) => g1.toUpperCase());
    newObj[camelKey] = obj[key];
  }
  return newObj;
}

app.get('/api/cars', (req, res) => {
  const db = new sqlite3.Database(DB_PATH);

  const sql = `
    SELECT
      r.price, r.mileage, r.year, r.place, 
      n.*
    FROM raw_cars r
    JOIN normalized_cars n ON r.url = n.url
    WHERE DATE(r.scraped_at) = DATE('now', 'localtime')
  `;

  db.all(sql, [], (err, rows) => {
    db.close();
    if (err) {
      res.status(500).json({ error: 'Failed to load car data from database.' });
      return;
    }
    const camelRows = rows.map(toCamelCase);
    res.json(camelRows);
  });
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`Backend server running on http://localhost:${PORT}`);
});
