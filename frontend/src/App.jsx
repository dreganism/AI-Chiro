import { useEffect, useMemo, useState } from 'react';
import { api } from './api';

const initialAuth = () => ({
  access: localStorage.getItem('token') || '',
  refresh: localStorage.getItem('refreshToken') || ''
});

export default function App() {
  const [auth, setAuth] = useState(initialAuth);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [file, setFile] = useState(null);
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const isAuthenticated = Boolean(auth.access);

  const authHeaders = useMemo(
    () => ({ Authorization: `Bearer ${auth.access}` }),
    [auth.access]
  );

  const persistAuth = (access, refresh) => {
    localStorage.setItem('token', access);
    localStorage.setItem('refreshToken', refresh);
    setAuth({ access, refresh });
  };

  const clearAuth = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    setAuth({ access: '', refresh: '' });
  };

  const fetchReports = async () => {
    if (!isAuthenticated) return;
    try {
      const data = await api.listReports(auth.access);
      setReports(data);
    } catch (err) {
      console.error(err);
      if (err.message.includes('401') && auth.refresh) {
        try {
          const refreshed = await api.refresh(auth.refresh);
          persistAuth(refreshed.access_token, auth.refresh);
          const retry = await api.listReports(refreshed.access_token);
          setReports(retry);
        } catch (refreshError) {
          clearAuth();
        }
      }
    }
  };

  const handleLogin = async (evt) => {
    evt.preventDefault();
    setError('');
    try {
      const data = await api.login(email, password);
      persistAuth(data.access_token, data.refresh_token);
      setEmail('');
      setPassword('');
      fetchReports();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleRegister = async (evt) => {
    evt.preventDefault();
    setError('');
    try {
      await api.register(email, password);
      await handleLogin(evt);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError('');
    try {
      await api.upload(file, auth.access);
      setFile(null);
      setTimeout(fetchReports, 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await api.deleteReport(id, auth.access);
      fetchReports();
    } catch (err) {
      setError(err.message);
    }
  };

  useEffect(() => {
    fetchReports();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [auth.access]);

  if (!isAuthenticated) {
    return (
      <div className="container">
        <div className="card" style={{ marginTop: '5rem' }}>
          <h1 style={{ textAlign: 'center', marginBottom: '1rem' }}>SJWG AI Reporter</h1>
          {error && <p style={{ color: '#dc2626' }}>{error}</p>}
          <form className="grid" onSubmit={handleLogin}>
            <input placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <div className="grid grid-2">
              <button type="submit" style={buttonStyle('primary')}>Login</button>
              <button type="button" style={buttonStyle('secondary')} onClick={handleRegister}>
                Register
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="card" style={{ marginTop: '2rem' }}>
        <header style={{ display: 'flex', justify-content: 'space-between', alignItems: 'center' }}>
          <div>
            <h2 style={{ margin: 0 }}>SJWG AI Reporter</h2>
            <p style={{ margin: 0, color: '#64748b' }}>Upload scans, let AI craft structured summaries.</p>
          </div>
          <button style={buttonStyle('danger')} onClick={clearAuth}>
            Logout
          </button>
        </header>

        {error && <p style={{ color: '#dc2626' }}>{error}</p>}

        <section style={{ marginTop: '2rem' }}>
          <h3>Upload Document</h3>
          <div className="grid grid-2">
            <input type="file" accept=".pdf,.png,.jpg,.jpeg" onChange={(e) => setFile(e.target.files[0])} />
            <button style={buttonStyle('primary')} onClick={handleUpload} disabled={!file || loading}>
              {loading ? 'Uploading…' : 'Generate Report'}
            </button>
          </div>
        </section>

        <section style={{ marginTop: '2rem' }}>
          <div style={{ display: 'flex', justify-content: 'space-between', alignItems: 'center' }}>
            <h3>Your Reports</h3>
            <div className="grid grid-2" style={{ gap: '0.5rem' }}>
              <button style={buttonStyle('secondary')} onClick={fetchReports}>
                Refresh
              </button>
            </div>
          </div>
          {reports.length === 0 ? (
            <p style={{ color: '#94a3b8' }}>No reports yet. Upload a document to get started.</p>
          ) : (
            <div className="grid">
              {reports.map((report) => (
                <article key={report.id} className="card" style={{ boxShadow: 'none', border: '1px solid #e2e8f0' }}>
                  <header style={{ display: 'flex', justify-content: 'space-between', alignItems: 'center' }}>
                    <div>
                      <h4 style={{ margin: '0 0 0.25rem 0' }}>{report.title}</h4>
                      <small style={{ color: '#94a3b8' }}>{new Date(report.created_at).toLocaleString()}</small>
                    </div>
                    <span className={`badge ${statusClass(report.status)}`}>{report.status}</span>
                  </header>

                  {report.preview && (
                    <p style={{ marginTop: '1rem', color: '#475569' }}>{report.preview}</p>
                  )}

                  <div className="grid grid-2" style={{ marginTop: '1.5rem' }}>
                    <button style={buttonStyle('danger')} onClick={() => handleDelete(report.id)}>
                      Delete
                    </button>
                    {report.pdf_report && (
                      <a
                        style={{ ...buttonStyle('primary'), textAlign: 'center', textDecoration: 'none', lineHeight: '2.5rem' }}
                        href={report.pdf_report}
                        target="_blank"
                        rel="noreferrer"
                      >
                        Download PDF
                      </a>
                    )}
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

function buttonStyle(variant) {
  const base = {
    padding: '0.75rem 1.25rem',
    borderRadius: '0.75rem',
    border: 'none',
    fontWeight: 600,
    fontSize: '1rem',
    color: '#fff'
  };
  const variants = {
    primary: { background: 'linear-gradient(90deg, #2563eb, #7c3aed)' },
    secondary: { background: '#0f172a' },
    danger: { background: '#dc2626' }
  };
  return { ...base, ...variants[variant] };
}

function statusClass(status) {
  if (status === 'completed') return 'success';
  if (status === 'failed') return 'failed';
  return 'pending';
}
