// src/pages/Login.tsx
import { useState } from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Mail, Lock, ChevronRight, CheckCircle } from 'lucide-react';

export default function Login() {
  const [step, setStep] = useState<'email' | 'otp'>('email');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [loading, setLoading] = useState(false);

  const handleOtpChange = (index: number, value: string) => {
    if (!/^\d?$/.test(value)) return;
    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);

    if (value && index < 5) {
      const next = document.getElementById(`otp-${index + 1}`);
      next?.focus();
    }
  };

const handleSubmitEmail = async (e: React.FormEvent) => {
  e.preventDefault();
  setLoading(true);

  try {
    const response = await fetch("http://127.0.0.1:8000/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ email, password }),
    });

    const data = await response.json();

    if (response.ok) {
      localStorage.setItem("loginEmail", email); // on sauvegarde l'email
      setStep("otp");
    } else {
      alert(data.detail || "Erreur de connexion");
    }
  } catch (err) {
    alert("Impossible de contacter le serveur");
  } finally {
    setLoading(false);
  }
};

const handleSubmitOtp = async (e: React.FormEvent) => {
  e.preventDefault();
  const code = otp.join("");

  if (code.length !== 6) return;

  setLoading(true);

  try {
    const response = await fetch("http://127.0.0.1:8000/auth/verify-otp", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        email: localStorage.getItem("loginEmail") || "",
        code,
      }),
    });

    const userData = await response.json();

    if (response.ok) {
      localStorage.setItem("currentUser", JSON.stringify(userData));
      window.location.href = "/dashboard";
    } else {
      alert(userData.detail || "Code incorrect");
    }
  } catch (err) {
    alert("Erreur réseau");
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
            <div className="col-md-6 login-form">
              <h1 className="display-5 fw-bold text-center text-blue-night mb-4">
                Connexion
              </h1>

              <div className="login-card">
                {/* ÉTAPE 1 : EMAIL + MDP */}
                {step === 'email' && (
                  <form onSubmit={handleSubmitEmail}>
                    <div className="mb-3">
                      <label className="form-label fw-medium">Email</label>
                      <div className="input-group">
                        <span className="input-group-text"><Mail size={20} /></span>
                        <input
                          type="email"
                          className="form-control"
                          placeholder="votre@email.com"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          required
                        />
                      </div>
                    </div>

                    <div className="mb-4">
                      <label className="form-label fw-medium">Mot de passe</label>
                      <div className="input-group">
                        <span className="input-group-text"><Lock size={20} /></span>
                        <input
                          type="password"
                          className="form-control"
                          placeholder="••••••••"
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                          required
                        />
                      </div>
                    </div>

                    <button type="submit" className="btn btn-otp w-100 d-flex align-items-center justify-content-center gap-2">
                      Recevoir le code OTP
                      <ChevronRight size={20} />
                    </button>
                  </form>
                )}

                {/* ÉTAPE 2 : OTP */}
                {step === 'otp' && (
                  <form onSubmit={handleSubmitOtp}>
                    <div className="text-center mb-4">
                      <CheckCircle size={48} className="text-emerald mb-3" />
                      <p className="text-muted">
                        Code envoyé à <strong>{email}</strong>
                      </p>
                    </div>

                    <div className="otp-input-group">
                      {otp.map((digit, i) => (
                        <input
                          key={i}
                          id={`otp-${i}`}
                          type="text"
                          maxLength={1}
                          className="otp-input"
                          value={digit}
                          onChange={(e) => handleOtpChange(i, e.target.value)}
                          placeholder="0"
                          autoFocus={i === 0}
                        />
                      ))}
                    </div>

                    <button
                      type="submit"
                      className="btn btn-otp w-100 mt-3"
                      disabled={otp.join('').length !== 6}
                    >
                      Vérifier & Accéder
                    </button>

                    <p className="text-center text-muted mt-3">
                      Code non reçu ? <a href="#" className="text-emerald fw-medium">Renvoyer</a>
                    </p>
                  </form>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}