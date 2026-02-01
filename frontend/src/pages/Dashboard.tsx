// src/pages/Dashboard.tsx
import { useState, useEffect, useRef } from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import {
  Fingerprint,
  Search,
  Image as ImageIcon,
  LogOut,
  Upload,
  CheckCircle,
  Loader2
} from 'lucide-react';

type MenuItem = 'compare' | 'search' | 'process';

export default function Dashboard() {
  const [activeMenu, setActiveMenu] = useState<MenuItem>('search');

  // Fichiers bruts
  const [compareFiles, setCompareFiles] = useState<(File | null)[]>([null, null]);
  const [searchFile, setSearchFile] = useState<File | null>(null);

  // Prévisualisations en base64
  const [comparePreviews, setComparePreviews] = useState<(string | null)[]>([null, null]);
  const [searchPreview, setSearchPreview] = useState<string | null>(null);

  // Pour le traitement d'image
  const [processedImage, setProcessedImage] = useState<any | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processStage, setProcessStage] = useState<"original" | "clahe" | "gabor" | "binary" | "skeleton">("skeleton");

  // Résultats
  const [compareResult, setCompareResult] = useState<any>(null);
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [isComparing, setIsComparing] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [showDetails, setShowDetails] = useState(false); // NOUVEAU: État pour afficher les détails


  // Refs
  const compareRef1 = useRef<HTMLInputElement>(null);
  const compareRef2 = useRef<HTMLInputElement>(null);
  const searchRef = useRef<HTMLInputElement>(null);
  const processRef = useRef<HTMLInputElement>(null);

  // Chargement de l'utilisateur


  // Fonction universelle de chargement (marche à 100%)
  const handleFile = (e: React.ChangeEvent<HTMLInputElement>, index?: number) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;

      if (index !== undefined) {
        setComparePreviews(prev => {
          const arr = [...prev];
          arr[index] = result;
          return arr;
        });
        setCompareFiles(prev => {
          const arr = [...prev];
          arr[index] = file;
          return arr;
        });
      } else {
        setSearchPreview(result);
        setSearchFile(file);
      }
    };
    reader.readAsDataURL(file);
  };

  const launchComparison = async () => {
    if (!compareFiles[0] || !compareFiles[1]) return;

    setIsComparing(true);
    setCompareResult(null);

    const formData = new FormData();
    formData.append("file1", compareFiles[0]!, "empreinte1.jpg");
    formData.append("file2", compareFiles[1]!, "empreinte2.jpg");

    try {
      const res = await fetch("http://127.0.0.1:8000/compare/", {
        method: "POST",
        body: formData
      });

      if (!res.ok) {
        const err = await res.text();
        console.error("Backend error:", err);
        setCompareResult({ similarity: 0, verdict: "Erreur backend" });
        return;
      }

      const data = await res.json();
      setCompareResult(data);
    } catch (err) {
      setCompareResult({ similarity: 0, verdict: "Serveur hors ligne" });
    } finally {
      setIsComparing(false);
    }
  };

  const launchSearch = async () => {
    if (!searchFile) return;
    setIsSearching(true);
    setSearchResults([]);

    const formData = new FormData();
    formData.append("fingerprint", searchFile);

    try {
      const res = await fetch("http://127.0.0.1:8000/search/", {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      setSearchResults(data.matches || []);
    } catch {
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  // TRAITEMENT & ANALYSE DÉTAILLÉE (NOUVEAU)
  const launchProcess = async () => {
    if (!compareFiles[0] || !compareFiles[1]) return;

    setIsProcessing(true);
    setProcessedImage(null); // Will store the JSON object now

    const formData = new FormData();
    formData.append("file1", compareFiles[0]);
    formData.append("file2", compareFiles[1]);
    formData.append("stage", processStage);

    try {
      // Note: On appelle /analyze maintenant
      const res = await fetch("http://127.0.0.1:8000/process/analyze", {
        method: "POST",
        body: formData
      });

      if (!res.ok) throw new Error("Erreur traitement");

      const data = await res.json();
      // data contains: image1_processed, image2_processed, match_visualization, stats
      setProcessedImage(data as any);
    } catch (err) {
      alert("Erreur lors du traitement");
      console.error(err);
    } finally {
      setIsProcessing(false);
    }
  };

  // Nettoyage des URL blob
  useEffect(() => {
    return () => {
      if (processedImage) URL.revokeObjectURL(processedImage);
    };
  }, [processedImage]);

  return (
    <div className="d-flex flex-column min-vh-100 bg-light">
      <Header />
      <div className="flex-grow-1 d-flex">
        <div className="sidebar-menu bg-blue-night text-white">
          <div className="p-4">
            <h5 className="mb-4 fw-bold">Menu</h5>
            <ul className="nav flex-column gap-2">
              {[
                { id: 'compare', label: 'Comparer', icon: Fingerprint },
                { id: 'search', label: 'Rechercher', icon: Search },
                { id: 'process', label: 'Traiter', icon: ImageIcon },
              ].map((item) => (
                <li key={item.id}>
                  <button
                    className={`menu-btn w-100 text-start ${activeMenu === item.id ? 'active' : ''}`}
                    onClick={() => setActiveMenu(item.id as MenuItem)}
                  >
                    <item.icon size={20} className="me-2" />
                    {item.label}
                  </button>
                </li>
              ))}
              <li className="mt-auto pt-5">
                <a href="/" className="menu-btn text-white text-start w-100">
                  <LogOut size={20} className="me-2" />
                  Retour Accueil
                </a>
              </li>
            </ul>
          </div>
        </div>

        <main className="flex-grow-1 p-4 bg-white">
          <div className="container-fluid">
            <div className="d-flex justify-content-between align-items-center mb-5">
              <h1 className="h3 fw-bold text-blue-night">
                {activeMenu === 'compare' && 'Comparer deux empreintes'}
                {activeMenu === 'search' && 'Rechercher dans la base'}
                {activeMenu === 'process' && "Traitement d'image"}
                {activeMenu === 'process' && "Traitement d'image"}
              </h1>
            </div>

            {/* COMPARAISON */}
            {activeMenu === 'compare' && (
              <div className="row g-4">
                {[0, 1].map((i) => (
                  <div key={i} className="col-md-6">
                    <div
                      className="upload-zone border-2 border-dashed border-gray-300 rounded-3 p-5 text-center cursor-pointer hover:border-emerald transition"
                      onClick={() => (i === 0 ? compareRef1.current : compareRef2.current)?.click()}
                    >
                      <input
                        type="file"
                        accept="image/*"
                        hidden
                        ref={i === 0 ? compareRef1 : compareRef2}
                        onChange={(e) => handleFile(e, i)}
                      />
                      {comparePreviews[i] ? (
                        <div>
                          <img
                            src={comparePreviews[i]!}
                            alt="Empreinte"
                            className="uploaded-img rounded-3 shadow"
                            style={{ maxHeight: '380px', width: '100%', objectFit: 'contain' }}
                          />
                          <p className="mt-3 text-emerald">
                            <CheckCircle size={24} /> Image sélectionnée
                          </p>
                        </div>
                      ) : (
                        <div className="text-muted">
                          <Upload size={48} className="mb-3" />
                          <p className="fs-5">Cliquez pour choisir l'empreinte {i + 1}</p>
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {compareFiles[0] && compareFiles[1] && (
                  <div className="col-12 text-center mt-8">
                    <button
                      onClick={launchComparison}
                      disabled={isComparing}
                      className="btn btn-emerald btn-lg px-8 py-4 shadow-lg text-xl fw-bold"
                    >
                      {isComparing ? (
                        <>Analyse en cours <Loader2 className="animate-spin ms-3" /></>
                      ) : (
                        "Lancer la comparaison"
                      )}
                    </button>

                    {compareResult && (
                      <div className={`mt-10 p-10 rounded-4 shadow-2xl border-8 max-w-4xl mx-auto ${compareResult.similarity > 65 ? 'bg-emerald-100 border-emerald' : 'bg-red-100 border-red'}`}>
                        <h2 className={`text-9xl font-black ${compareResult.similarity > 65 ? 'text-emerald-900' : 'text-red-900'}`}>
                          {compareResult.similarity}%
                        </h2>
                        <p className="text-4xl fw-bold mt-6 text-blue-night">
                          {compareResult.verdict || "Analyse terminée"}
                        </p>
                        {compareResult.similarity > 85 && (
                          <div className="mt-8 p-8 bg-emerald-700 text-white rounded-3 text-5xl font-black">
                            IDENTITÉ CONFIRMÉE
                          </div>
                        )}

                        {/* BOUTON DÉTAILS */}
                        <button
                          className="btn btn-outline-dark mt-4"
                          onClick={() => setShowDetails(!showDetails)}
                        >
                          {showDetails ? "Masquer les détails" : "Voir les détails techniques"}
                        </button>

                        {/* SECTION DÉTAILS */}
                        {showDetails && (
                          <div className="mt-4 p-4 bg-white rounded shadow text-start">
                            <h4 className="fw-bold text-blue-night border-bottom pb-2 mb-3">Détails de l'Analyse</h4>
                            <div className="row">
                              <div className="col-md-4 text-center border-end">
                                <div className="text-muted small">Minuties (Img 1)</div>
                                <div className="fs-4 fw-bold text-dark">{compareResult.minutiae_img1}</div>
                              </div>
                              <div className="col-md-4 text-center border-end">
                                <div className="text-muted small">Minuties (Img 2)</div>
                                <div className="fs-4 fw-bold text-dark">{compareResult.minutiae_img2}</div>
                              </div>
                              <div className="col-md-4 text-center">
                                <div className="text-muted small">Correspondances</div>
                                <div className="fs-4 fw-bold text-emerald">{compareResult.matches_found}</div>
                              </div>
                            </div>

                            <div className="mt-3 bg-light p-3 rounded small">
                              <strong>Méthode :</strong> {compareResult.details?.algo} <br />
                              <em>{compareResult.details?.description}</em>
                            </div>

                            {compareResult.visualization && (
                              <div className="mt-3 text-center">
                                <div className="text-muted small mb-1">Visualisation des points communs :</div>
                                <img src={compareResult.visualization} alt="Matches" className="img-fluid rounded border" />
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                  </div>

                )}
              </div>
            )}

            {/* RECHERCHE */}
            {activeMenu === 'search' && (
              <div>
                {/* === ZONE UPLOAD – inchangée === */}
                <div
                  className="upload-zone border-2 border-dashed border-gray-300 rounded-3 p-5 text-center cursor-pointer hover:border-emerald transition mb-5"
                  onClick={() => searchRef.current?.click()}
                >
                  <input
                    type="file"
                    accept="image/*"
                    hidden
                    ref={searchRef}
                    onChange={(e) => handleFile(e)}
                  />
                  {searchPreview ? (
                    <div>
                      <img
                        src={searchPreview}
                        alt="Recherche"
                        className="uploaded-img rounded-3 shadow"
                        style={{ maxHeight: '380px', width: '100%', objectFit: 'contain' }}
                        onError={(e) => {
                          (e.target as HTMLImageElement).onerror = null; // prevent loop
                          (e.target as HTMLImageElement).src = "https://via.placeholder.com/400x300/e0e0e0/333333?text=Aperçu+non+disponible+(Format+non+supporté)";
                        }}
                      />
                      <p className="mt-3 text-emerald">
                        <CheckCircle size={24} /> Image sélectionnée
                      </p>
                      {searchFile?.name.toLowerCase().endsWith('.tif') && (
                        <p className="text-muted small">Le format .tif peut ne pas s'afficher ici, mais l'analyse fonctionnera.</p>
                      )}
                    </div>
                  ) : (
                    <div className="text-muted">
                      <Search size={48} className="mb-3" />
                      <p className="fs-5">Cliquez pour choisir une empreinte à rechercher</p>
                    </div>
                  )}
                </div>

                {searchFile && (
                  <div className="text-center mb-8">
                    <button
                      onClick={launchSearch}
                      disabled={isSearching}
                      className="btn btn-emerald btn-lg px-8 py-4 shadow-lg text-xl fw-bold"
                    >
                      {isSearching ? (
                        <>Recherche en cours <Loader2 className="animate-spin ms-3" /></>
                      ) : (
                        "Rechercher dans la base"
                      )}
                    </button>
                  </div>
                )}

                {/* === RÉSULTATS + DIAGRAMME === */}
                {searchResults.length > 0 && (
                  <div className="search-results">

                    <h4 className="mb-4 text-blue-night fw-bold">Résultats trouvés</h4>

                    {/* === CARTES – PHOTOS CORRIGÉES + PLACEHOLDER === */}
                    <div className="row g-4 mb-5">
                      {searchResults.map((res: any, i: number) => (
                        <div key={i} className="col-md-4">
                          <div className="card h-100 shadow-sm border-0">
                            <div className="card-body d-flex align-items-center gap-3">
                              <img
                                src={
                                  res.photo_profil
                                    ? `http://127.0.0.1:8000/uploads/profiles/${res.photo_profil}`
                                    : "https://via.placeholder.com/80/6366f1/ffffff?text=Person"
                                }
                                alt={res.nom}
                                className="result-photo rounded-circle"
                                style={{ width: '60px', height: '60px', objectFit: 'cover' }}
                                onError={(e) => {
                                  (e.target as HTMLImageElement).src = "https://via.placeholder.com/80/6366f1/ffffff?text=Person";
                                }}
                              />
                              <div>
                                <h6 className="mb-0 fw-bold">{res.nom} {res.prenom || ''}</h6>
                                <p className="text-emerald fw-bold mb-0">{res.similarity}%</p>
                                {res.similarity > 85 && (
                                  <span className="badge bg-emerald text-white">CORRESPONDANCE FORTE</span>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* === DIAGRAMME EXACTEMENT COMME TU VEUX === */}
                    <div className="bg-white rounded-3 shadow-lg p-4">
                      <h5 className="text-center fw-bold text-blue-night mb-3">Taux de correspondance</h5>

                      <div className="overflow-x-auto">
                        <svg width="100%" height="400" viewBox="0 0 920 400" style={{ fontFamily: 'Arial, sans-serif' }}>
                          {/* Fond de la grille */}
                          <defs>
                            <pattern id="grid" width="100" height="28" patternUnits="userSpaceOnUse">
                              <path d="M 100 0 L 0 0 0 28" fill="none" stroke="#f0f0f0" strokeWidth="1" />
                            </pattern>
                          </defs>
                          <rect x="90" y="40" width="790" height="280" fill="url(#grid)" />

                          {/* Cadre style Matlab (Box) */}
                          <rect x="90" y="40" width="790" height="280" fill="none" stroke="#333" strokeWidth="1.5" />

                          {/* Graduations Y et Ticks */}
                          {[0, 20, 40, 60, 80, 100].map(val => (
                            <g key={val}>
                              {/* Tick mark intérieur */}
                              <line x1="90" y1={320 - val * 2.8} x2="98" y2={320 - val * 2.8} stroke="#333" strokeWidth="1" />
                              {/* Tick mark extérieur (droit) */}
                              <line x1="880" y1={320 - val * 2.8} x2="872" y2={320 - val * 2.8} stroke="#333" strokeWidth="1" />

                              {/* Ligne pointillée fine */}
                              <line x1="98" y1={320 - val * 2.8} x2="872" y2={320 - val * 2.8} stroke="#ddd" strokeWidth="1" strokeDasharray="4" />

                              <text x="80" y={325 - val * 2.8} textAnchor="end" fontSize="12" fill="#333">
                                {val}%
                              </text>
                            </g>
                          ))}

                          {/* Barres propres et fines */}
                          {searchResults.map((res: any, i: number) => {
                            const x = 140 + i * 80; // Espacement ajusté
                            if (x > 850) return null; // Avoid overflow
                            const height = res.similarity * 2.8;
                            const y = 320 - height;

                            const color = res.similarity >= 85 ? "#10b981" :
                              res.similarity >= 60 ? "#f59e0b" : "#ef4444";

                            return (
                              <g key={i}>
                                {/* Barre avec bordure fine */}
                                <rect x={x} y={y} width="40" height={height} fill={color} stroke="#333" strokeWidth="0.5" />

                                {/* Pourcentage au dessus */}
                                <text x={x + 20} y={y - 10} textAnchor="middle" fontSize="12" fontWeight="bold" fill="#333">
                                  {Math.round(res.similarity)}%
                                </text>

                                {/* Nom en bas (rotation si besoin, ici simple) */}
                                <text x={x + 20} y="340" textAnchor="middle" fontSize="11" fill="#333" style={{ textTransform: 'capitalize' }}>
                                  {res.nom.split(" ")[0]}
                                </text>
                              </g>
                            );
                          })}
                        </svg>
                      </div>

                      {/* Légende discrète */}
                      {/* LÉGENDE PROPRE ET COLORÉE */}
                      <div className="d-flex justify-content-center gap-5 mt-4">
                        <div className="d-flex align-items-center gap-2">
                          <div className="w-5 h-5 bg-teal-600 rounded"></div>
                          <span className="font-medium text-gray-700">≥ 85% – Match confirmé</span>
                        </div>
                        <div className="d-flex align-items-center gap-2">
                          <div className="w-5 h-5 bg-orange-600 rounded"></div>
                          <span className="font-medium text-gray-700">60–84% – Similitude moyenne</span>
                        </div>
                        <div className="d-flex align-items-center gap-2">
                          <div className="w-5 h-5 bg-red-600 rounded"></div>
                          <span className="font-medium text-gray-700">&lt; 60% – Faible correspondance</span>
                        </div>
                      </div>
                    </div>

                  </div>
                )}
              </div>
            )}

            {/* TRAITEMENT D'IMAGE & COMPARAISON DÉTAILLÉE */}
            {activeMenu === 'process' && (
              <div className="row g-5">
                {/* COLONNE GAUCHE : UPLOAD & OPTIONS */}
                <div className="col-md-4">
                  <div className="bg-white p-4 rounded-4 shadow-sm mb-4">
                    <h5 className="fw-bold text-blue-night mb-3">1. Charger les empreintes</h5>

                    {/* Image 1 */}
                    <div className="mb-3">
                      <label className="form-label fw-bold small text-muted">Image 1</label>
                      <div
                        className="border rounded-3 p-2 text-center cursor-pointer hover:bg-gray-50 transition"
                        onClick={() => compareRef1.current?.click()}
                        style={{ height: '100px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                      >
                        <input type="file" hidden ref={compareRef1} onChange={(e) => handleFile(e, 0)} />
                        {comparePreviews[0] ? (
                          <img src={comparePreviews[0]!} className="h-100 mw-100 object-contain" alt="1" />
                        ) : <span className="text-muted small">+ Choisir Image 1</span>}
                      </div>
                    </div>

                    {/* Image 2 */}
                    <div className="mb-4">
                      <label className="form-label fw-bold small text-muted">Image 2</label>
                      <div
                        className="border rounded-3 p-2 text-center cursor-pointer hover:bg-gray-50 transition"
                        onClick={() => compareRef2.current?.click()}
                        style={{ height: '100px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                      >
                        <input type="file" hidden ref={compareRef2} onChange={(e) => handleFile(e, 1)} />
                        {comparePreviews[1] ? (
                          <img src={comparePreviews[1]!} className="h-100 mw-100 object-contain" alt="2" />
                        ) : <span className="text-muted small">+ Choisir Image 2</span>}
                      </div>
                    </div>

                    <h5 className="fw-bold text-blue-night mb-3">2. Choisir le traitement</h5>
                    <select
                      className="form-select mb-4"
                      value={processStage}
                      onChange={(e) => setProcessStage(e.target.value as any)}
                    >
                      <option value="original">Original (Pas de filtre)</option>
                      <option value="clahe">Amélioration contraste (CLAHE)</option>
                      <option value="gabor">Filtre de Gabor (Détection Crêtes)</option>
                      <option value="binary">Binarisation (Noir & Blanc)</option>
                      <option value="skeleton">Squelettisation (Minutiae)</option>
                    </select>

                    <button
                      onClick={launchProcess}
                      disabled={isProcessing || !compareFiles[0] || !compareFiles[1]}
                      className="btn btn-emerald w-100 py-3 fw-bold shadow"
                    >
                      {isProcessing ? <Loader2 className="animate-spin mx-auto" /> : "TRAITER & COMPARER"}
                    </button>
                    {!compareFiles[1] && <small className="text-danger d-block mt-2 text-center">Ajoutez 2 images pour comparer</small>}
                  </div>
                </div>

                {/* COLONNE DROITE : RÉSULTATS VISUALISÉS */}
                <div className="col-md-8">
                  {processedImage ? (
                    <div className="d-flex flex-column gap-4">

                      {/* LIGNE 1: COMPARAISON CÔTE À CÔTE */}
                      <div className="row g-3">
                        <div className="col-6">
                          <div className="bg-white p-3 rounded-3 shadow-sm text-center h-100">
                            <h6 className="fw-bold text-muted mb-2">Image 1 Traitée ({processStage})</h6>
                            <img src={(processedImage as any).image1_processed} className="img-fluid rounded border" alt="Proc 1" />
                          </div>
                        </div>
                        <div className="col-6">
                          <div className="bg-white p-3 rounded-3 shadow-sm text-center h-100">
                            <h6 className="fw-bold text-muted mb-2">Image 2 Traitée ({processStage})</h6>
                            <img src={(processedImage as any).image2_processed} className="img-fluid rounded border" alt="Proc 2" />
                          </div>
                        </div>
                      </div>

                      {/* LIGNE 2: PREUVE VISUELLE */}
                      <div className="bg-white p-4 rounded-4 shadow text-center">
                        <h5 className="fw-bold text-emerald mb-3">Preuve de Comparaison (Matching)</h5>
                        <p className="text-muted small mb-3">
                          Les lignes vertes relient les caractéristiques identiques trouvées sur les deux images traitées.
                        </p>
                        <img
                          src={(processedImage as any).match_visualization}
                          className="img-fluid rounded-3 border border-2 border-emerald"
                          style={{ maxHeight: '400px' }}
                          alt="Preuve"
                        />

                        <div className="row mt-4 pt-3 border-top">
                          <div className="col-4 border-end">
                            <div className="text-muted small text-uppercase fw-bold">Points Communs</div>
                            <div className="fs-2 fw-black text-emerald">{(processedImage as any).stats.matches}</div>
                          </div>
                          <div className="col-8">
                            <div className="text-muted small text-uppercase fw-bold">Score de Similitude</div>
                            <div className="display-6 fw-black text-blue-night">{(processedImage as any).stats.score}%</div>
                            <div className="progress mt-2" style={{ height: '6px' }}>
                              <div
                                className="progress-bar bg-emerald"
                                role="progressbar"
                                style={{ width: `${(processedImage as any).stats.score}%` }}
                              ></div>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* LIGNE 3: EXPLICATIONS DÉTAILLÉES (DEMANDE UTILISATEUR) */}
                      <div className="bg-blue-night text-white p-4 rounded-4 shadow">
                        <h5 className="fw-bold mb-3 border-bottom border-light pb-2">
                          <CheckCircle className="me-2 d-inline" size={24} />
                          Comprendre le Résultat
                        </h5>
                        <div className="fs-6" style={{ lineHeight: '1.6' }}>
                          {/* On utilise white-space: pre-line pour respecter les sauts de ligne du backend */}
                          <div style={{ whiteSpace: 'pre-line' }}>
                            {(processedImage as any).explanation}
                          </div>
                        </div>
                      </div>

                    </div>
                  ) : (
                    <div className="bg-light rounded-4 h-100 d-flex align-items-center justify-content-center text-muted p-5 border-2 border-dashed">
                      <div className="text-center opacity-50">
                        <ImageIcon size={64} className="mb-3" />
                        <p className="fs-5">Chargez deux images et lancez le traitement pour voir la comparaison détaillée ici.</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}


          </div>
        </main>
      </div>
      <Footer />
    </div>
  );
}