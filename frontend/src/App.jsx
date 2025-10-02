import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import Navbar from './components/Navbar';
import HomePage from './components/HomePage';
import SearchPage from './components/SearchPage';
import PredictionsPage from './components/PredictionsPage';
import RecommendationsPage from './components/RecommendationsPage';
import Footer from './components/Footer';
import AuthPage from './components/AuthPage';
import HourlyConsumption from './components/HourlyConsumption';
import TariffCalculator from './components/TariffCalculator';
import Leaderboard from './components/Leaderboard';
import Chatbot from './components/Chatbot';
import ProviderDashboard from "./components/ProviderDashboard";
import TopConsumers from "./components/TopConsumers";
import SmartHouse from "./components/SmartHouse"; 

function App() {
  const [currentPage, setCurrentPage] = useState('auth');
  const [role, setRole] = useState(null);
  const [userId, setUserId] = useState(() => {
    // Load saved ID from localStorage (if any)
    return localStorage.getItem("userId") || null;
  });

  // Persist userId so refresh doesn't log out
  useEffect(() => {
    if (userId) {
      localStorage.setItem("userId", userId);
    }
  }, [userId]);

  const renderPage = () => {
    switch (currentPage) {
      case 'auth':
        return (
          <AuthPage
            setCurrentPage={setCurrentPage}
            setRole={setRole}
            setUserId={setUserId}
          />
        );
      case 'home':
        return <HomePage role={role} userId={userId} />;
      case 'search':
        return <SearchPage userId={userId} />;
      case 'predictions':
        return <PredictionsPage userId={userId} />;
      case 'recommendations':
        return <RecommendationsPage userId={userId} />;
      case 'consumption':
        return <HourlyConsumption userId={userId} />;
      case 'tariff':
        return <TariffCalculator userId={userId} />;
      case 'leaderboard':
        return <Leaderboard />;
      case 'smarthouse':
        return <SmartHouse userId={userId} />;
      case "provider-dashboard":
        return <ProviderDashboard setCurrentPage={setCurrentPage} userId={userId} />;
      case "top-consumers":
        return <TopConsumers userId={userId} />;
      default:
        return <HomePage role={role} userId={userId} />;
    }
  };

  return (
    <div>
      {currentPage !== 'auth' && (
        <Navbar
          setCurrentPage={setCurrentPage}
          currentPage={currentPage}
          role={role}
        />
      )}

      <main>{renderPage()}</main>

      {currentPage !== 'auth' && <Footer />}

      {role === 'consumer' && currentPage !== 'auth' && <Chatbot userId={userId} />}
    </div>
  );
}

const container = document.getElementById('root');
const root = createRoot(container);
root.render(<App />);
