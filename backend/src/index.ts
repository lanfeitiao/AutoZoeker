import express from 'express';
import cors from 'cors';
import fs from 'fs';
import path from 'path';

const app = express();
app.use(cors());
app.use(express.json());

const DATA_PATH = path.join(__dirname, '../../scraper/gaspedaal_cars.json');

app.get('/api/cars', (req, res) => {
  try {
    const data = fs.readFileSync(DATA_PATH, 'utf-8');
    const cars = JSON.parse(data);
    res.json(cars);
  } catch (err) {
    res.status(500).json({ error: 'Failed to load car data.' });
  }
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`Backend server running on http://localhost:${PORT}`);
});
