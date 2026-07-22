import { Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import HomePage from './page/HomePage';
import SearchResultsPage from './page/SearchResultsPage';
import ProductDetailsPage from './page/ProductDetailsPage';
import PharmaciesMapPage from './page/PharmaciesMapPage';
import './App.css';

function App() {
  return (
    <div className="app-wrapper">
      <Header />
      <main className="app-main">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/search" element={<SearchResultsPage />} />
          <Route path="/medicine/:id" element={<ProductDetailsPage />} />
          <Route path="/map" element={<PharmaciesMapPage />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

export default App;
