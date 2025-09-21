import { Routes, Route } from 'react-router-dom';
import HomePage from "./page/HomePage";
import SearchResultsPage from "./page/SearchResultsPage";
import ProductDetailsPage from "./page/ProductDetailsPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/search" element={<SearchResultsPage />} />
      <Route path="/medicine/:id" element={<ProductDetailsPage />} />
    </Routes>
  );
}

export default App;
