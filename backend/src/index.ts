import express from 'express';
import cors from 'cors';

const app = express();
app.use(cors());
app.use(express.json());

// Mock car data
const cars = [
  {
    name: 'Toyota Corolla Touring Sports 1.8 Hybrid Business Carplay-Ca',
    status: 'Available',
    url: 'https://marktplaats.nl/v/a/toyota-corolla',
    mileage: 92513,
    price: 19948,
    roadValue: 18800,
    notes: '里程低，business版。dealer位置在鹿特丹往南一点，100公里左右',
    phone: '0186 640 950',
    dealer: 'Autobedrijf Nieuwkoop',
    rdw: true,
    bovag: true,
    plate: 'H-401-ZX',
    year: 2020,
    apkExpiry: '2026-06-29',
  },
  {
    name: 'Toyota Corolla Touring Sports 1.8 Hybrid Active | Org NL',
    status: '已约看车',
    url: 'https://autoscout24.nl/a/toyota-corolla',
    mileage: 104780,
    price: 18750,
    roadValue: 19050,
    notes: '最后一任是私人车主。位置在海牙旁边，60公里。周六11点左右有别的test drive，所以最好12点之后去',
    phone: '0172788425',
    dealer: 'Vos en Vos Automotive',
    rdw: false,
    bovag: false,
    plate: 'K-662-BD',
    year: 2020,
    apkExpiry: '2023-11-13',
  },
  {
    name: 'Toyota Corolla Touring Sports 1.8 Hybrid Active | Camera | A',
    status: '已约看车',
    url: 'https://marktplaats.nl/v/a/toyota-corolla-camera',
    mileage: 115033,
    price: 18995,
    roadValue: 17650,
    notes: '比较均衡。乌特纳姆中间，70公里。到之前半小时联系一下他们',
    phone: '0318-520178',
    dealer: 'Vakgarage Heije',
    rdw: true,
    bovag: true,
    plate: 'H-390-DP',
    year: 2020,
    apkExpiry: '2026-01-28',
  },
];

app.get('/api/cars', (req, res) => {
  res.json(cars);
});

const PORT = 3001;
app.listen(PORT, () => {
  console.log(`Backend server running on http://localhost:${PORT}`);
});
