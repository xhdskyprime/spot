import React, { useState, useEffect, useRef } from 'react';
import './index.css';

const API_BASE = "http://localhost:8000";
const WS_BASE = "ws://localhost:8000";

const formatDateToDMY = (dateStr) => {
  if (!dateStr) return '';
  const parts = dateStr.split('-');
  if (parts.length === 3) {
    return `${parts[2]}/${parts[1]}/${parts[0]}`;
  }
  return dateStr;
};

const getTodayString = () => {
  const d = new Date();
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

const getInitialTargetDate = () => {
  const d = new Date();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const yyyy = d.getFullYear();
  return `${mm}-${yyyy}`;
};

const getInitialYearMonth = () => {
  const d = new Date();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const yyyy = d.getFullYear();
  return `${yyyy}-${mm}`;
};

const formatMonthToIndo = (monthStr) => {
  if (!monthStr) return '';
  const parts = monthStr.split('-');
  if (parts.length === 2) {
    const year = parts[0];
    const monthIndex = parseInt(parts[1], 10) - 1;
    const monthsIndo = [
      'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
      'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
    ];
    if (monthIndex >= 0 && monthIndex < 12) {
      return `${monthsIndo[monthIndex]} ${year}`;
    }
  }
  return monthStr;
};

const Sidebar = ({ view, setView, status, handleLogin, isRunning }) => (
  <div className="sidebar">
    <div className="sidebar-brand">
      <div className="brand-icon">⚡</div>
      <span className="brand-name">SPOT HUB</span>
    </div>
    
    <div className={`user-profile ${status.session_valid ? 'logged-in' : 'logged-out'}`}>
      <div className="avatar">
        {status.session_valid ? '👨‍💼' : '👤'}
      </div>
      <div className="user-info">
        <span className="user-name">{status.session_valid ? 'Administrator' : 'Guest'}</span>
        <div className="user-status">
          <div className="status-dot"></div>
          <span className="status-text">{status.session_valid ? 'Online' : 'Offline'}</span>
        </div>
      </div>
    </div>

    <div style={{ padding: '0 0.5rem', marginBottom: '2rem' }}>
      <button 
        className="btn btn-outline" 
        style={{ width: '100%', justifyContent: 'center', fontSize: '0.8rem', padding: '0.5rem' }}
        onClick={handleLogin}
        disabled={isRunning}
      >
        {status.session_valid ? '🔄 Refresh' : '🔑 Login'}
      </button>
    </div>

    <ul className="nav-menu">
      <li className={`nav-item ${view === 'dashboard' ? 'active' : ''}`} onClick={() => setView('dashboard')}>
        <span className="nav-icon">📊</span> <span className="nav-text">Dashboard</span>
      </li>
      <li className="nav-section">AUTOMATION</li>
      <li className={`nav-item ${view === 'jadwal' ? 'active' : ''}`} onClick={() => setView('jadwal')}>
        <span className="nav-icon">📅</span> <span className="nav-text">Jadwal Shift</span>
      </li>
      <li className={`nav-item ${view === 'api' ? 'active' : ''}`} onClick={() => setView('api')}>
        <span className="nav-icon">🚀</span> <span className="nav-text">Fast API Input</span>
      </li>
      <li className="nav-section">REPORTS</li>
      <li className={`nav-item ${view === 'download' ? 'active' : ''}`} onClick={() => setView('download')}>
        <span className="nav-icon">📥</span> <span className="nav-text">Download Bulanan</span>
      </li>
      <li className={`nav-item ${view === 'download_harian' ? 'active' : ''}`} onClick={() => setView('download_harian')}>
        <span className="nav-icon">⏳</span> <span className="nav-text">Download Harian</span>
      </li>
      <li className={`nav-item ${view === 'download_opd' ? 'active' : ''}`} onClick={() => setView('download_opd')}>
        <span className="nav-icon">🏢</span> <span className="nav-text">Laporan OPD</span>
      </li>
      <li className={`nav-item ${view === 'problem_resolver' ? 'active' : ''}`} onClick={() => setView('problem_resolver')}>
        <span className="nav-icon">🛠️</span> <span className="nav-text">Problem Resolver</span>
      </li>


      <li className={`nav-item ${view === 'filter' ? 'active' : ''}`} onClick={() => setView('filter')}>
        <span className="nav-icon">🔍</span> <span className="nav-text">Filter PDF</span>
      </li>
      <li className={`nav-item ${view === 'sinkronisasi' ? 'active' : ''}`} onClick={() => setView('sinkronisasi')}>
        <span className="nav-icon">🔄</span> <span className="nav-text">Sinkronisasi</span>
      </li>

    </ul>

    <div className="sidebar-footer">
      <li className={`nav-item ${view === 'settings' ? 'active' : ''}`} onClick={() => setView('settings')}>
        <span className="nav-icon">⚙️</span> <span className="nav-text">Settings</span>
      </li>
    </div>
  </div>
);

const LogViewer = ({ logs, logEndRef }) => (
  <div className="card log-card">
    <div className="card-header">
      <div className="card-title">Console Output</div>
      <div className="live-tag">LIVE</div>
    </div>
    <div className="log-container">
      {logs.length === 0 && <div className="log-empty">Waiting for process to start...</div>}
      {logs.map((log, i) => <div key={i} className="log-line">{log}</div>)}
      <div ref={logEndRef} />
    </div>
  </div>
);

const ProcessStatus = ({ status, error, onRetry }) => {
  if (status === 'idle') return null;

  return (
    <div className="status-overlay">
      {status === 'running' && <div className="spinner"></div>}
      {status === 'done' && <div className="status-icon" style={{fontSize: '3rem', marginBottom: '1rem'}}>✅</div>}
      {status === 'error' && <div className="status-icon" style={{fontSize: '3rem', marginBottom: '1rem'}}>❌</div>}
      
      <div className={`status-title ${status === 'done' ? 'status-success' : (status === 'error' ? 'status-error' : '')}`}>
        {status === 'running' ? 'Proses Sedang Berjalan' : (status === 'done' ? 'Proses Berhasil!' : 'Terjadi Kesalahan')}
      </div>
      
      <div className="status-msg">
        {status === 'running' ? 'Mohon tunggu sebentar, sistem sedang memproses permintaan Anda. Anda bisa memantau detail log di menu Settings.' : 
         (status === 'done' ? 'Semua tugas telah diselesaikan dengan sukses.' : 'Proses terhenti karena adanya kendala teknis.')}
      </div>

      {status === 'error' && error && (
        <div className="error-box">
          <strong>Error Detail:</strong><br/>
          {error}
        </div>
      )}

      {(status === 'done' || status === 'error') && (
        <button className="btn btn-outline" style={{marginTop: '1.5rem'}} onClick={onRetry}>
          {status === 'done' ? 'Selesai' : 'Tutup'}
        </button>
      )}
    </div>
  );
};

const JadwalEditor = ({ 
  tableData, setTableData, updateCell, handlePaste, handleNamaChange, 
  searchResults, activeSearchIdx, selectSearch, isRunning, runFromTable, 
  pullCurrentJadwal, removeRow, bulkUpdateDate, processStatus, lastError, resetStatus
}) => {
  const [targetDate, setTargetDate] = useState(getInitialTargetDate());

  return (
    <div className="view-container animate-fade-in">
      <div className="header-glass">
        <div>
          <h1>Interactive Schedule</h1>
          <p>Manage employee shifts with real-time sync to SPOT system.</p>
        </div>
        <div className="header-actions">
          <div className="bulk-date-tool" style={{display: 'flex', gap: '0.5rem'}}>
            <input 
              className="table-input" 
              style={{width: '100px'}} 
              value={targetDate} 
              onChange={e => setTargetDate(e.target.value)}
              placeholder="MM-YYYY"
            />
            <button className="btn btn-outline btn-sm" onClick={() => bulkUpdateDate(targetDate)}>Apply All</button>
          </div>
          <button className="btn btn-outline" onClick={() => setTableData([...tableData, { NIP: '', Nama: '', Bulan_Tahun: targetDate, ...Object.fromEntries([...Array(31)].map((_, i) => [i + 1, ''])) }])}>+ Add Row</button>
          <button className="btn btn-primary" onClick={runFromTable} disabled={isRunning}>
            {isRunning ? '⏳ Running...' : '🚀 Run Automation'}
          </button>
        </div>
      </div>

      {processStatus !== 'idle' ? (
        <ProcessStatus status={processStatus} error={lastError} onRetry={resetStatus} />
      ) : (
        <div className="schedule-board animate-fade-in">
          <div className="board-wrapper">
            <div className="board-header">
              <div className="board-cell sticky-ident s-1">Actions</div>
              <div className="board-cell sticky-ident s-2">NIP</div>
              <div className="board-cell sticky-ident s-3">Nama Pegawai</div>
              <div className="board-cell sticky-ident s-4">Month</div>
              {[...Array(31)].map((_, i) => (
                <div key={i} className="board-cell">{i + 1}</div>
              ))}
            </div>
            
            {tableData.map((row, idx) => (
              <div className="board-row" key={idx}>
                <div className="board-cell sticky-ident s-1">
                  <div style={{display: 'flex', gap: '8px'}}>
                    <button className="btn-icon" onClick={() => pullCurrentJadwal(idx)} title="Pull Current">🔄</button>
                    <button className="btn-icon danger" onClick={() => removeRow(idx)} title="Delete">🗑️</button>
                  </div>
                </div>
                <div className="board-cell sticky-ident s-2">
                  <input className="board-input" value={row.NIP} onChange={e => updateCell(idx, 'NIP', e.target.value)} placeholder="NIP" />
                </div>
                <div className="board-cell sticky-ident s-3" style={{ zIndex: activeSearchIdx === idx ? 100 : undefined }}>
                  <div className="grid-search-container">
                    <input className="board-input nama-input" value={row.Nama} onChange={e => handleNamaChange(idx, e.target.value)} placeholder="Cari Nama..." />
                    {activeSearchIdx === idx && searchResults.length > 0 && (
                      <div className="search-dropdown">
                        {searchResults.map((res, i) => (
                          <div key={i} onClick={() => selectSearch(idx, res)} className="dropdown-item">
                            <span className="res-nama">{res.Nama}</span>
                            <span className="res-nip">{res.NIP}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
                <div className="board-cell sticky-ident s-4">
                  <input className="board-input" value={row.Bulan_Tahun} onChange={e => updateCell(idx, 'Bulan_Tahun', e.target.value)} />
                </div>
                {[...Array(31)].map((_, i) => (
                  <div key={i} className="board-cell">
                    <input 
                      className={`board-input shift-${row[i + 1] || ''}`} 
                      maxLength="1" 
                      value={row[i + 1] || ''} 
                      onPaste={e => handlePaste(e, idx, (i + 1).toString())} 
                      onChange={e => updateCell(idx, i + 1, e.target.value.toUpperCase())} 
                    />
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

function App() {
  const [view, setView] = useState('dashboard');
  const [status, setStatus] = useState({ auth_exists: false, session_valid: false, status_label: 'NONE', scripts: [], db_exists: false });
  const [logs, setLogs] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [processStatus, setProcessStatus] = useState('idle'); // idle, running, done, error
  const [lastError, setLastError] = useState("");
  const logEndRef = useRef(null);

  const resetStatus = () => setProcessStatus('idle');
  
  const [searchResults, setSearchResults] = useState([]);
  const [activeSearchIdx, setActiveSearchIdx] = useState(null);
  const [tableData, setTableData] = useState([{ NIP: '', Nama: '', Bulan_Tahun: getInitialTargetDate(), ...Object.fromEntries([...Array(31)].map((_, i) => [i + 1, ''])) }]);
  const [pdfFilterMode, setPdfFilterMode] = useState('both');

  useEffect(() => { fetchStatus(); }, [view]);
  useEffect(() => { if (logEndRef.current) logEndRef.current.scrollIntoView({ behavior: 'smooth' }); }, [logs]);

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/status`);
      const data = await res.json();
      setStatus(data);
    } catch (e) { console.error("Status check failed", e); }
  };

  const syncPegawaiDB = async (month = getInitialTargetDate()) => {
    setIsRunning(true);
    setLogs([`🔄 Syncing employee database for unit (${month})...`]);
    try {
      const res = await fetch(`${API_BASE}/api/sync_pegawai?month=${month}`);
      const data = await res.json();
      setLogs(prev => [...prev, `✅ Database synced! Found ${data.length} employees.`]);
      fetchStatus();
    } catch (e) { setLogs(prev => [...prev, `❌ Sync failed: ${e.message}`]); }
    setIsRunning(false);
  };

  const bulkUpdateDate = (date) => {
    const newData = tableData.map(row => ({ ...row, Bulan_Tahun: date }));
    setTableData(newData);
  };

  const removeRow = (idx) => {
    if (tableData.length === 1) {
      setTableData([{ NIP: '', Nama: '', Bulan_Tahun: tableData[0].Bulan_Tahun, ...Object.fromEntries([...Array(31)].map((_, i) => [i + 1, ''])) }]);
    } else {
      setTableData(tableData.filter((_, i) => i !== idx));
    }
  };

  const handleDBUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    setLogs([`📤 Uploading Master Pegawai (${file.name})...`]);
    try {
      const res = await fetch(`${API_BASE}/api/upload_pegawai_db`, { method: 'POST', body: formData });
      const data = await res.json();
      if (data.status === 'success') { setLogs(prev => [...prev, `✅ Database updated! ${data.count} employees saved.`]); fetchStatus(); }
      else { setLogs(prev => [...prev, `❌ Failed: ${data.message}`]); }
    } catch (e) { setLogs(prev => [...prev, `❌ Error: ${e.message}`]); }
  };

  const handleNamaChange = async (idx, val) => {
    updateCell(idx, 'Nama', val);
    if (!val || val.trim().length === 0) { setSearchResults([]); return; }
    try {
      const res = await fetch(`${API_BASE}/api/search_pegawai?q=${encodeURIComponent(val)}`);
      const data = await res.json();
      setSearchResults(data);
      setActiveSearchIdx(idx);
    } catch (e) { console.error("Search failed", e); }
  };

  const selectSearch = (idx, res) => {
    const newData = [...tableData];
    newData[idx].NIP = res.NIP;
    newData[idx].Nama = res.Nama;
    setTableData(newData);
    setSearchResults([]);
    setActiveSearchIdx(null);
  };

  const updateCell = (index, key, value) => {
    const newData = [...tableData];
    newData[index][key] = value;
    setTableData(newData);
  };

  const handlePaste = (e, rowIdx, colKey) => {
    e.preventDefault();
    const paste = e.clipboardData.getData('text');
    const rows = paste.split(/\r?\n/).filter(r => r.trim() !== '');
    const newData = [...tableData];
    rows.forEach((rowText, i) => {
      const targetRowIdx = rowIdx + i;
      if (!newData[targetRowIdx]) {
        newData[targetRowIdx] = { NIP: '', Nama: '', Bulan_Tahun: newData[0].Bulan_Tahun, ...Object.fromEntries([...Array(31)].map((_, j) => [j + 1, ''])) };
      }
      const cells = rowText.split('\t');
      const startColIdx = colKey === 'NIP' ? 0 : (colKey === 'Nama' ? 1 : (colKey === 'Bulan_Tahun' ? 2 : parseInt(colKey) + 2));
      cells.forEach((cellVal, j) => {
        const currentColIdx = startColIdx + j;
        if (currentColIdx === 0) newData[targetRowIdx].NIP = cellVal || '';
        else if (currentColIdx === 1) newData[targetRowIdx].Nama = cellVal || '';
        else if (currentColIdx === 2) newData[targetRowIdx].Bulan_Tahun = cellVal || '';
        else {
          const day = currentColIdx - 2;
          if (day >= 1 && day <= 31) newData[targetRowIdx][day] = (cellVal || '').toUpperCase();
        }
      });
    });
    setTableData(newData);
  };

  const runScript = (scriptName, args = "") => {
    setIsRunning(true);
    setProcessStatus('running');
    setLastError("");
    setLogs([`🚀 Starting ${scriptName}...`]);
    const wsUrl = new URL(`${WS_BASE}/ws/run/${scriptName}`);
    if (args) wsUrl.searchParams.append("args", args);
    const ws = new WebSocket(wsUrl.toString());
    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === 'log') setLogs(prev => [...prev, msg.data]);
      else if (msg.type === 'done') { 
        setIsRunning(false); 
        setProcessStatus('done');
        fetchStatus(); 
      }
      else if (msg.type === 'error') { 
        setLogs(prev => [...prev, `❌ Error: ${msg.data}`]); 
        setProcessStatus('error');
        setLastError(msg.data);
        setIsRunning(false); 
      }
    };
    ws.onclose = () => {
      if (processStatus === 'running') {
        setIsRunning(false);
        setProcessStatus('error');
        setLastError("Koneksi terputus tiba-tiba.");
      }
    };
  };


  const runFromTable = async () => {
    setIsRunning(true);
    setLogs([`🚀 Saving data and starting automation...`]);
    try {
      const res = await fetch(`${API_BASE}/api/run/jadwal_json`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(tableData),
      });
      const data = await res.json();
      runScript('otomatisasi_jadwal.py', `--file ${data.filename}`);
    } catch (e) { setLogs(prev => [...prev, `❌ Failed to start: ${e.message}`]); setIsRunning(false); }
  };

  const pullCurrentJadwal = async (idx) => {
    const row = tableData[idx];
    if (!row.NIP || !row.Bulan_Tahun) { alert("Isi NIP dan Bulan dulu!"); return; }
    setLogs(prev => [...prev, `🔍 Pulling schedule for ${row.Nama}...`]);
    try {
      const res = await fetch(`${API_BASE}/api/get_current_jadwal?nip=${row.NIP}&month=${row.Bulan_Tahun}`);
      const shifts = await res.json();
      const newData = [...tableData];
      for (let day = 1; day <= 31; day++) { newData[idx][day] = shifts[day] || ''; }
      setTableData(newData);
      setLogs(prev => [...prev, `✅ Schedule pulled!`]);
    } catch (e) { setLogs(prev => [...prev, `❌ Pull failed: ${e.message}`]); }
  };

  return (
    <div className="app-container">
      <Sidebar 
        view={view} 
        setView={setView} 
        status={status} 
        handleLogin={() => runScript('otomatisasi_piket.py', '--login-only')}
        isRunning={isRunning}
      />
      <div className="main-content">
        {view === 'dashboard' && (
          <div className="view-container animate-fade-in">
            <div className="header-glass">
              <div>
                <h1>Welcome to SPOT Hub</h1>
                <p>Your centralized dashboard for administrative automation.</p>
              </div>
            </div>
            
            <div className="stat-grid">
              <div className="stat-card premium">
                <div className="stat-icon">🔑</div>
                <div className="stat-info">
                  <div className="stat-label">System Access</div>
                  <div className={`stat-value ${status.session_valid ? 'success' : 'danger'}`}>
                    {status.status_label}
                  </div>
                </div>
              </div>
              <div className="stat-card premium">
                <div className="stat-icon">👥</div>
                <div className="stat-info">
                  <div className="stat-label">Employee DB</div>
                  <div className="stat-value">{status.db_exists ? 'READY' : 'EMPTY'}</div>
                </div>
              </div>
              <div className="stat-card premium">
                <div className="stat-icon">🛠️</div>
                <div className="stat-info">
                  <div className="stat-label">Active Tools</div>
                  <div className="stat-value">{status.scripts.length} Units</div>
                </div>
              </div>
            </div>

            <div className="grid-2-col">
              <div className="card glass-card" style={{padding: '2rem'}}>
                <div className="card-header"><div className="card-title">Quick Start</div></div>
                <div className="action-list">
                  <div className="action-item" onClick={() => setView('jadwal')}>
                    <div className="action-icon">📅</div>
                    <div className="action-content">
                      <div className="action-title">Manage Schedules</div>
                      <div className="action-desc">Update employee shift patterns.</div>
                    </div>
                  </div>
                  <div className="action-item" onClick={() => setView('download')}>
                    <div className="action-icon">📥</div>
                    <div className="action-content">
                      <div className="action-title">Batch Download</div>
                      <div className="action-desc">Download reports for multiple employees.</div>
                    </div>
                  </div>
                  <div className="action-item" onClick={() => setView('download_opd')}>
                    <div className="action-icon">🏢</div>
                    <div className="action-content">
                      <div className="action-title">Laporan OPD</div>
                      <div className="action-desc">Download monthly reports for the whole unit.</div>
                    </div>
                  </div>
                </div>

              </div>
              
              <div className="card glass-card" style={{padding: '2rem'}}>
                <div className="card-header"><div className="card-title">Templates</div></div>
                <div className="template-grid">
                  <a href={`${API_BASE}/api/download_sample/jadwal`} className="template-card">
                    <span className="icon">📄</span>
                    <span>Jadwal Excel</span>
                  </a>
                  <a href={`${API_BASE}/api/download_sample/bulanan`} className="template-card">
                    <span className="icon">📋</span>
                    <span>Report List</span>
                  </a>
                  <a href={`${API_BASE}/api/download_sample/harian`} className="template-card">
                    <span className="icon">🗓️</span>
                    <span>Daily List</span>
                  </a>
                  <a href={`${API_BASE}/api/download_sample/sinkronisasi`} className="template-card">
                    <span className="icon">🔄</span>
                    <span>Sync List</span>
                  </a>

                </div>
              </div>
            </div>
          </div>
        )}

        {view === 'jadwal' && <JadwalEditor 
          tableData={tableData} setTableData={setTableData} updateCell={updateCell} 
          handlePaste={handlePaste} handleNamaChange={handleNamaChange} 
          searchResults={searchResults} activeSearchIdx={activeSearchIdx} 
          selectSearch={selectSearch} isRunning={isRunning} 
          runFromTable={runFromTable} pullCurrentJadwal={pullCurrentJadwal} removeRow={removeRow}
          bulkUpdateDate={bulkUpdateDate} 
          processStatus={processStatus} lastError={lastError} resetStatus={resetStatus}
        />}

        {view === 'api' && (
          <div className="view-container animate-fade-in">
            <div className="header-glass">
              <div>
                <h1>Fast API Input</h1>
                <p>High-speed schedule injection using internal APIs.</p>
              </div>
            </div>
            <div className="card glass-card" style={{padding: '2rem'}}>
              <div className="card-header"><div className="card-title">Setup</div></div>
              <p style={{marginBottom: '1.5rem', color: 'var(--text-secondary)'}}>Gunakan modul ini jika Anda sudah memiliki file Excel yang sesuai dengan format sistem.</p>
              <div className="button-group" style={{display: 'flex', gap: '1rem'}}>
                <button className="btn btn-primary" onClick={() => runScript('otomatisasi_api.py')} disabled={isRunning}>
                  {isRunning ? '⏳ Running...' : '🚀 Start Injection'}
                </button>
                <a href={`${API_BASE}/api/download_sample/jadwal`} className="btn btn-outline" style={{textDecoration: 'none'}}>📥 Get Format</a>
              </div>
            </div>
            <ProcessStatus status={processStatus} error={lastError} onRetry={resetStatus} />
          </div>
        )}

        {view === 'download' && (
          <div className="view-container animate-fade-in">
            <div className="header-glass">
              <div>
                <h1>Monthly Report Downloader</h1>
                <p>Batch download PDF/Excel reports for multiple employees at once.</p>
              </div>
            </div>
            <div className="card glass-card" style={{padding: '2rem'}}>
              <div className="card-header"><div className="card-title">Batch Configuration</div></div>
              <p style={{marginBottom: '1.5rem', color: 'var(--text-secondary)'}}>
                Sistem akan membaca daftar antrean dari file <strong>data_download_laporan.xlsx</strong>. 
                Pastikan file tersebut sudah diperbarui sebelum menjalankan download.
              </p>
              <div className="upload-actions" style={{display: 'flex', gap: '1rem', alignItems: 'center'}}>
                <button className="btn btn-primary" style={{padding: '1rem 2rem'}} onClick={() => runScript('batch_download_laporan.py')} disabled={isRunning}>
                  {isRunning ? '⏳ Processing...' : '🚀 Start Batch Download'}
                </button>
                <div style={{display: 'flex', gap: '0.5rem'}}>
                  <a href={`${API_BASE}/api/download_sample/bulanan`} className="btn btn-outline" style={{textDecoration: 'none'}}>📥 Download Template</a>
                  <label className="btn btn-outline" style={{cursor: 'pointer'}}>
                    📁 Upload Excel Baru
                    <input type="file" hidden accept=".xlsx" onChange={async (e) => {
                      const file = e.target.files[0];
                      if (!file) return;
                      const formData = new FormData();
                      formData.append('file', file);
                      setLogs([`📤 Uploading list report...`]);
                      try {
                        const res = await fetch(`${API_BASE}/api/upload_monthly_list`, { method: 'POST', body: formData });
                        const data = await res.json();
                        setLogs(prev => [...prev, `✅ Berhasil upload: ${data.filename}`]);
                        setLogs(prev => [...prev, `⚠️ Berkas ini tersimpan sebagai data_download_laporan.xlsx`]);
                      } catch (err) { setLogs(prev => [...prev, `❌ Gagal: ${err.message}`]); }
                    }} />
                  </label>
                </div>
              </div>
            </div>
            <ProcessStatus status={processStatus} error={lastError} onRetry={resetStatus} />
          </div>
        )}

        {view === 'download_harian' && (
          <div className="view-container animate-fade-in">
            <div className="header-glass">
              <div>
                <h1>Daily Report Downloader</h1>
                <p>Retrieve daily attendance records for specific date ranges.</p>
              </div>
            </div>
            <div className="card glass-card" style={{padding: '2rem'}}>
              <div className="card-header"><div className="card-title">Configuration</div></div>
              
              <div className="config-grid">
                <div className="input-field">
                  <label>Tanggal Mulai</label>
                  <input type="date" id="start_date" className="table-input" defaultValue={getTodayString()} />
                </div>
                <div className="input-field">
                  <label>Tanggal Selesai</label>
                  <input type="date" id="end_date" className="table-input" defaultValue={getTodayString()} />
                </div>
                <div className="input-field">
                  <label>ID SKPD Primary</label>
                  <input id="skpd1" className="table-input" defaultValue="4.02.01.01" />
                </div>
                <div className="input-field">
                  <label>ID SKPD Secondary</label>
                  <input id="skpd2" className="table-input" defaultValue="4.02.01.01.0010" />
                </div>
              </div>

              <div className="button-group" style={{marginTop: '1.5rem'}}>
                <button className="btn btn-primary" onClick={() => {
                  const s = formatDateToDMY(document.getElementById('start_date').value);
                  const e = formatDateToDMY(document.getElementById('end_date').value);
                  const s1 = document.getElementById('skpd1').value;
                  const s2 = document.getElementById('skpd2').value;
                  runScript('batch_download_harian.py', `${s} ${e} ${s1} ${s2}`);
                }} disabled={isRunning}>
                  🚀 Run Range Download
                </button>
              </div>

              <div className="divider">OR</div>

              <div className="upload-actions" style={{display: 'flex', gap: '1rem', alignItems: 'center'}}>
                <label className="btn btn-outline" style={{cursor: 'pointer'}}>
                  📁 Use Excel List
                  <input type="file" hidden accept=".xlsx" onChange={async (e) => {
                    const file = e.target.files[0];
                    if (!file) return;
                    const formData = new FormData();
                    formData.append('file', file);
                    setLogs([`📤 Uploading Daily Excel...`]);
                    try {
                      const res = await fetch(`${API_BASE}/api/upload_daily_list`, { method: 'POST', body: formData });
                      await res.json();
                      setLogs(prev => [...prev, `✅ Berhasil upload: data_download_harian.xlsx`]);
                    } catch (err) { setLogs(prev => [...prev, `❌ Gagal: ${err.message}`]); }
                  }} />
                </label>
                <button className="btn btn-primary" onClick={() => runScript('batch_download_harian.py')} disabled={isRunning}>
                  🚀 Start Excel Download
                </button>
                <a href={`${API_BASE}/api/download_sample/harian`} className="btn btn-outline" style={{textDecoration: 'none'}}>Template</a>
              </div>
            </div>
            <ProcessStatus status={processStatus} error={lastError} onRetry={resetStatus} />
          </div>
        )}

        {view === 'download_opd' && (
          <div className="view-container animate-fade-in">
            <div className="header-glass">
              <div>
                <h1>Laporan Kehadiran OPD (Excel)</h1>
                <p>Download monthly attendance reports for the entire OPD or specific employees.</p>
              </div>
            </div>
            <div className="card glass-card" style={{padding: '2rem'}}>
              <div className="card-header"><div className="card-title">Configuration</div></div>
              
              <div className="config-grid">
                <div className="input-field">
                  <label>Periode</label>
                  <input type="month" id="opd_periode" className="table-input" defaultValue={getInitialYearMonth()} />
                </div>
                <div className="input-field" style={{position: 'relative'}}>
                  <label>Cari Pegawai (Opsional)</label>
                  <input 
                    id="opd_nip_search" 
                    className="table-input" 
                    placeholder="Ketik nama untuk filter NIP..." 
                    onChange={async (e) => {
                      const val = e.target.value;
                      if (!val) { setSearchResults([]); return; }
                      const res = await fetch(`${API_BASE}/api/search_pegawai?q=${encodeURIComponent(val)}`);
                      const data = await res.json();
                      setSearchResults(data);
                      setActiveSearchIdx('opd');
                    }}
                  />
                  {activeSearchIdx === 'opd' && searchResults.length > 0 && (
                    <div className="search-dropdown" style={{top: '100%', left: 0, width: '100%', zIndex: 100}}>
                      {searchResults.map((res, i) => (
                        <div key={i} onClick={() => {
                          document.getElementById('opd_nip').value = res.NIP;
                          document.getElementById('opd_nip_search').value = res.Nama;
                          setSearchResults([]);
                          setActiveSearchIdx(null);
                        }} className="dropdown-item">
                          <span className="res-nama">{res.Nama}</span>
                          <span className="res-nip">{res.NIP}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                <div className="input-field">
                  <label>NIP Terpilih</label>
                  <input id="opd_nip" className="table-input" placeholder="Kosongkan untuk ALL" />
                </div>
                <div className="input-field">
                  <label>ID SKPD 1</label>
                  <input id="opd_skpd1" className="table-input" defaultValue="4.02.01.01" />
                </div>
                <div className="input-field">
                  <label>ID SKPD 2</label>
                  <input id="opd_skpd2" className="table-input" defaultValue="4.02.01.01.0010" />
                </div>
              </div>

              <div className="button-group" style={{marginTop: '1.5rem'}}>
                <button className="btn btn-primary" onClick={() => {
                  const p = formatMonthToIndo(document.getElementById('opd_periode').value);
                  const n = document.getElementById('opd_nip').value;
                  const s1 = document.getElementById('opd_skpd1').value;
                  const s2 = document.getElementById('opd_skpd2').value;
                  runScript('batch_download_opd.py', `"${p}" ${s1} ${s2} ${n}`);
                }} disabled={isRunning}>
                  🚀 Download Laporan OPD (.xls)
                </button>
              </div>

              <div className="divider">ANALYSIS TOOLS</div>
              
              <div style={{display: 'flex', gap: '1rem', alignItems: 'center'}}>
                <button className="btn btn-outline" onClick={() => runScript('filter_opd_masalah.py')} disabled={isRunning}>
                  🔍 Analisa Masalah (&gt; 5 Jam)
                </button>
                <a href={`${API_BASE}/api/download_result/opd_masalah`} className="btn btn-outline" style={{textDecoration: 'none'}}>📥 Download Hasil Analisa</a>
              </div>
            </div>
            <ProcessStatus status={processStatus} error={lastError} onRetry={resetStatus} />
          </div>
        )}

        {view === 'problem_resolver' && (
          <ProblemResolver 
            API_BASE={API_BASE} 
            isRunning={isRunning} 
            runScript={runScript}
            processStatus={processStatus}
            lastError={lastError}
            resetStatus={resetStatus}
          />
        )}

        {view === 'filter' && (


          <div className="view-container animate-fade-in">
            <div className="header-glass">
              <div>
                <h1>Data Filtering Tools</h1>
                <p>Extract specific logic-based attendance from exported files.</p>
              </div>
            </div>
            
            <div className="grid-2-col">
              <div className="card glass-card" style={{padding: '2rem'}}>
                <div className="card-header"><div className="card-title">Filter Masalah Harian</div></div>
                <p style={{marginBottom: '1.5rem', color: 'var(--text-secondary)'}}>Saring Laporan Harian untuk mencari: 1) TMTB, 2) Datang Kosong (Ket Kosong), 3) Pulang Kosong (Ket Kosong). Pastikan file .xls ada di folder "laporan harian".</p>
                <div className="button-group" style={{display: 'flex', gap: '1rem'}}>
                  <button className="btn btn-primary" onClick={() => runScript('filter_harian_masalah.py')} disabled={isRunning}>
                    🔍 Cari Masalah
                  </button>
                  <a href={`${API_BASE}/api/download_result/harian_masalah`} className="btn btn-outline" style={{textDecoration: 'none'}}>📥 Download Hasil</a>
                </div>
              </div>

              <div className="card glass-card" style={{padding: '2rem'}}>
                <div className="card-header"><div className="card-title">Filter PDF Bulanan</div></div>
                <p style={{marginBottom: '1rem', color: 'var(--text-secondary)'}}>Pilih kriteria penyaringan data dari berkas PDF di folder "laporan bulanan":</p>
                
                <div className="filter-options" style={{display: 'flex', gap: '0.5rem', marginBottom: '1.5rem'}}>
                  <button 
                    className={`btn ${pdfFilterMode === 'tm' ? 'btn-primary' : 'btn-outline'} btn-sm`}
                    style={{flex: 1, justifyContent: 'center'}}
                    onClick={() => setPdfFilterMode('tm')}
                  >TM Saja</button>
                  <button 
                    className={`btn ${pdfFilterMode === 'psw' ? 'btn-primary' : 'btn-outline'} btn-sm`}
                    style={{flex: 1, justifyContent: 'center'}}
                    onClick={() => setPdfFilterMode('psw')}
                  >PSW Saja</button>
                  <button 
                    className={`btn ${pdfFilterMode === 'both' ? 'btn-primary' : 'btn-outline'} btn-sm`}
                    style={{flex: 1, justifyContent: 'center'}}
                    onClick={() => setPdfFilterMode('both')}
                  >TM & PSW</button>
                </div>

                <div className="button-group" style={{display: 'flex', gap: '1rem'}}>
                  <button className="btn btn-primary" onClick={() => runScript('filter_absen.py', `--mode ${pdfFilterMode}`)} disabled={isRunning}>
                    🚀 Ekstrak PDF
                  </button>
                  <a href={`${API_BASE}/api/download_result/pdf_filter`} className="btn btn-outline" style={{textDecoration: 'none'}}>📥 Hasil</a>
                </div>
              </div>
            </div>
            
            <ProcessStatus status={processStatus} error={lastError} onRetry={resetStatus} />
          </div>
        )}

        {view === 'sinkronisasi' && (
          <div className="view-container animate-fade-in">
            <div className="header-glass">
              <div>
                <h1>Data Synchronization</h1>
                <p>Force sync attendance data from machine/old DB to SPOT system.</p>
              </div>
            </div>
            <div className="card glass-card" style={{padding: '2rem'}}>
              <div className="card-header"><div className="card-title">Configuration</div></div>
              
              <div className="config-grid">
                <div className="input-field">
                  <label>Tanggal Mulai</label>
                  <input type="date" id="sync_start" className="table-input" defaultValue={getTodayString()} />
                </div>
                <div className="input-field">
                  <label>Tanggal Selesai</label>
                  <input type="date" id="sync_end" className="table-input" defaultValue={getTodayString()} />
                </div>
                <div className="input-field" style={{position: 'relative'}}>
                  <label>Cari Pegawai (Autofill)</label>
                  <input 
                    id="sync_nip_search" 
                    className="table-input" 
                    placeholder="Ketik nama atau NIP..." 
                    onChange={async (e) => {
                      const val = e.target.value;
                      if (!val) { setSearchResults([]); return; }
                      const res = await fetch(`${API_BASE}/api/search_pegawai?q=${encodeURIComponent(val)}`);
                      const data = await res.json();
                      setSearchResults(data);
                      setActiveSearchIdx('sync');
                    }}
                  />
                  {activeSearchIdx === 'sync' && searchResults.length > 0 && (
                    <div className="search-dropdown" style={{top: '100%', left: 0, width: '100%', zIndex: 100}}>
                      {searchResults.map((res, i) => (
                        <div key={i} onClick={() => {
                          document.getElementById('sync_nip').value = res.NIP;
                          document.getElementById('sync_nip_search').value = res.Nama;
                          setSearchResults([]);
                          setActiveSearchIdx(null);
                        }} className="dropdown-item">
                          <span className="res-nama">{res.Nama}</span>
                          <span className="res-nip">{res.NIP}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                <div className="input-field">
                  <label>NIP Terpilih</label>
                  <input id="sync_nip" className="table-input" readOnly placeholder="NIP otomatis terisi" />
                </div>

                <div className="input-field">
                  <label>Kunkom ID</label>
                  <input id="sync_kunkom" className="table-input" defaultValue="11" />
                </div>
                <div className="input-field">
                  <label>Kununit ID</label>
                  <input id="sync_kununit" className="table-input" defaultValue="83" />
                </div>
              </div>

              <div className="button-group" style={{marginTop: '1.5rem', display: 'flex', gap: '1rem'}}>
                <button className="btn btn-primary" onClick={() => {
                  const s = formatDateToDMY(document.getElementById('sync_start').value);
                  const e = formatDateToDMY(document.getElementById('sync_end').value);
                  const nip = document.getElementById('sync_nip').value;
                  const kunkom = document.getElementById('sync_kunkom').value;
                  const kununit = document.getElementById('sync_kununit').value;
                  let args = `${s} ${e} --kunkom ${kunkom} --kununit ${kununit}`;
                  if (nip) args += ` --nip ${nip}`;
                  runScript('sinkronisasi_api.py', args);
                }} disabled={isRunning}>
                  🚀 Run Synchronization
                </button>
              </div>

              <div className="divider">OR USE EXCEL LIST</div>

              <div className="upload-actions" style={{display: 'flex', gap: '1rem', alignItems: 'center'}}>
                <label className="btn btn-outline" style={{cursor: 'pointer'}}>
                  📁 Upload Sync List
                  <input type="file" hidden accept=".xlsx" onChange={async (e) => {
                    const file = e.target.files[0];
                    if (!file) return;
                    const formData = new FormData();
                    formData.append('file', file);
                    setLogs([`📤 Uploading Sync list...`]);
                    try {
                      const res = await fetch(`${API_BASE}/api/upload_sync_list`, { method: 'POST', body: formData });
                      await res.json();
                      setLogs(prev => [...prev, `✅ Berhasil upload: data_sinkronisasi.xlsx`]);
                    } catch (err) { setLogs(prev => [...prev, `❌ Gagal: ${err.message}`]); }
                  }} />
                </label>
                <button className="btn btn-primary" onClick={() => {
                  const s = formatDateToDMY(document.getElementById('sync_start').value);
                  const e = formatDateToDMY(document.getElementById('sync_end').value);
                  const kunkom = document.getElementById('sync_kunkom').value;
                  const kununit = document.getElementById('sync_kununit').value;
                  runScript('sinkronisasi_api.py', `${s} ${e} --kunkom ${kunkom} --kununit ${kununit}`);
                }} disabled={isRunning}>
                  🚀 Start Batch Sync
                </button>

                <button className="btn btn-outline" onClick={() => {
                  const s = formatDateToDMY(document.getElementById('sync_start').value);
                  const e = formatDateToDMY(document.getElementById('sync_end').value);
                  const kunkom = document.getElementById('sync_kunkom').value;
                  const kununit = document.getElementById('sync_kununit').value;
                  runScript('sinkronisasi_api.py', `${s} ${e} --kunkom ${kunkom} --kununit ${kununit} --db`);
                }} disabled={isRunning}>
                  👥 Run for All (From DB)
                </button>

                <a href={`${API_BASE}/api/download_sample/sinkronisasi`} className="btn btn-outline" style={{textDecoration: 'none'}}>Template</a>

              </div>
            </div>
            <ProcessStatus status={processStatus} error={lastError} onRetry={resetStatus} />
          </div>
        )}

        {view === 'settings' && (

          <div className="view-container animate-fade-in">
            <div className="header-glass">
              <div>
                <h1>System Settings</h1>
                <p>Manage authentication and employee reference data.</p>
              </div>
            </div>
            
            <div className="grid-2-col">
              <div className="card glass-card" style={{padding: '2rem'}}>
                <div className="card-header"><div className="card-title">Auth & Sessions</div></div>
                <p style={{marginBottom: '1.5rem', color: 'var(--text-secondary)'}}>Login ke sistem SPOT untuk memperbarui token akses.</p>
                <button className="btn btn-outline" style={{width: '100%', justifyContent: 'center'}} onClick={() => runScript('otomatisasi_piket.py', '--login-only')} disabled={isRunning}>
                  🔑 Renew Login Session
                </button>
              </div>

              <div className="card glass-card" style={{padding: '2rem'}}>
                <div className="card-header"><div className="card-title">Master Pegawai</div></div>
                <p style={{marginBottom: '1.5rem', color: 'var(--text-secondary)'}}>Sync database dari SPOT atau upload file Excel Master.</p>
                <div className="button-group-vertical" style={{display: 'flex', flexDirection: 'column', gap: '0.75rem'}}>
                  <button className="btn btn-outline" onClick={() => syncPegawaiDB(tableData[0].Bulan_Tahun)} disabled={isRunning}>
                    🔄 Sync from Live System
                  </button>
                  <label className="btn btn-primary" style={{textAlign: 'center', justifyContent: 'center'}}>
                    📁 Upload Excel DB
                    <input type="file" hidden accept=".xlsx" onChange={handleDBUpload} />
                  </label>
                </div>
                {status.db_exists && <div className="status-indicator-mini success">● Database Ready</div>}
              </div>
            </div>
            <LogViewer logs={logs} logEndRef={logEndRef} />
          </div>
        )}
      </div>
    </div>
  );
}

const ProblemResolver = ({ API_BASE, isRunning, runScript, processStatus, lastError, resetStatus }) => {
  const [activeTab, setActiveTab] = React.useState("daily"); // "daily" or "opd"
  const [problems, setProblems] = React.useState([]);
  const [opdProblems, setOpdProblems] = React.useState([]);
  const [selectedIds, setSelectedIds] = React.useState([]);
  const [filter, setFilter] = React.useState("");
  const [loading, setLoading] = React.useState(false);
  const [criteria, setCriteria] = React.useState("ALL"); // "TM", "PSW", "ALL"
  const [masalahFilter, setMasalahFilter] = React.useState("ALL");

  // State untuk Panel Resolusi Interaktif
  const [selectedProblem, setSelectedProblem] = React.useState(null);
  
  const [rawLogs, setRawLogs] = React.useState([]);
  const [rawLogsLoading, setRawLogsLoading] = React.useState(false);
  const [rawLogsError, setRawLogsError] = React.useState("");

  const [shiftInfo, setShiftInfo] = React.useState(null);
  const [shiftLoading, setShiftLoading] = React.useState(false);
  const [shiftError, setShiftError] = React.useState("");

  const [shiftPosting, setShiftPosting] = React.useState(false);
  const [shiftPostMessage, setShiftPostMessage] = React.useState("");
  const [shiftPostError, setShiftPostError] = React.useState("");

  const [kedinasanKeterangan, setKedinasanKeterangan] = React.useState("");
  const [kedinasanPosting, setKedinasanPosting] = React.useState(false);
  const [kedinasanMessage, setKedinasanMessage] = React.useState("");
  const [kedinasanError, setKedinasanError] = React.useState("");

  const [syncLoading, setSyncLoading] = React.useState(false);
  const [syncStatus, setSyncStatus] = React.useState("idle"); // "idle", "success", "error"

  const [dailyReport, setDailyReport] = React.useState(null);
  const [dailyReportLoading, setDailyReportLoading] = React.useState(false);
  const [dailyReportError, setDailyReportError] = React.useState("");

  const [resolutionStatus, setResolutionStatus] = React.useState({});

  const [monthlyResolving, setMonthlyResolving] = React.useState(false);
  const [monthlyResolvingResults, setMonthlyResolvingResults] = React.useState([]);
  const [monthlyResolvingError, setMonthlyResolvingError] = React.useState("");
  const [monthlyResolvingSuccess, setMonthlyResolvingSuccess] = React.useState(false);

  const [verificationData, setVerificationData] = React.useState(null);
  const [verificationLoading, setVerificationLoading] = React.useState(false);
  const [verificationError, setVerificationError] = React.useState("");

  const handleExportExcel = async () => {
    if (displayedProblems.length === 0) return;
    
    const dataToExport = displayedProblems.map((p, idx) => {
      if (activeTab === 'daily') {
        return {
          'No': idx + 1,
          'Hari/Tanggal': p.Hari || p.Tanggal || '',
          'NIP': p.NIP || '',
          'Nama Pegawai': p.Nama || '',
          'Masalah': p.Masalah || '',
          'Detail': p.Detail || ''
        };
      } else {
        if (p.Masalah) {
          return {
            'No': idx + 1,
            'Hari/Tanggal': p.Hari || p.Tanggal || '',
            'NIP': p.NIP || '',
            'Nama Pegawai': p.Nama || '',
            'Jam Masuk': p.JamMasuk || '',
            'Jam Pulang': p.JamPulang || '',
            'TTWM': p.TTWM || '',
            'TTWP': p.TTWP || '',
            'Masalah': p.Masalah || '',
            'Detail': p.Detail || ''
          };
        } else {
          return {
            'No': idx + 1,
            'NIP': p.NIP || '',
            'Nama Pegawai': p.Nama || '',
            'TTWM (Late)': p.TTWM || '',
            'TTWP (Early)': p.TTWP || '',
            'Total Over-Time': p.Total || '',
          };
        }
      }
    });

    try {
      const response = await fetch(`${API_BASE}/api/export_excel`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dataToExport)
      });
      if (!response.ok) throw new Error("Gagal mengekspor Excel.");
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Laporan_Filter_${activeTab === 'daily' ? 'Harian' : 'OPD'}_${new Date().toISOString().slice(0, 10)}.xlsx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      alert("Error: " + e.message);
    }
  };

  const handleAutoResolveMonthly = async (p) => {
    setMonthlyResolving(true);
    setMonthlyResolvingError("");
    setMonthlyResolvingSuccess(false);
    setMonthlyResolvingResults([]);
    
    const skpd1 = document.getElementById("opd_skpd1")?.value || "4.02.01.01";
    const skpd2 = document.getElementById("opd_skpd2")?.value || "4.02.01.01.0010";
    
    const periodVal = document.getElementById("opd_period")?.value || getInitialYearMonth();
    const parts = periodVal.split("-");
    const formattedMonth = parts.length === 2 ? `${parts[1]}-${parts[0]}` : getInitialTargetDate();
    
    try {
      const url = `${API_BASE}/api/auto_resolve_monthly?nip=${p.NIP}&month=${formattedMonth}&skpd1=${skpd1}&skpd2=${skpd2}`;
      const res = await fetch(url);
      const data = await res.json();
      
      if (data.status === "success") {
        setMonthlyResolvingResults(data.results);
        setMonthlyResolvingSuccess(true);
      } else {
        setMonthlyResolvingError(data.message || "Gagal melakukan auto resolve bulanan.");
      }
    } catch (e) {
      setMonthlyResolvingError("Terjadi kesalahan koneksi saat memproses.");
    }
    setMonthlyResolving(false);
  };

  const handleVerifyOpdRealtime = async (p) => {
    setVerificationLoading(true);
    setVerificationError("");
    setVerificationData(null);
    
    const skpd1 = document.getElementById("opd_skpd1")?.value || "4.02.01.01";
    const skpd2 = document.getElementById("opd_skpd2")?.value || "4.02.01.01.0010";
    
    const periodVal = document.getElementById("opd_periode")?.value || getInitialYearMonth();
    const parts = periodVal.split("-");
    const formattedMonth = parts.length === 2 ? `${parts[1]}-${parts[0]}` : getInitialTargetDate();
    
    try {
      const url = `${API_BASE}/api/get_individual_opd_status?nip=${p.NIP}&month=${formattedMonth}&skpd1=${skpd1}&skpd2=${skpd2}`;
      const res = await fetch(url);
      const data = await res.json();
      
      if (data.status === "success") {
        setVerificationData(data);
      } else {
        setVerificationError(data.message || "Gagal mengambil data verifikasi.");
      }
    } catch (e) {
      setVerificationError("Kesalahan koneksi saat verifikasi.");
    }
    setVerificationLoading(false);
  };

  const handleAutoResolveSingle = async (p) => {
    const key = `${p.NIP}_${p.Tanggal}`;
    setResolutionStatus(prev => ({
      ...prev,
      [key]: { status: 'running', message: 'Ambil log & analisis...' }
    }));
    
    const skpd1 = document.getElementById("opd_skpd1")?.value || "4.02.01.01";
    const skpd2 = document.getElementById("opd_skpd2")?.value || "4.02.01.01.0010";
    
    try {
      const url = `${API_BASE}/api/auto_resolve_single?nip=${p.NIP}&date=${p.Tanggal}&skpd1=${skpd1}&skpd2=${skpd2}`;
      const res = await fetch(url);
      const data = await res.json();
      
      setResolutionStatus(prev => ({
        ...prev,
        [key]: { 
          status: data.status,
          message: data.message,
          detectedShift: data.detected_shift
        }
      }));
    } catch (e) {
      setResolutionStatus(prev => ({
        ...prev,
        [key]: { status: 'error', message: `Gagal: Koneksi terputus.` }
      }));
    }
  };

  const handleAutoResolveSelected = async () => {
    const selectedProblems = displayedProblems.filter(p => selectedIds.includes(p.id));
    if (selectedProblems.length === 0) return;
    
    // Set status to queuing/running for all selected
    for (const p of selectedProblems) {
      const key = `${p.NIP}_${p.Tanggal}`;
      setResolutionStatus(prev => ({
        ...prev,
        [key]: { status: 'running', message: 'Dalam antrean...' }
      }));
    }
    
    // Process sequentially to be safe with SPOT API
    for (const p of selectedProblems) {
      await handleAutoResolveSingle(p);
    }
  };

  const handleAutoResolveAll = async () => {
    if (displayedProblems.length === 0) return;
    
    // Set status to queuing/running for all displayed problems
    for (const p of displayedProblems) {
      const key = `${p.NIP}_${p.Tanggal}`;
      setResolutionStatus(prev => ({
        ...prev,
        [key]: { status: 'running', message: 'Dalam antrean...' }
      }));
    }
    
    // Process sequentially
    for (const p of displayedProblems) {
      await handleAutoResolveSingle(p);
    }
  };

  const fetchDaily = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/daily_problems`);
      const data = await res.json();
      setProblems(data.map((p, i) => ({ ...p, id: i })));
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const fetchOpd = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/opd_problems`);
      const data = await res.json();
      setOpdProblems(data.map((p, i) => ({ ...p, id: i })));
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const fetchMonthlyDetail = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/monthly_detail_problems?criteria=${criteria}`);
      const data = await res.json();
      setOpdProblems(data.map((p, i) => ({ 
        ...p, 
        id: i, 
        Total: p.Masalah,
      })));
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  // Reset state detail saat berganti item terpilih
  React.useEffect(() => {
    setRawLogs([]);
    setRawLogsError("");
    setShiftInfo(null);
    setShiftError("");
    setSyncStatus("idle");
    setDailyReport(null);
    setDailyReportError("");
    setShiftPosting(false);
    setShiftPostMessage("");
    setShiftPostError("");
    setMonthlyResolving(false);
    setMonthlyResolvingResults([]);
    setMonthlyResolvingError("");
    setMonthlyResolvingSuccess(false);
    setVerificationData(null);
    setVerificationLoading(false);
    setVerificationError("");
    setKedinasanKeterangan("");
    setKedinasanPosting(false);
    setKedinasanMessage("");
    setKedinasanError("");
  }, [selectedProblem]);

  React.useEffect(() => {
    if (activeTab === "daily") fetchDaily();
    else fetchOpd();
    setSelectedIds([]);
    setSelectedProblem(null);
  }, [activeTab]);

  const toggleSelect = (id) => {
    setSelectedIds(prev => prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]);
  };

  const fetchRawLogs = async (p) => {
    setRawLogsLoading(true);
    setRawLogsError("");
    const skpd1 = document.getElementById("opd_skpd1")?.value || "4.02.01.01";
    const skpd2 = document.getElementById("opd_skpd2")?.value || "4.02.01.01.0010";
    try {
      const res = await fetch(`${API_BASE}/api/get_log_absensi?nip=${p.NIP}&date=${p.Tanggal}&skpd1=${skpd1}&skpd2=${skpd2}`);
      const data = await res.json();
      if (data.status === "success") {
        setRawLogs(data.logs);
      } else {
        setRawLogsError(data.message || "Gagal memuat log.");
      }
    } catch (e) {
      setRawLogsError("Terjadi kesalahan koneksi.");
    }
    setRawLogsLoading(false);
  };

  const fetchShiftInfo = async (p) => {
    setShiftLoading(true);
    setShiftError("");
    try {
      const res = await fetch(`${API_BASE}/api/get_shift_for_date?nip=${p.NIP}&date=${p.Tanggal}`);
      const data = await res.json();
      if (data.status === "success") {
        setShiftInfo(data);
      } else {
        setShiftError(data.message || "Gagal memuat shift.");
      }
    } catch (e) {
      setShiftError("Terjadi kesalahan koneksi.");
    }
    setShiftLoading(false);
  };

  const handlePostShift = async (p, shiftCode) => {
    setShiftPosting(true);
    setShiftPostMessage("");
    setShiftPostError("");
    const skpd1 = document.getElementById("opd_skpd1")?.value || "4.02.01.01";
    const skpd2 = document.getElementById("opd_skpd2")?.value || "4.02.01.01.0010";
    try {
      const res = await fetch(`${API_BASE}/api/post_shift_for_date?nip=${p.NIP}&date=${p.Tanggal}&shift=${shiftCode}&skpd1=${skpd1}&skpd2=${skpd2}`);
      const data = await res.json();
      if (data.status === "success") {
        setShiftPostMessage(`Berhasil diset ke ${shiftCode}!`);
      } else {
        setShiftPostError(data.message || "Gagal menyetel shift.");
      }
    } catch (e) {
      setShiftPostError("Terjadi kesalahan koneksi.");
    }
    setShiftPosting(false);
  };

  const handlePostKedinasan = async (p, type) => {
    if (!kedinasanKeterangan || kedinasanKeterangan.trim() === "") {
      setKedinasanError("Keterangan wajib diisi!");
      return;
    }
    setKedinasanPosting(true);
    setKedinasanMessage("");
    setKedinasanError("");
    const skpd1 = document.getElementById("opd_skpd1")?.value || "4.02.01.01";
    const skpd2 = document.getElementById("opd_skpd2")?.value || "4.02.01.01.0010";
    try {
      const url = `${API_BASE}/api/post_kedinasan?nip=${p.NIP}&nama=${encodeURIComponent(p.Nama)}&date=${p.Tanggal}&keterangan=${encodeURIComponent(kedinasanKeterangan)}&type=${type}&skpd1=${skpd1}&skpd2=${skpd2}`;
      const res = await fetch(url);
      const data = await res.json();
      if (data.status === "success") {
        setKedinasanMessage(data.message);
        setKedinasanKeterangan("");
      } else {
        setKedinasanError(data.message || "Gagal menyimpan kedinasan.");
      }
    } catch (e) {
      setKedinasanError("Terjadi kesalahan koneksi.");
    }
    setKedinasanPosting(false);
  };

  const triggerSync = async (p) => {
    setSyncLoading(true);
    setSyncStatus("idle");
    const skpd1 = document.getElementById("opd_skpd1")?.value || "4.02.01.01";
    const skpd2 = document.getElementById("opd_skpd2")?.value || "4.02.01.01.0010";
    try {
      const res = await fetch(`${API_BASE}/api/sync_single?nip=${p.NIP}&date=${p.Tanggal}&skpd1=${skpd1}&skpd2=${skpd2}`);
      const data = await res.json();
      if (data.status === "success") {
        setSyncStatus("success");
      } else {
        setSyncStatus("error");
      }
    } catch (e) {
      setSyncStatus("error");
    }
    setSyncLoading(false);
  };

  const fetchDailyReport = async (p) => {
    setDailyReportLoading(true);
    setDailyReportError("");
    const skpd1 = document.getElementById("opd_skpd1")?.value || "4.02.01.01";
    const skpd2 = document.getElementById("opd_skpd2")?.value || "4.02.01.01.0010";
    try {
      const res = await fetch(`${API_BASE}/api/get_daily_report?nip=${p.NIP}&date=${p.Tanggal}&skpd1=${skpd1}&skpd2=${skpd2}`);
      const data = await res.json();
      if (data.status === "success") {
        setDailyReport(data.report);
      } else {
        setDailyReportError(data.message || "Gagal memuat laporan harian.");
      }
    } catch (e) {
      setDailyReportError("Terjadi kesalahan koneksi.");
    }
    setDailyReportLoading(false);
  };

  const displayedProblems = (activeTab === "daily" ? problems : opdProblems).filter(p => {
    const matchesSearch = (p.Nama||"").toLowerCase().includes(filter.toLowerCase()) || 
      (p.Masalah && p.Masalah.toLowerCase().includes(filter.toLowerCase())) ||
      (p.Tanggal && p.Tanggal.includes(filter)) ||
      (p.NIP && p.NIP.includes(filter));
    
    if (activeTab === "daily" && masalahFilter !== "ALL") {
      return matchesSearch && p.Masalah === masalahFilter;
    }
    return matchesSearch;
  });

  const selectAll = (type) => {
    if (type === 'all') setSelectedIds(displayedProblems.map(p => p.id));
    if (type === 'none') setSelectedIds([]);
  };

  const handleProcessDaily = async () => {
    const toProcess = problems.filter(p => selectedIds.includes(p.id));
    const res = await fetch(`${API_BASE}/api/run/problems_json`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(toProcess)
    });
    const result = await res.json();
    if (result.status === 'ready') runScript('otomatisasi_api.py');
  };

  const handleProcessOpd = async () => {
    const toProcess = opdProblems.filter(p => selectedIds.includes(p.id));
    const periodVal = document.getElementById("opd_period")?.value;
    const formattedMonth = formatMonthToIndo(periodVal);
    const url = formattedMonth 
      ? `${API_BASE}/api/run/prepare_monthly_download?month=${encodeURIComponent(formattedMonth)}` 
      : `${API_BASE}/api/run/prepare_monthly_download`;

    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(toProcess)
    });
    const result = await res.json();
    if (result.status === 'ready') {
      runScript('batch_download_laporan.py');
    }
  };

  return (
    <div className="view-container animate-fade-in">
      <div className="header-glass">
        <div>
          <div className="view-badge">INTEGRATED PIPELINE</div>
          <h1>Attendance Management Workspace</h1>
          <p>Scan daily gaps or analyze unit-wide patterns to trigger deep-dive downloads.</p>
        </div>
      </div>

      <div className="tabs" style={{display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', background: 'rgba(255,255,255,0.05)', padding: '0.5rem', borderRadius: '12px', width: 'fit-content'}}>
        <button className={`btn ${activeTab === 'daily' ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setActiveTab('daily')} style={{borderRadius: '8px'}}>📊 Daily Problems</button>
        <button className={`btn ${activeTab === 'opd' ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setActiveTab('opd')} style={{borderRadius: '8px'}}>🏢 OPD Analytics Pipeline</button>
      </div>

      <div className="resolver-grid" style={{
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
        gap: '1.5rem', 
        marginBottom: '2rem'
      }}>
        {/* Input Card */}
        <div className="card glass-card" style={{padding: '1.5rem', borderLeft: '4px solid var(--primary)'}}>
          <div className="card-header" style={{marginBottom: '1rem'}}>
            <div className="card-title">
              {activeTab === 'daily' ? '📥 Update Daily Data' : '🔍 Scan OPD Summary'}
            </div>
          </div>
          
          {activeTab === 'daily' ? (
            <>
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.8rem', marginBottom: '1rem'}}>
                <div className="input-field">
                  <label>Start</label>
                  <input type="date" id="prob_start" className="table-input" defaultValue={getTodayString()} />
                </div>
                <div className="input-field">
                  <label>End</label>
                  <input type="date" id="prob_end" className="table-input" defaultValue={getTodayString()} />
                </div>
              </div>
              <div className="button-group">
                <button className="btn btn-primary" style={{flex: 1}} onClick={() => {
                  const s = formatDateToDMY(document.getElementById('prob_start').value);
                  const e = formatDateToDMY(document.getElementById('prob_end').value);
                  runScript('batch_download_harian.py', `${s} ${e}`);
                }}>Download Harian</button>
                <button className="btn btn-outline" onClick={fetchDaily}>Scan Problem</button>
              </div>
              
              <div className="divider">FILTER MASALAH</div>
              <div className="button-group" style={{display: 'flex', gap: '0.4rem', flexWrap: 'wrap'}}>
                <button className={`btn btn-sm ${masalahFilter === 'ALL' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setMasalahFilter('ALL')} style={{flex: '1 0 45%'}}>Semua</button>
                <button className={`btn btn-sm ${masalahFilter === 'TMTB' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setMasalahFilter('TMTB')} style={{flex: '1 0 45%'}}>TMTB</button>
                <button className={`btn btn-sm ${masalahFilter === 'Datang Kosong' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setMasalahFilter('Datang Kosong')} style={{flex: '1 0 45%'}}>Datang Kosong</button>
                <button className={`btn btn-sm ${masalahFilter === 'Pulang Kosong' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setMasalahFilter('Pulang Kosong')} style={{flex: '1 0 45%'}}>Pulang Kosong</button>
              </div>
            </>
          ) : (
            <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.8rem'}}>
              <div className="input-field" style={{gridColumn: 'span 2'}}>
                <label>Bulan & Tahun (Laporan OPD)</label>
                <input type="month" id="opd_period" className="table-input" defaultValue={getInitialYearMonth()} />
              </div>
              <div className="input-field">
                <label>SKPD 1</label>
                <input id="opd_skpd1" className="table-input" defaultValue="4.02.01.01" />
              </div>
              <div className="input-field">
                <label>SKPD 2</label>
                <input id="opd_skpd2" className="table-input" defaultValue="4.02.01.01.0010" />
              </div>
              <button className="btn btn-primary" onClick={() => {
                const p = formatMonthToIndo(document.getElementById('opd_period').value);
                const s1 = document.getElementById('opd_skpd1').value;
                const s2 = document.getElementById('opd_skpd2').value;
                runScript('batch_download_opd.py', `"${p}" ${s1} ${s2}`);
              }}>📥 Download OPD</button>
              <button className="btn btn-outline" onClick={fetchOpd}>🔍 Scan Problems</button>
            </div>
          )}
        </div>

        {/* Tools Card */}
        <div className="card glass-card" style={{padding: '1.5rem', borderLeft: '4px solid var(--accent)'}}>
          <div className="card-header" style={{marginBottom: '1rem'}}>
            <div className="card-title">{activeTab === 'daily' ? 'Batch Selection' : '🎯 Analysis Filters'}</div>
          </div>
          
          {activeTab === 'opd' && (
            <div className="button-group" style={{display: 'flex', gap: '0.5rem', marginBottom: '1rem'}}>
              <button className={`btn btn-sm ${criteria === 'TM' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setCriteria('TM')} style={{flex: 1}}>TM Saja</button>
              <button className={`btn btn-sm ${criteria === 'PSW' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setCriteria('PSW')} style={{flex: 1}}>PSW Saja</button>
              <button className={`btn btn-sm ${criteria === 'ALL' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setCriteria('ALL')} style={{flex: 1}}>TM & PSW</button>
            </div>
          )}

          <input className="table-input" placeholder="Search name or NIP..." value={filter} onChange={e => setFilter(e.target.value)} style={{width: '100%', marginBottom: '1rem'}} />
          
          <div className="button-group" style={{display: 'flex', gap: '0.5rem'}}>
            <button className="btn btn-outline btn-sm" style={{flex: 1}} onClick={() => selectAll('all')}>Select Visible</button>
            <button className="btn btn-outline btn-sm" style={{flex: 1}} onClick={() => selectAll('none')}>Clear</button>
            {activeTab === 'daily' && displayedProblems.length > 0 && (
              <button 
                className="btn btn-primary btn-sm" 
                style={{flex: 2, background: 'linear-gradient(135deg, var(--accent), var(--accent-secondary))'}}
                onClick={handleAutoResolveAll}
              >
                ⚡ Auto Resolve All
              </button>
            )}
            {activeTab === 'opd' && (
              <button className="btn btn-primary btn-sm" style={{flex: 2}} onClick={fetchMonthlyDetail} disabled={loading}>🚀 Ekstrak & Analisa</button>
            )}
          </div>
        </div>
      </div>

      {/* Table Results & Interactive Panel Split Layout */}
      <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'flex-start', flexWrap: 'wrap' }}>
        <div className="card glass-card" style={{ padding: '0', overflow: 'hidden', flex: selectedProblem && activeTab === 'daily' ? '3 1 60%' : '1 1 100%', minWidth: '320px' }}>
          <div className="card-header" style={{padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
            <div className="card-title">{activeTab === 'daily' ? 'Daily Analysis Results' : 'High Over-Time Detection (>5hr)'}</div>
            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
              <button 
                className="btn btn-outline btn-sm"
                onClick={handleExportExcel}
                disabled={displayedProblems.length === 0}
                style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}
              >
                📥 Export Excel
              </button>
              <div className="view-badge">{displayedProblems.length} results</div>
            </div>
          </div>
          <div className="table-container" style={{maxHeight: '500px', overflowY: 'auto'}}>
            <table className="schedule-table">
              <thead>
                <tr>
                  <th style={{width: '50px', cursor: 'pointer'}} onClick={() => {
                    const allVisibleIds = displayedProblems.map(p => p.id);
                    const isAllSelected = allVisibleIds.every(id => selectedIds.includes(id));
                    if (isAllSelected) setSelectedIds(selectedIds.filter(id => !allVisibleIds.includes(id)));
                    else setSelectedIds([...new Set([...selectedIds, ...allVisibleIds])]);
                  }}>
                    <div className={`checkbox-custom ${(displayedProblems.length > 0 && displayedProblems.every(p => selectedIds.includes(p.id))) ? 'checked' : ''}`}>
                      {(displayedProblems.length > 0 && displayedProblems.every(p => selectedIds.includes(p.id))) ? '✓' : ''}
                    </div>
                  </th>
                  <th style={{width: '120px'}}>Hari/Tanggal</th>
                  <th style={{width: '180px'}}>NIP</th>
                  <th>Nama Pegawai</th>
                  {displayedProblems[0]?.JamMasuk !== undefined && <th style={{width: '110px'}}>Jam Masuk</th>}
                  {displayedProblems[0]?.JamPulang !== undefined && <th style={{width: '110px'}}>Jam Pulang</th>}
                  {displayedProblems[0]?.JamMasuk !== undefined && <th style={{width: '90px'}}>TTWM</th>}
                  {displayedProblems[0]?.JamMasuk !== undefined && <th style={{width: '90px'}}>TTWP</th>}
                  {!displayedProblems[0]?.Masalah && <th style={{width: '100px'}}>TTWM</th>}
                  {!displayedProblems[0]?.Masalah && <th style={{width: '100px'}}>TTWP</th>}
                  <th style={{width: '150px'}}>{displayedProblems[0]?.Masalah ? 'Masalah' : 'Total'}</th>
                  {activeTab === 'daily' && <th style={{width: '250px'}}>Status/Aksi</th>}
                </tr>
              </thead>
              <tbody>
                {displayedProblems.map(p => {
                  const isSelectedForAction = selectedProblem && selectedProblem.NIP === p.NIP;
                  return (
                    <tr 
                      key={p.id} 
                      className={`${selectedIds.includes(p.id) ? 'active' : ''}`}
                      onClick={() => {
                        setSelectedProblem(p);
                      }}
                      style={{ 
                        cursor: 'pointer',
                        borderLeft: isSelectedForAction ? '4px solid var(--accent)' : 'none',
                        background: isSelectedForAction ? 'rgba(99, 102, 241, 0.08)' : ''
                      }}
                    >
                      <td 
                        style={{textAlign: 'center', width: '50px'}}
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleSelect(p.id);
                        }}
                      >
                        <div className={`checkbox-custom ${selectedIds.includes(p.id) ? 'checked' : ''}`}>
                          {selectedIds.includes(p.id) ? '✓' : ''}
                        </div>
                      </td>
                      <td style={{fontSize: '0.85rem'}}>{p.Hari || p.Tanggal || '-'}</td>
                      <td style={{fontFamily: 'monospace'}}>{p.NIP}</td>
                      <td style={{fontWeight: isSelectedForAction ? 700 : 400}}>{p.Nama}</td>
                      {displayedProblems[0]?.JamMasuk !== undefined && <td style={{fontSize: '0.9rem', opacity: 0.8}}>{p.JamMasuk || '-'}</td>}
                      {displayedProblems[0]?.JamPulang !== undefined && <td style={{fontSize: '0.9rem', opacity: 0.8}}>{p.JamPulang || '-'}</td>}
                      {displayedProblems[0]?.JamMasuk !== undefined && <td style={{fontSize: '0.9rem', opacity: 0.8}}>{p.TTWM || '-'}</td>}
                      {displayedProblems[0]?.JamMasuk !== undefined && <td style={{fontSize: '0.9rem', opacity: 0.8}}>{p.TTWP || '-'}</td>}
                      {!displayedProblems[0]?.Masalah && <td style={{fontSize: '0.9rem', opacity: 0.8}}>{p.TTWM}</td>}
                      {!displayedProblems[0]?.Masalah && <td style={{fontSize: '0.9rem', opacity: 0.8}}>{p.TTWP}</td>}
                      <td>
                        <span className={`badge ${p.Masalah ? (p.Masalah === 'Kosong' ? 'badge-urgent' : 'badge-warn') : 'badge-primary'}`}>
                          {p.Masalah || p.Total}
                        </span>
                      </td>
                      {activeTab === 'daily' && (
                        <td onClick={(e) => e.stopPropagation()}>
                          {(() => {
                            const key = `${p.NIP}_${p.Tanggal}`;
                            const res = resolutionStatus[key];
                            if (!res) {
                              return (
                                <button 
                                  className="btn btn-outline btn-sm"
                                  style={{ padding: '0.35rem 0.75rem', fontSize: '0.7rem', display: 'inline-flex', alignItems: 'center', gap: '0.3rem' }}
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleAutoResolveSingle(p);
                                  }}
                                >
                                  ⚡ Auto Resolve
                                </button>
                              );
                            }
                            if (res.status === 'running') {
                              return (
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                  <div className="spinner-mini"></div>
                                  <span style={{ fontSize: '0.72rem', color: 'var(--accent)', fontWeight: 500 }}>{res.message}</span>
                                </div>
                              );
                            }
                            if (res.status === 'success') {
                              const shiftName = res.detectedShift === 'P' ? 'Pagi' : res.detectedShift === 'S' ? 'Siang' : 'Malam';
                              return (
                                <span className="badge" style={{ background: 'rgba(16, 185, 129, 0.1)', color: 'var(--success)', border: '1px solid rgba(16, 185, 129, 0.2)', fontSize: '0.7rem' }} title={res.message}>
                                  ✅ Auto: {shiftName} ({res.detectedShift})
                                </span>
                              );
                            }
                            if (res.status === 'review_manual') {
                              return (
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                  <span className="badge" style={{ background: 'rgba(245, 158, 11, 0.1)', color: 'var(--warning)', border: '1px solid rgba(245, 158, 11, 0.2)', fontSize: '0.7rem' }} title={res.message}>
                                    ⚠️ Review Manual
                                  </span>
                                  <button 
                                    className="btn btn-ghost btn-sm" 
                                    style={{ padding: '0.2rem', minHeight: 'auto', minWidth: 'auto' }}
                                    title="Coba Lagi"
                                    onClick={() => handleAutoResolveSingle(p)}
                                  >🔄</button>
                                </div>
                              );
                            }
                            return (
                              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <span className="badge badge-urgent" style={{ fontSize: '0.7rem' }} title={res.message}>
                                  ❌ Gagal
                                </span>
                                <button 
                                  className="btn btn-ghost btn-sm" 
                                  style={{ padding: '0.2rem', minHeight: 'auto', minWidth: 'auto' }}
                                  title="Coba Lagi"
                                  onClick={() => handleAutoResolveSingle(p)}
                                >🔄</button>
                              </div>
                            );
                          })()}
                        </td>
                      )}
                    </tr>
                  );
                })}
                {displayedProblems.length === 0 && <tr><td colSpan={12} style={{textAlign: 'center', padding: '4rem', opacity: 0.5}}>No data to display. Click Scan/Analyze to begin.</td></tr>}
              </tbody>
            </table>
          </div>
          {selectedIds.length > 0 && (
            <div className="process-footer animate-up" style={{padding: '1.5rem', display: 'flex', justifyContent: 'center', gap: '1rem', background: 'rgba(255,255,255,0.02)'}}>
              {activeTab === 'daily' && (
                <button 
                  className="btn btn-outline" 
                  style={{padding: '1rem 2rem', borderColor: 'var(--accent)', color: '#fff'}}
                  onClick={handleAutoResolveSelected}
                >
                  ⚡ AUTO RESOLVE SELECTED
                </button>
              )}
              <button className="btn btn-primary" style={{padding: '1rem 3rem'}} onClick={async () => {
                  if (activeTab === 'daily') {
                      handleProcessDaily();
                  } else {
                      const firstSelected = opdProblems.find(p => p.id === selectedIds[0]);
                      if (firstSelected?.Masalah) {
                          const s1 = document.getElementById('opd_skpd1')?.value || "4.02.01.01";
                          const s2 = document.getElementById('opd_skpd2')?.value || "4.02.01.01.0010";
                          const toProcess = opdProblems.filter(p => selectedIds.includes(p.id)).map(p => ({ ...p, skpd1: s1, skpd2: s2 }));
                          const res = await fetch(`${API_BASE}/api/run/problems_json`, {
                              method: 'POST',
                              headers: { 'Content-Type': 'application/json' },
                              body: JSON.stringify(toProcess)
                          });
                          const result = await res.json();
                          if (result.status === 'ready') runScript('otomatisasi_api.py');
                      } else {
                          handleProcessOpd();
                      }
                  }
              }}>
                {activeTab === 'daily' 
                  ? `🚀 RESOLVE ${selectedIds.length} ITEMS VIA FAST API` 
                  : (opdProblems.find(p => p.id === selectedIds[0])?.Masalah 
                      ? `🚀 RESOLVE ${selectedIds.length} ITEMS VIA FAST API` 
                      : `📥 DOWNLOAD DETAILED REPORTS FOR ${selectedIds.length} EMPLOYEES`)}
              </button>
            </div>
          )}
        </div>

        {/* Resolution Panel */}
        {selectedProblem && (
          <div className="card glass-card animate-up" style={{ padding: '1.5rem', flex: '2 1 35%', minWidth: '320px', position: 'sticky', top: '1.5rem', borderLeft: '4px solid var(--accent)', display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.25rem', borderBottom: '1px solid var(--border)', paddingBottom: '1rem' }}>
              <div style={{ flex: 1, paddingRight: '0.5rem' }}>
                <div className="view-badge" style={{ background: 'rgba(99,102,241,0.1)', color: 'var(--accent)', marginBottom: '0.5rem', display: 'inline-block' }}>
                  {activeTab === 'daily' ? 'RESOLVER INTERAKTIF' : 'RESOLVER BULANAN'}
                </div>
                <h2 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#fff', wordBreak: 'break-word', lineHeight: '1.3' }}>{selectedProblem.Nama}</h2>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', marginTop: '0.3rem', lineHeight: '1.4' }}>
                  <strong>NIP:</strong> {selectedProblem.NIP}<br />
                  {activeTab === 'daily' ? (
                    <><strong>Tanggal:</strong> {selectedProblem.Tanggal}</>
                  ) : (
                    <><strong>Bulan:</strong> {(() => {
                      const val = document.getElementById("opd_period")?.value || getInitialYearMonth();
                      return formatMonthToIndo(val);
                    })()}</>
                  )}
                </p>
                <div style={{ marginTop: '0.5rem' }}>
                  {activeTab === 'daily' ? (
                    <span className="badge badge-urgent">{selectedProblem.Masalah}</span>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                      <div style={{ display: 'flex', gap: '0.3rem', flexWrap: 'wrap' }}>
                        <span className="badge badge-urgent" title="Total Telat Masuk">TTWM: {selectedProblem.TTWM}</span>
                        <span className="badge badge-warn" title="Total Pulang Cepat">TTWP: {selectedProblem.TTWP}</span>
                      </div>
                      {selectedProblem.JamMasuk !== undefined && (
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '0.2rem', lineHeight: '1.4' }}>
                          <div>🚪 <strong>Masuk:</strong> {selectedProblem.JamMasuk || '-'}</div>
                          <div>🚪 <strong>Pulang:</strong> {selectedProblem.JamPulang || '-'}</div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
              <button 
                onClick={() => setSelectedProblem(null)} 
                style={{ 
                  background: 'transparent', 
                  border: 'none', 
                  color: 'var(--text-secondary)', 
                  fontSize: '1.75rem', 
                  cursor: 'pointer', 
                  lineHeight: '1',
                  padding: '0 0.5rem'
                }}
              >&times;</button>
            </div>

            {activeTab === 'daily' ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {/* Langkah 1: Log Absensi */}
                <div style={{ background: 'rgba(15, 23, 42, 0.4)', border: '1px solid var(--border)', borderRadius: '12px', padding: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                    <h3 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#fff' }}>🔍 Langkah 1: Log Absensi Mentah</h3>
                    <button className="btn btn-outline btn-sm" onClick={() => fetchRawLogs(selectedProblem)} disabled={rawLogsLoading}>
                      {rawLogsLoading ? 'Loading...' : 'Ambil Log'}
                    </button>
                  </div>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem', lineHeight: '1.3' }}>Cek riwayat tapping finger pegawai di mesin.</p>
                  
                  {rawLogsError && <div className="error-box" style={{ marginTop: '0.5rem' }}>{rawLogsError}</div>}
                  
                  {rawLogs.length > 0 ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '0.5rem', maxHeight: '180px', overflowY: 'auto' }}>
                      {rawLogs.map((log, idx) => {
                        const parts = log.Tanggal.split(" ");
                        const datePart = parts[0] || "";
                        const timePart = parts[1] || "";
                        return (
                          <div key={idx} style={{ 
                            background: 'rgba(2, 6, 23, 0.5)', 
                            padding: '0.75rem', 
                            borderRadius: '10px', 
                            fontSize: '0.75rem', 
                            border: '1px solid rgba(255,255,255,0.05)',
                            display: 'flex',
                            flexDirection: 'column',
                            gap: '0.35rem'
                          }}>
                            <div style={{ display: 'flex', alignItems: 'center', justifycontent: 'space-between' }}>
                              <div style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--success)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                                🕒 {timePart}
                              </div>
                              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 500 }}>
                                📅 {datePart}
                              </div>
                            </div>
                            <div style={{ 
                              color: 'var(--text-secondary)', 
                              fontSize: '0.7rem', 
                              borderTop: '1px solid rgba(255,255,255,0.04)', 
                              paddingTop: '0.3rem', 
                              display: 'flex', 
                              justifycontent: 'space-between' 
                            }}>
                              <span>SN: <strong style={{ color: '#fff' }}>{log.SerialNumber}</strong></span>
                              <span>IP: <strong style={{ color: '#fff' }}>{log.IP}</strong></span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  ) : !rawLogsLoading && (
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontStyle: 'italic', marginTop: '0.2rem' }}>Belum ada log yang diambil.</div>
                  )}
                </div>

                {/* Langkah 2: Setel Jadwal Shift */}
                <div style={{ background: 'rgba(15, 23, 42, 0.4)', border: '1px solid var(--border)', borderRadius: '12px', padding: '1rem' }}>
                  <h3 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#fff', marginBottom: '0.4rem' }}>📅 Langkah 2: Atur Jadwal Shift</h3>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.6rem', lineHeight: '1.3' }}>Setel kode shift kerja pegawai pada tanggal bermasalah ini.</p>
                  
                  <div style={{ display: 'flex', gap: '0.4rem', marginTop: '0.5rem', flexWrap: 'wrap' }}>
                    <button 
                      className="btn btn-outline btn-sm" 
                      style={{ flex: '1 0 18%', borderColor: '#eab308', color: '#eab308', fontSize: '0.7rem' }} 
                      onClick={() => handlePostShift(selectedProblem, 'P')} 
                      disabled={shiftPosting}
                    >
                      Pagi (P)
                    </button>
                    <button 
                      className="btn btn-outline btn-sm" 
                      style={{ flex: '1 0 18%', borderColor: '#6366f1', color: '#6366f1', fontSize: '0.7rem' }} 
                      onClick={() => handlePostShift(selectedProblem, 'S')} 
                      disabled={shiftPosting}
                    >
                      Siang (S)
                    </button>
                    <button 
                      className="btn btn-outline btn-sm" 
                      style={{ flex: '1 0 18%', borderColor: '#f87171', color: '#f87171', fontSize: '0.7rem' }} 
                      onClick={() => handlePostShift(selectedProblem, 'M')} 
                      disabled={shiftPosting}
                    >
                      Malam (M)
                    </button>
                    <button 
                      className="btn btn-outline btn-sm" 
                      style={{ flex: '1 0 18%', borderColor: '#10b981', color: '#10b981', fontSize: '0.7rem' }} 
                      onClick={() => handlePostShift(selectedProblem, 'D')} 
                      disabled={shiftPosting}
                    >
                      Dinas (D)
                    </button>
                    <button 
                      className="btn btn-outline btn-sm" 
                      style={{ flex: '1 0 18%', borderColor: 'var(--text-muted)', color: 'var(--text-muted)', fontSize: '0.7rem' }} 
                      onClick={() => handlePostShift(selectedProblem, 'L')} 
                      disabled={shiftPosting}
                    >
                      Libur (L)
                    </button>
                  </div>

                  {shiftPosting && <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontStyle: 'italic', marginTop: '0.5rem' }}>Mengubah jadwal shift...</div>}
                  {shiftPostMessage && <div style={{ color: 'var(--success)', fontSize: '0.75rem', fontWeight: 700, marginTop: '0.5rem' }}>✅ {shiftPostMessage}</div>}
                  {shiftPostError && <div className="error-box" style={{ marginTop: '0.5rem', fontSize: '0.75rem' }}>❌ {shiftPostError}</div>}
                </div>

                {/* Langkah 2b: Dinas Luar / Diklat */}
                <div style={{ background: 'rgba(15, 23, 42, 0.4)', border: '1px solid var(--border)', borderRadius: '12px', padding: '1rem' }}>
                  <h3 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#fff', marginBottom: '0.4rem' }}>💼 Langkah 2b: Dinas Luar / Diklat</h3>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.6rem', lineHeight: '1.3' }}>Daftarkan kedinasan pegawai jika sedang dinas luar atau diklat.</p>
                  
                  <div style={{ marginBottom: '0.6rem' }}>
                    <label style={{ display: 'block', fontSize: '0.7rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>Keterangan / Deskripsi:</label>
                    <textarea 
                      className="table-input" 
                      style={{ width: '100%', minHeight: '60px', fontSize: '0.75rem', padding: '0.4rem', borderRadius: '6px', background: 'rgba(2, 6, 23, 0.4)', color: '#fff', border: '1px solid var(--border)', resize: 'vertical' }}
                      value={kedinasanKeterangan}
                      onChange={e => setKedinasanKeterangan(e.target.value)}
                      placeholder="Contoh: Rapat koordinasi dinas..."
                    />
                  </div>

                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button 
                      className="btn btn-outline btn-sm" 
                      style={{ flex: 1, borderColor: '#10b981', color: '#10b981', fontSize: '0.75rem' }} 
                      onClick={() => handlePostKedinasan(selectedProblem, 'dinas')} 
                      disabled={kedinasanPosting}
                    >
                      Dinas Luar (DL)
                    </button>
                    <button 
                      className="btn btn-outline btn-sm" 
                      style={{ flex: 1, borderColor: '#6366f1', color: '#6366f1', fontSize: '0.75rem' }} 
                      onClick={() => handlePostKedinasan(selectedProblem, 'diklat')} 
                      disabled={kedinasanPosting}
                    >
                      Diklat
                    </button>
                  </div>

                  {kedinasanPosting && <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontStyle: 'italic', marginTop: '0.5rem' }}>Mendaftarkan kedinasan...</div>}
                  {kedinasanMessage && <div style={{ color: 'var(--success)', fontSize: '0.75rem', fontWeight: 700, marginTop: '0.5rem' }}>✅ {kedinasanMessage}</div>}
                  {kedinasanError && <div className="error-box" style={{ marginTop: '0.5rem', fontSize: '0.75rem' }}>❌ {kedinasanError}</div>}
                </div>

                {/* Langkah 3: Sinkronisasi */}
                <div style={{ background: 'rgba(15, 23, 42, 0.4)', border: '1px solid var(--border)', borderRadius: '12px', padding: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                    <h3 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#fff' }}>🔄 Langkah 3: Sinkronisasi</h3>
                    <button className="btn btn-primary btn-sm" onClick={() => triggerSync(selectedProblem)} disabled={syncLoading}>
                      {syncLoading ? 'Syncing...' : 'Sinkronkan'}
                    </button>
                  </div>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem', lineHeight: '1.3' }}>Kirim data tapping ke sistem SPOT.</p>
                  
                  {syncStatus === 'success' && (
                    <div style={{ color: 'var(--success)', fontSize: '0.75rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.3rem', marginTop: '0.5rem' }}>
                      ✅ Sinkronisasi Berhasil!
                    </div>
                  )}
                  {syncStatus === 'error' && (
                    <div style={{ color: 'var(--danger)', fontSize: '0.75rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.3rem', marginTop: '0.5rem' }}>
                      ❌ Sinkronisasi Gagal!
                    </div>
                  )}
                </div>

                {/* Langkah 4: Verifikasi Laporan Harian */}
                <div style={{ background: 'rgba(15, 23, 42, 0.4)', border: '1px solid var(--border)', borderRadius: '12px', padding: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                    <h3 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#fff' }}>✅ Langkah 4: Cek Laporan Harian</h3>
                    <button className="btn btn-outline btn-sm" onClick={() => fetchDailyReport(selectedProblem)} disabled={dailyReportLoading}>
                      {dailyReportLoading ? 'Loading...' : 'Verifikasi'}
                    </button>
                  </div>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem', lineHeight: '1.3' }}>Konfirmasi jam Masuk/Pulang yang terupdate.</p>
                  
                  {dailyReportError && <div className="error-box" style={{ marginTop: '0.5rem' }}>{dailyReportError}</div>}
                  
                  {dailyReport ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '0.5rem', background: 'rgba(2, 6, 23, 0.3)', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border)' }}>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.75rem' }}>
                        <div><span style={{ color: 'var(--text-muted)' }}>Masuk:</span> <strong style={{ color: dailyReport.Masuk ? '#fff' : 'var(--danger)' }}>{dailyReport.Masuk || 'Kosong'}</strong></div>
                        <div><span style={{ color: 'var(--text-muted)' }}>Pulang:</span> <strong style={{ color: dailyReport.Pulang ? '#fff' : 'var(--danger)' }}>{dailyReport.Pulang || 'Kosong'}</strong></div>
                      </div>
                      <div style={{ fontSize: '0.75rem', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '0.4rem', marginTop: '0.2rem' }}>
                        <span style={{ color: 'var(--text-muted)' }}>Keterangan:</span> <strong style={{ color: dailyReport.Keterangan ? 'var(--warning)' : 'var(--success)' }}>{dailyReport.Keterangan || 'Sesuai (Ok)'}</strong>
                      </div>
                      <div style={{ marginTop: '0.3rem' }}>
                        {(!dailyReport.Masuk || !dailyReport.Pulang) && !/(dinas|diklat)/i.test(dailyReport.Keterangan || '') ? (
                          <span className="badge badge-warn" style={{ fontSize: '0.65rem', padding: '0.15rem 0.5rem' }}>⚠️ Masih Ada Jam Kosong</span>
                        ) : (
                          <span className="badge badge-primary" style={{ fontSize: '0.65rem', padding: '0.15rem 0.5rem', background: 'rgba(16, 185, 129, 0.1)', color: 'var(--success)' }}>
                            {/(dinas|diklat)/i.test(dailyReport.Keterangan || '') ? '✅ Dinas / Diklat' : '✅ Sudah Sesuai (Ok)'}
                          </span>
                        )}
                      </div>
                    </div>
                  ) : !dailyReportLoading && (
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontStyle: 'italic', marginTop: '0.2rem' }}>Belum diverifikasi.</div>
                  )}
                </div>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                <div style={{ background: 'rgba(15, 23, 42, 0.4)', border: '1px solid var(--border)', borderRadius: '12px', padding: '1rem' }}>
                  <h3 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#fff', marginBottom: '0.4rem' }}>⚡ Perbaikan Otomatis 1 Bulan</h3>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.8rem', lineHeight: '1.4' }}>
                    Sistem akan menganalisa log absen mentah harian pegawai sepanjang bulan, mencocokkan shift yang sesuai secara otomatis untuk setiap hari, lalu menyinkronkannya langsung ke SPOT.
                  </p>
                  
                  <button 
                    className="btn btn-primary" 
                    style={{ width: '100%', justifyContent: 'center' }} 
                    onClick={() => handleAutoResolveMonthly(selectedProblem)} 
                    disabled={monthlyResolving}
                  >
                    {monthlyResolving ? (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <div className="spinner-mini"></div>
                        Memproses Perbaikan...
                      </div>
                    ) : '🚀 Mulai Perbaikan Bulanan'}
                  </button>
                  
                  {monthlyResolvingError && (
                    <div className="error-box" style={{ marginTop: '0.75rem', fontSize: '0.75rem' }}>
                      ❌ {monthlyResolvingError}
                    </div>
                  )}
                  
                  {monthlyResolvingSuccess && (
                    <div style={{ color: 'var(--success)', fontSize: '0.78rem', fontWeight: 700, marginTop: '0.75rem' }}>
                      ✅ Berhasil memproses perbaikan bulanan! Silakan lakukan cetak ulang berkas di SPOT untuk memverifikasi.
                    </div>
                  )}
                </div>

                {/* Real-time Verification Card */}
                <div style={{ background: 'rgba(15, 23, 42, 0.4)', border: '1px solid var(--border)', borderRadius: '12px', padding: '1rem' }}>
                  <h3 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#fff', marginBottom: '0.4rem' }}>📊 Verifikasi Hasil Terkini (Real-Time)</h3>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.8rem', lineHeight: '1.4' }}>
                    Ambil data total akumulasi jam telat (TTWM) & cepat pulang (TTWP) langsung dari server SPOT secara real-time untuk membandingkan sebelum dan sesudah perbaikan.
                  </p>
                  
                  <button 
                    className="btn btn-outline" 
                    style={{ width: '100%', justifyContent: 'center', marginBottom: '0.75rem' }} 
                    onClick={() => handleVerifyOpdRealtime(selectedProblem)} 
                    disabled={verificationLoading}
                  >
                    {verificationLoading ? (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <div className="spinner-mini"></div>
                        Menghubungkan SPOT...
                      </div>
                    ) : '🔄 Verifikasi TTWM & TTWP Terbaru'}
                  </button>
                  
                  {verificationError && (
                    <div className="error-box" style={{ fontSize: '0.75rem' }}>
                      ❌ {verificationError}
                    </div>
                  )}
                  
                  {verificationData && (
                    <div style={{ background: 'rgba(2, 6, 23, 0.3)', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border)', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                      <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#fff', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '0.3rem', display: 'flex', justifyContent: 'space-between' }}>
                        <span>Parameter</span>
                        <span>Sebelum</span>
                        <span style={{ color: 'var(--success)' }}>Sesudah (SPOT)</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
                        <span style={{ color: 'var(--text-muted)' }}>Lambat (TTWM)</span>
                        <span style={{ textDecoration: 'line-through', opacity: 0.7 }}>{selectedProblem.TTWM}</span>
                        <strong style={{ color: (verificationData.ttwm === '00:00:00' || verificationData.ttwm === '0' || verificationData.ttwm === '') ? 'var(--success)' : '#fff' }}>{verificationData.ttwm || '00:00:00'}</strong>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
                        <span style={{ color: 'var(--text-muted)' }}>Cepat (TTWP)</span>
                        <span style={{ textDecoration: 'line-through', opacity: 0.7 }}>{selectedProblem.TTWP}</span>
                        <strong style={{ color: (verificationData.ttwp === '00:00:00' || verificationData.ttwp === '0' || verificationData.ttwp === '') ? 'var(--success)' : '#fff' }}>{verificationData.ttwp || '00:00:00'}</strong>
                      </div>
                    </div>
                  )}
                </div>

                {monthlyResolvingResults.length > 0 && (
                  <div style={{ background: 'rgba(15, 23, 42, 0.2)', border: '1px solid var(--border)', borderRadius: '12px', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    <h4 style={{ fontSize: '0.8rem', fontWeight: 700, color: '#fff', borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '0.4rem' }}>📊 Log Perbaikan Harian</h4>
                    <div style={{ maxHeight: '200px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                      {monthlyResolvingResults.map((r, idx) => (
                        <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', background: 'rgba(255,255,255,0.02)', padding: '0.35rem 0.5rem', borderRadius: '6px' }}>
                          <span>Tanggal {r.day}</span>
                          <span style={{ 
                            color: r.status === 'success' ? 'var(--success)' : 
                                   (r.status === 'review_manual' ? 'var(--warning)' : 'var(--danger)'),
                            fontWeight: 600
                          }}>
                            {r.status === 'success' ? `✅ Shift ${r.detected_shift}` : 
                             (r.status === 'review_manual' ? '⚠️ Check' : '❌ Gagal')}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      <ProcessStatus status={processStatus} error={lastError} onRetry={resetStatus} />

    </div>
  );
};




export default App;
