// src/pages/Register.tsx
import { useState } from 'react';
import { User, Mail, Lock, Upload, Fingerprint, X } from 'lucide-react';
import Header from '../components/Header';
import Footer from '../components/Footer';

const DOIGTS = [
  'Pouce droit',
  'Index droit',
  'Majeur droit',
  'Annulaire droit',
  'Auriculaire droit',
  'Pouce gauche',
  'Index gauche',
  'Majeur gauche'
];

interface Empreinte {
  file: File;
  preview: string;
  doigt: string;
}

export default function Register() {
  const [formData, setFormData] = useState({
    nom: '',
    email: '',
    password: ''
  });
  const [photoProfil, setPhotoProfil] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string>('');
  const [empreintes, setEmpreintes] = useState<(Empreinte | null)[]>(Array(8).fill(null));
  const [dragOver, setDragOver] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handlePhoto = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setPhotoProfil(file);
      const reader = new FileReader();
      reader.onloadend = () => setPhotoPreview(reader.result as string);
      reader.readAsDataURL(file);
    }
  };

  const handleDrop = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    setDragOver(null);
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setEmpreintes(prev => {
          const updated = [...prev];
          updated[index] = { file, preview: reader.result as string, doigt: DOIGTS[index] };
          return updated;
        });
      };
      reader.readAsDataURL(file);
    }
  };

  const removeEmpreinte = (index: number) => {
    setEmpreintes(prev => {
      const updated = [...prev];
      updated[index] = null;
      return updated;
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.nom || !formData.email || !formData.password) {
      setMessage({ type: 'error', text: 'Tous les champs obligatoires doivent être remplis.' });
      return;
    }

    setLoading(true);
    setMessage(null);

    const data = new FormData();
    data.append('nom', formData.nom);
    data.append('email', formData.email);
    data.append('password', formData.password);
    if (photoProfil) data.append('photo_profil', photoProfil);

    empreintes.forEach((emp, i) => {
      if (emp) {
        data.append(`empreinte_${i + 1}`, emp.file);
        data.append(`doigt_${i + 1}`, emp.doigt);
      }
    });

    try {
      const res = await fetch('http://localhost:8000/auth/register', {
        method: 'POST',
        body: data
      });
const result = await res.json();

if (res.ok) {
  setMessage({ type: 'success', text: 'Inscription réussie ! Un code OTP a été envoyé à votre email.' });
  setTimeout(() => window.location.href = '/login', 2000);
} else {
  // Au lieu de result.detail, utilise JSON.stringify si c'est un objet
  const errorText = typeof result.detail === 'string'
    ? result.detail
    : JSON.stringify(result.detail);
  setMessage({ type: 'error', text: errorText || 'Erreur lors de l’inscription.' });
}

    } catch (err) {
      setMessage({ type: 'error', text: 'Erreur de connexion au serveur.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="d-flex flex-column min-vh-100">
      <Header />

      <main className="flex-grow-1 py-5">
        <div className="container">
          <div className="row justify-content-center">
            <div className="col-lg-8">
              <h1 className="display-5 fw-bold text-center text-blue-night mb-4">
                Créer votre compte
              </h1>

              {message && (
                <div className={`alert ${message.type === 'success' ? 'alert-success' : 'alert-danger'} text-center`}>
                  {message.text}
                </div>
              )}

              <form onSubmit={handleSubmit} className="bg-white p-4 p-md-5 rounded shadow">
                {/* Informations personnelles */}
                <div className="row g-3 mb-4">
                  <div className="col-md-6">
                    <label className="form-label">
                      <User size={18} className="icon-blue me-1" /> Nom complet
                    </label>
                    <input
                      type="text"
                      name="nom"
                      value={formData.nom}
                      onChange={handleInput}
                      className="form-control"
                      required
                    />
                  </div>
                  <div className="col-md-6">
                    <label className="form-label">
                      <Mail size={18} className="icon-blue me-1" /> Email
                    </label>
                    <input
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInput}
                      className="form-control"
                      required
                    />
                  </div>
                  <div className="col-md-6">
                    <label className="form-label">
                      <Lock size={18} className="icon-blue me-1" /> Mot de passe
                    </label>
                    <input
                      type="password"
                      name="password"
                      value={formData.password}
                      onChange={handleInput}
                      className="form-control"
                      required
                    />
                  </div>
                  <div className="col-md-6">
                    <label className="form-label">Photo de profil</label>
                    <div className="border border-dashed rounded p-3 text-center">
                      {photoPreview ? (
                        <img src={photoPreview} alt="Profil" className="img-fluid rounded" style={{ maxHeight: '120px' }} />
                      ) : (
                        <div>
                          <Upload size={32} className="icon-blue mb-2" />
                          <p className="text-muted small">Cliquez ou glissez ici</p>
                        </div>
                      )}
                      <input type="file" accept="image/*" onChange={handlePhoto} className="d-none" id="photo" />
                      <label htmlFor="photo" className="btn btn-outline-blue-night btn-sm mt-2">Choisir</label>
                    </div>
                  </div>
                </div>

                {/* Empreintes digitales */}
                <div className="mb-4">
                  <h5 className="fw-semibold text-blue-night d-flex align-items-center">
                    <Fingerprint size={20} className="me-2" />
                    Empreintes digitales (facultatif - max 8)
                  </h5>
                  <div className="row g-3">
                    {DOIGTS.map((doigt, i) => (
                      <div key={i} className="col-6 col-md-3">
                        <div
                          className={`border rounded p-3 text-center position-relative ${
                            dragOver === i ? 'border-blue-night bg-light' : 'border-dashed'
                          }`}
                          onDragOver={(e) => { e.preventDefault(); setDragOver(i); }}
                          onDragLeave={() => setDragOver(null)}
                          onDrop={(e) => handleDrop(e, i)}
                        >
                          {empreintes[i] ? (
                            <>
                              <img src={empreintes[i]!.preview} alt={doigt} className="img-fluid rounded mb-2" style={{ height: '80px' }} />
                              <p className="small text-muted mb-1">{doigt}</p>
                              <button
                                type="button"
                                onClick={() => removeEmpreinte(i)}
                                className="btn-close position-absolute top-0 end-0 m-2"
                                aria-label="Supprimer"
                              />
                            </>
                          ) : (
                            <>
                              <Fingerprint size={32} className="icon-blue mb-2" />
                              <p className="small text-muted">{doigt}</p>
                              <p className="text-muted xsmall">Glissez ici</p>
                            </>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="btn btn-blue-night w-100 d-flex align-items-center justify-content-center gap-2"
                >
                  {loading ? (
                    <>Envoi en cours...</>
                  ) : (
                    <>
                      S'inscrire
                    </>
                  )}
                </button>
              </form>

              <p className="text-center mt-4 text-muted">
                Déjà un compte ? <a href="/login" className="text-blue-night text-decoration-none">Se connecter</a>
              </p>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}