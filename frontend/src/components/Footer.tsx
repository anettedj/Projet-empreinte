// src/components/Footer.tsx
import { School, Copyright } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-blue-night text-white py-4 mt-auto">
      <div className="container">
        <div className="row align-items-center text-center text-md-start">
          <div className="col-md-4 mb-3 mb-md-0">
            <div className="d-flex align-items-center justify-content-center justify-content-md-start gap-2">
              <School size={20} className="icon-blue" />
              <span>École Polytechnique d'Abomey-Calavi</span>
            </div>
          </div>
          <div className="col-md-4 mb-3 mb-md-0">
            <div className="d-flex justify-content-center gap-3 flex-wrap">
              <a href="/" className="text-white text-decoration-none">Accueil</a>
              <a href="/register" className="text-white text-decoration-none">Inscription</a>
              <a href="/login" className="text-white text-decoration-none">Connexion</a>
              <a href="/dashboard" className="text-white text-decoration-none">Dashboard</a>
            </div>
          </div>
          <div className="col-md-4">
            <div className="d-flex align-items-center justify-content-center justify-content-md-end gap-1 text-sm">
              <Copyright size={14} />
              <span>2025 - Tous droits réservés</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}