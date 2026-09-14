import { useState, useEffect } from 'react';
import Header from './components/Header.jsx';
import SentimentAnalyzer from './components/SentimentAnalyzer.jsx';
import Footer from './components/Footer.jsx';

export default function App() {
  const [apiStatus, setApiStatus] = useState('checking');

  useEffect(() => {
    fetch('http://localhost:8000/')
      .then((res) => (res.ok ? setApiStatus('online') : setApiStatus('offline')))
      .catch(() => setApiStatus('offline'));
  }, []);

  return (
    <div className="min-h-screen bg-[#1c1c1c] text-white flex flex-col font-sans selection:bg-white selection:text-black">
      <Header apiStatus={apiStatus} />
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 sm:px-12 py-12">
        <SentimentAnalyzer />
      </main>
      <Footer />
    </div>
  );
}