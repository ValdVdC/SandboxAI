import React from 'react';
import Header from '../components/Header';
import '../styles/VersionComparison.css';

const VersionComparison: React.FC = () => {
  return (
    <>
      <Header />
      <div className="version-comparison-page">
        <h1>Comparação de Versões</h1>
        <p>Esta página permite comparar side-by-side duas versões diferentes de um prompt.</p>
      </div>
    </>
  );
};

export default VersionComparison;
