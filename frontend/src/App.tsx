import { useEffect, useState } from "react";
import type { FormEvent } from "react";

import { api, friendlyError } from "./services/api";
import type { DocumentRecord } from "./services/api";

import Dashboard from "./pages/Dashboard";

type Mode = "login" | "register";

function App() {
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem("documind_token")
  );

  const [documents, setDocuments] = useState<DocumentRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [mode, setMode] = useState<Mode>("login");

  async function loadDocuments(authToken: string) {
    setLoading(true);

    try {
      const data = await api.documents(authToken);
      setDocuments(data);
      setError("");
    } catch (err) {
      if ((err as { status?: number }).status === 401) {
        logout();
      } else {
        setError(friendlyError(err));
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (token) {
      void loadDocuments(token);
    }
  }, [token]);

  function handleLogin(newToken: string) {
    localStorage.setItem("documind_token", newToken);
    setToken(newToken);
  }

  function logout() {
    localStorage.removeItem("documind_token");
    setToken(null);
    setDocuments([]);
    setError("");
  }

  if (token) {
    return (
      <Dashboard
        token={token}
        documents={documents}
        loading={loading}
        error={error}
        onRefresh={() => loadDocuments(token)}
        onLogout={logout}
      />
    );
  }

  return (
    <AuthScreen
      mode={mode}
      setMode={setMode}
      onLogin={handleLogin}
    />
  );
}

type AuthScreenProps = {
  mode: Mode;
  setMode: (mode: Mode) => void;
  onLogin: (token: string) => void;
};

function AuthScreen({
  mode,
  setMode,
  onLogin,
}: AuthScreenProps) {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");

  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const isRegister = mode === "register";

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    if (isRegister && password !== confirm) {
      setError("Passwords do not match.");
      return;
    }

    setBusy(true);

    try {
      if (isRegister) {
        await api.register(fullName, email, password);

        setMode("login");
        setError("Account created. Please sign in.");
      } else {
        const result = await api.login(email, password);
        onLogin(result.access_token);
      }
    } catch (err) {
      setError(friendlyError(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="auth-shell">
      <section className="auth-brand">
        <div className="brand-mark">D</div>

        <p className="eyebrow">DOCUMIND AI</p>

        <h1>
          Intelligent
          <br />
          <span>Document Assistant</span>
        </h1>

        <p>
          Turn unstructured documents into trusted,
          actionable intelligence.
        </p>

        <div className="brand-stat">
          <strong>10 MB</strong>
          <span>secure ingestion limit</span>
        </div>
      </section>

      <section className="auth-panel">
        <p className="eyebrow">
          {isRegister
            ? "CREATE WORKSPACE ACCESS"
            : "WELCOME BACK"}
        </p>

        <h2>
          {isRegister
            ? "Create your account"
            : "Sign in to your workspace"}
        </h2>

        <p className="muted">
          {isRegister
            ? "Start processing documents with DocuMind AI."
            : "Upload, process and analyze documents with AI."}
        </p>

        <form onSubmit={submit}>
          {isRegister && (
            <label>
              Full name

              <input
                required
                minLength={3}
                value={fullName}
                onChange={(event) =>
                  setFullName(event.target.value)
                }
                placeholder="Aarav Sharma"
              />
            </label>
          )}

          <label>
            Email

            <input
              required
              type="email"
              value={email}
              onChange={(event) =>
                setEmail(event.target.value)
              }
              placeholder="you@company.com"
            />
          </label>

          <label>
            Password

            <input
              required
              minLength={8}
              type="password"
              value={password}
              onChange={(event) =>
                setPassword(event.target.value)
              }
              placeholder="Minimum 8 characters"
            />
          </label>

          {isRegister && (
            <label>
              Confirm password

              <input
                required
                type="password"
                value={confirm}
                onChange={(event) =>
                  setConfirm(event.target.value)
                }
                placeholder="Repeat your password"
              />
            </label>
          )}

          {error && (
            <div className="alert">
              {error}
            </div>
          )}

          <button
            type="submit"
            className="primary-button"
            disabled={busy}
          >
            {busy
              ? "Please wait..."
              : isRegister
              ? "Create account"
              : "Sign in"}
          </button>
        </form>

        <p className="switch-auth">
          {isRegister
            ? "Already have an account?"
            : "New to DocuMind AI?"}

          {" "}

          <button
            type="button"
            onClick={() => {
              setMode(
                isRegister
                  ? "login"
                  : "register"
              );
              setError("");
            }}
          >
            {isRegister
              ? "Sign in"
              : "Create an account"}
          </button>
        </p>
      </section>
    </main>
  );
}

export default App;