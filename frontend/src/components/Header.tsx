// src/components/Header.tsx
import { Fingerprint, UserPlus, LogIn } from 'lucide-react';

export default function Header() {
  return (
    <nav className="navbar navbar-expand-lg bg-blue-night shadow-lg">
      <div className="container-fluid">
        <a className="navbar-brand text-white d-flex align-items-center gap-2" href="/">
          <Fingerprint size={28} className="icon-blue" />
          <span className="fw-bold">Empreintes Digitales</span>
        </a>
        <div className="ms-auto d-flex gap-2">
          <a href="/register" className="btn btn-blue-night btn-sm d-flex align-items-center gap-1">
            <UserPlus size={18} />
            <span className="d-none d-md-inline">S'inscrire</span>
          </a>
          <a href="/login" className="btn btn-outline-blue-night btn-sm d-flex align-items-center gap-1">
            <LogIn size={18} />
            <span className="d-none d-md-inline">Connexion</span>
          </a>
        </div>
      </div>
    </nav>
  );
}