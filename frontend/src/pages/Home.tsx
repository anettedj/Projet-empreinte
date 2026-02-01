// src/pages/Home.tsx
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Upload, Search, Shield, UserPlus, LogIn } from 'lucide-react';

export default function Home() {
  return (
    <div className="d-flex flex-column min-vh-100">
      <Header />

      {/* TITRE SUR L'IMAGE */}
      <div className="title-bg-image">
        <div className="title-content">
          <h1 className="display-4 fw-bold text-white">
            Bienvenue sur l’Application de <span>Traitement & Gestion</span> d’Empreintes Digitales
          </h1>
        </div>
      </div>

      {/* SOUS-TITRE EN DESSOUS (SUR LE FOND DU SITE) */}
      <div className="container py-4">
        <p className="lead text-muted text-center col-lg-8 mx-auto">
          Une solution sécurisée, rapide et précise pour l’enregistrement, la comparaison et l’identification d’empreintes digitales.
        </p>
      </div>

      <main className="flex-grow-1 py-5">
        <div className="container">
          {/* Boutons */}
          <div className="row justify-content-center mb-5">
            <div className="col-md-6 mb-4">
              <a href="/dashboard" className="btn btn-blue-night btn-lg w-100 d-flex align-items-center justify-content-center gap-2">
                <Shield size={24} />
                Accéder au Tableau de Bord
              </a>
            </div>
          </div>

          {/* Comment ça marche */}
          <h2 className="text-center display-6 fw-bold text-blue-night mb-5">Comment ça marche ?</h2>

          <div className="row g-4">
            {/* Étape 1 */}
            <div className="col-md-4">
              <div className="text-center p-4 bg-white rounded shadow-sm h-100 card-hover">
                <Upload size={40} className="step-icon step-icon-emerald mb-3" />
                <h4 className="step-title-emerald">1. Inscription</h4>
                <p className="text-muted">Importez jusqu’à 8 empreintes digitales (une par doigt).</p>
              </div>
            </div>

            {/* Étape 2 */}
            <div className="col-md-4">
              <div className="text-center p-4 bg-white rounded shadow-sm h-100 card-hover">
                <Search size={40} className="step-icon step-icon-purple mb-3" />
                <h4 className="step-title-purple">2. Analyse</h4>
                <p className="text-muted">Nos algorithmes extraient les points caractéristiques.</p>
              </div>
            </div>

            {/* Étape 3 */}
            <div className="col-md-4">
              <div className="text-center p-4 bg-white rounded shadow-sm h-100 card-hover">
                <Shield size={40} className="step-icon step-icon-orange mb-3" />
                <h4 className="step-title-orange">3. Identification</h4>
                <p className="text-muted">Comparez en temps réel avec la base de données.</p>
              </div>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}