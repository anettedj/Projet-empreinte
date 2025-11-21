// src/pages/Dashboard.tsx
import { useState } from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import {useEffect } from 'react'; 
import { 
  Fingerprint, Search, Image as ImageIcon, User, LogOut, 
  Upload, CheckCircle, XCircle, Download, Filter
} from 'lucide-react';

type MenuItem = 'compare' | 'search' | 'process' | 'profile';

export default function Dashboard() {
  const [activeMenu, setActiveMenu] = useState<MenuItem>('profile');// ← assure-toi que useEffect est importé

const [user, setUser] = useState<any>(null);

useEffect(() => {
  const savedUser = localStorage.getItem("currentUser");
  if (savedUser) {
    setUser(JSON.parse(savedUser));
  } else {
    window.location.href = "/login"; 
  }
}, []);

  const [compareFiles, setCompareFiles] = useState<(File | null)[]>([null, null]);
  const [searchFile, setSearchFile] = useState<File | null>(null);
  const [processFile, setProcessFile] = useState<File | null>(null);

  // SIMULATION : résultats de comparaison
  const mockResults = [
    { name: "Marie Curie", similarity: 94, photo: "https://via.placeholder.com/80" },
    { name: "Albert Einstein", similarity: 87, photo: "https://via.placeholder.com/80" },
    { name: "Léonard de Vinci", similarity: 72, photo: null },
  ];

  const handleFileDrop = (index: number, e: React.DragEvent, setter: Function) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      setter(index === -1 ? file : (prev: any) => {
        const arr = [...prev];
        arr[index] = file;
        return arr;
      });
    }
  };

  const renderContent = () => {
    switch (activeMenu) {
      case 'compare':
        return (
          <div className="row g-4">
            {[0, 1].map((i) => (
              <div key={i} className="col-md-6">
                <div
                  className="upload-zone"
                  onDrop={(e) => handleFileDrop(i, e, setCompareFiles)}
                  onDragOver={(e) => e.preventDefault()}
                >
                  {compareFiles[i] ? (
                    <div className="text-center">
                      <img
                        src={URL.createObjectURL(compareFiles[i]!)}
                        alt="Empreinte"
                        className="uploaded-img"
                      />
                      <p className="mt-2 text-emerald">
                        <CheckCircle size={20} /> Chargée
                      </p>
                    </div>
                  ) : (
                    <div className="text-center text-muted">
                      <Upload size={48} className="mb-2" />
                      <p>Glissez l'empreinte {i + 1}</p>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {compareFiles[0] && compareFiles[1] && (
              <div className="col-12 text-center">
                <div className="comparison-result">
                  <h3 className="text-emerald">Similarité : 89%</h3>
                  <p>Les deux empreintes correspondent très probablement à la même personne.</p>
                </div>
              </div>
            )}
          </div>
        );

      case 'search':
        return (
          <div>
            <div
              className="upload-zone mb-4"
              onDrop={(e) => handleFileDrop(-1, e, setSearchFile)}
              onDragOver={(e) => e.preventDefault()}
            >
              {searchFile ? (
                <div className="text-center">
                  <img
                    src={URL.createObjectURL(searchFile)}
                    alt="Recherche"
                    className="uploaded-img"
                  />
                  <p className="mt-2 text-emerald">
                    <CheckCircle size={20} /> Chargée
                  </p>
                </div>
              ) : (
                <div className="text-center text-muted">
                  <Search size={48} className="mb-2" />
                  <p>Glissez une empreinte pour chercher dans la base</p>
                </div>
              )}
            </div>

            {searchFile && (
              <div className="search-results">
                <h4 className="mb-3">Résultats dans la base de données</h4>
                <div className="row g-3">
                  {mockResults.map((res, i) => (
                    <div key={i} className="col-md-4">
                      <div className="result-card">
                        <div className="d-flex align-items-center gap-3">
                          {res.photo ? (
                            <img src={res.photo} alt={res.name} className="result-photo" />
                          ) : (
                            <div className="result-photo placeholder-bg">
                              <User size={24} />
                            </div>
                          )}
                          <div>
                            <h6 className="mb-0">{res.name}</h6>
                            <p className="text-emerald mb-0">{res.similarity}%</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        );

      case 'process':
        return (
          <div>
            <div
              className="upload-zone mb-4"
              onDrop={(e) => handleFileDrop(-1, e, setProcessFile)}
              onDragOver={(e) => e.preventDefault()}
            >
              {processFile ? (
                <div className="text-center">
                  <img
                    src={URL.createObjectURL(processFile)}
                    alt="Traitement"
                    className="uploaded-img"
                  />
                  <div className="mt-3 d-flex justify-content-center gap-2">
                    <button className="btn btn-emerald btn-sm">
                      <Filter size={16} /> Appliquer filtre
                    </button>
                    <button className="btn btn-blue-night btn-sm text-white">
                      <Download size={16} /> Télécharger
                    </button>
                  </div>
                </div>
              ) : (
                <div className="text-center text-muted">
                  <ImageIcon size={48} className="mb-2" />
                  <p>Glissez une empreinte à traiter</p>
                </div>
              )}
            </div>
          </div>
        );

      case 'profile':
        return (
          <div className="text-center">
            <img src={user.photo} alt="Profil" className="profile-large" />
            <h3 className="mt-3">{user.name}</h3>
            <p className="text-muted">{user.email}</p>
            <p className="text-emerald">8 empreintes enregistrées</p>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="d-flex flex-column min-vh-100">
      <Header />
      <div className="flex-grow-1 d-flex">
        {/* MENU GAUCHE */}
        <div className="sidebar-menu">
          <div className="p-4">
            <h5 className="text-white mb-4">Menu</h5>
            <ul className="nav flex-column gap-2">
              {[
                 { id: 'profile', label: 'Profil', icon: User },
                { id: 'compare', label: 'Comparer', icon: Fingerprint },
                { id: 'search', label: 'Rechercher', icon: Search },
                { id: 'process', label: 'Traiter', icon: ImageIcon },
              ].map((item) => (
                <li key={item.id}>
                  <button
                    className={`menu-btn ${activeMenu === item.id ? 'active' : ''}`}
                    onClick={() => setActiveMenu(item.id as MenuItem)}
                  >
                    <item.icon size={20} />
                    {item.label}
                  </button>
                </li>
              ))}
              <li className="mt-auto">
                <a href="/login" className="menu-btn text-white">
                  <LogOut size={20} />
                  Déconnexion
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* CONTENU PRINCIPAL */}
        <main className="flex-grow-1 p-4">
          <div className="container-fluid">
            <div className="d-flex justify-content-between align-items-center mb-4">
              <h2 className="h4 fw-bold text-blue-night">
                {activeMenu === 'compare' && 'Comparer deux empreintes'}
                {activeMenu === 'search' && 'Rechercher dans la base'}
                {activeMenu === 'process' && 'Traitement d\'image'}
                {activeMenu === 'profile' && 'Mon profil'}
              </h2>
            </div>
            {renderContent()}
          </div>
        </main>
      </div>
      <Footer />
    </div>
  );
}