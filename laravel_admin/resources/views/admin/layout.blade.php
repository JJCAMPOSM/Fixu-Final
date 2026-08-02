<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fixu Admin</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #6366f1;
            --primary-hover: #4f46e5;
            --danger: #ef4444;
            --success: #10b981;
            
            /* Light mode defaults */
            --bg-body: #f8fafc;
            --bg-surface: rgba(255, 255, 255, 0.9);
            --bg-card: #ffffff;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --border: rgba(0, 0, 0, 0.1);
            --table-hover: rgba(0, 0, 0, 0.02);
            --gradient-circles: radial-gradient(circle at 15% 50%, rgba(99, 102, 241, 0.08), transparent 25%), radial-gradient(circle at 85% 30%, rgba(16, 185, 129, 0.05), transparent 25%);
            --input-bg: rgba(0, 0, 0, 0.03);
        }

        [data-theme="dark"] {
            /* Dark mode */
            --bg-body: #0f172a;
            --bg-surface: rgba(30, 41, 59, 0.7);
            --bg-card: rgba(30, 41, 59, 0.9);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border: rgba(255, 255, 255, 0.1);
            --table-hover: rgba(255, 255, 255, 0.02);
            --gradient-circles: radial-gradient(circle at 15% 50%, rgba(99, 102, 241, 0.15), transparent 25%), radial-gradient(circle at 85% 30%, rgba(16, 185, 129, 0.1), transparent 25%);
            --input-bg: rgba(15, 23, 42, 0.6);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-body);
            color: var(--text-main);
            display: flex;
            min-height: 100vh;
            background-image: var(--gradient-circles);
            transition: background-color 0.3s, color 0.3s;
        }

        /* Sidebar */
        .sidebar {
            width: 260px;
            height: 100vh;
            position: sticky;
            top: 0;
            overflow-y: auto;
            background: var(--bg-surface);
            backdrop-filter: blur(12px);
            border-right: 1px solid var(--border);
            padding: 2rem 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 2rem;
            flex-shrink: 0;
        }

        .sidebar-spacer {
            flex: 1;
        }

        .brand {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .nav-links {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .nav-link {
            display: block;
            text-decoration: none;
            color: var(--text-muted);
            padding: 0.75rem 1rem;
            border-radius: 8px;
            transition: all 0.2s ease;
            font-weight: 500;
        }

        .nav-link:hover, .nav-link.active {
            background: rgba(99, 102, 241, 0.1);
            color: var(--primary);
        }

        .btn-logout {
            display: block;
            width: 100%;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            border: 1px solid rgba(239, 68, 68, 0.3);
            background: transparent;
            color: var(--danger);
            font-family: inherit;
            font-weight: 500;
            cursor: pointer;
            text-align: center;
            text-decoration: none;
            transition: all 0.2s ease;
            margin-top: auto;
        }

        .btn-logout:hover {
            background: rgba(239, 68, 68, 0.1);
        }

        /* Main Content */
        .main-content {
            flex: 1;
            padding: 3rem;
            overflow-y: auto;
            position: relative;
        }

        .header {
            margin-bottom: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .header h1 {
            font-weight: 600;
            font-size: 1.8rem;
        }

        /* Cards & Glassmorphism */
        .card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            backdrop-filter: blur(8px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            animation: fadeIn 0.4s ease-out;
        }

        /* Forms & Inputs */
        .form-group {
            margin-bottom: 1.25rem;
        }
        
        label {
            display: block;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
            color: var(--text-muted);
        }

        input, select, textarea {
            width: 100%;
            padding: 0.75rem;
            background: var(--input-bg);
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text-main);
            font-family: inherit;
            transition: border-color 0.2s;
        }

        input:focus {
            outline: none;
            border-color: var(--primary);
        }

        /* Buttons */
        .btn {
            display: inline-block;
            padding: 0.6rem 1.2rem;
            border-radius: 6px;
            border: none;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            text-decoration: none;
        }

        .btn-primary {
            background: var(--primary);
            color: white;
            box-shadow: 0 0 15px rgba(99, 102, 241, 0.4);
        }

        .btn-primary:hover {
            background: var(--primary-hover);
            transform: translateY(-1px);
        }

        .btn-danger {
            background: rgba(239, 68, 68, 0.1);
            color: var(--danger);
            border: 1px solid rgba(239, 68, 68, 0.2);
        }

        .btn-danger:hover {
            background: var(--danger);
            color: white;
        }

        /* Tables */
        .table-container {
            overflow-x: auto;
            margin-top: 1.5rem;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th, td {
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }

        th {
            color: var(--text-muted);
            font-weight: 500;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        tr:hover td {
            background: var(--table-hover);
        }

        /* Mobile & Theme Adjustments */
        .mobile-header {
            display: none;
            padding: 1rem 1.5rem;
            background: var(--bg-surface);
            border-bottom: 1px solid var(--border);
            justify-content: space-between;
            align-items: center;
            backdrop-filter: blur(12px);
            z-index: 40;
        }
        
        button.icon-btn {
            background: none;
            border: none;
            color: var(--text-main);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0.5rem;
        }

        .dark-icon { display: none; }
        [data-theme="dark"] .dark-icon { display: block; }
        [data-theme="dark"] .light-icon { display: none; }

        @media (max-width: 768px) {
            body { flex-direction: column; }
            .sidebar {
                position: fixed;
                top: 0; left: 0;
                height: 100vh;
                z-index: 50;
                transform: translateX(-100%);
                transition: transform 0.3s;
            }
            .sidebar.show { transform: translateX(0); }
            .mobile-header { display: flex; }
            .main-content { padding: 1.5rem; width: 100%; }
            .header { flex-direction: column; align-items: flex-start; gap: 1rem; }
            .top-right { display: none !important; }
        }

        /* Desktop Header top right */
        .top-right {
            position: absolute;
            top: 1.5rem;
            right: 1.5rem;
            z-index: 10;
        }

        /* Alerts */
        .alert {
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
            animation: slideIn 0.3s ease-out;
        }

        .alert-success {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.2);
            color: var(--success);
        }

        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes slideIn {
            from { opacity: 0; transform: translateX(20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        .flex { display: flex; }
        .gap-4 { gap: 1rem; }
        .justify-between { justify-content: space-between; }
        .items-center { align-items: center; }
        .mt-4 { margin-top: 1rem; }
        .mb-4 { margin-bottom: 1rem; }
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
    </style>
</head>
<body>

    <script>
        // Init theme immediately to prevent FOUC
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
    </script>
    
    <div class="mobile-header">
        <div class="brand">
            <img src="{{ asset('img/logo.png') }}" alt="Fixu" style="height: 32px; object-fit: contain;">
            <span style="font-size: 1.1rem; color: var(--text-muted); font-weight: 500;">Admin</span>
        </div>
        <div class="flex items-center gap-4">
            <button class="icon-btn theme-toggle" onclick="toggleTheme()" title="Cambiar Tema">
                <svg class="light-icon" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
                <svg class="dark-icon" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
            </button>
            <button class="icon-btn menu-toggle" onclick="toggleSidebar()">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
            </button>
        </div>
    </div>

    <aside class="sidebar" id="sidebar">
        <div class="brand" style="gap: 0.6rem; margin-bottom: 2rem;">
            <img src="{{ asset('img/logo.png') }}" alt="Fixu" style="height: 38px; object-fit: contain;">
            <span style="font-size: 1.2rem; color: var(--text-muted); font-weight: 500; align-self: flex-end; padding-bottom: 3px;">Admin</span>
        </div>
        <ul class="nav-links" style="padding-top: 1rem;">
            <li><a href="{{ route('admin.dashboard') }}" class="nav-link {{ request()->routeIs('admin.dashboard') ? 'active' : '' }}">Dashboard</a></li>
            <li><a href="{{ route('admin.tickets.index') }}" class="nav-link {{ request()->routeIs('admin.tickets.*') ? 'active' : '' }}">Tickets</a></li>
            <li><a href="{{ route('admin.teams.index') }}" class="nav-link {{ request()->routeIs('admin.teams.*') ? 'active' : '' }}">Equipos</a></li>
            <li><a href="{{ route('admin.categories.index') }}" class="nav-link {{ request()->routeIs('admin.categories.*') ? 'active' : '' }}">Categorías</a></li>
            <li><a href="{{ route('admin.requesters.index') }}" class="nav-link {{ request()->routeIs('admin.requesters.*') ? 'active' : '' }}">Solicitantes</a></li>
            <li><a href="{{ route('admin.agents.index') }}" class="nav-link {{ request()->routeIs('admin.agents.*') ? 'active' : '' }}">Agentes</a></li>
        </ul>
        <div class="sidebar-spacer"></div>
        <div style="padding-top: 1rem; border-top: 1px solid rgba(100,116,139,0.3);">
            <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 0.75rem; padding: 0 0.5rem;">
                Admin (admin)
            </div>
            <a href="/auth/logout"
               style="display: block; width: 100%; padding: 0.65rem 1rem; border-radius: 8px;
                      border: 1px solid rgba(239,68,68,0.4); background: transparent;
                      color: #ef4444; font-family: inherit; font-weight: 500; cursor: pointer;
                      text-align: center; text-decoration: none; font-size: 0.95rem;
                      transition: background 0.2s;"
               onmouseover="this.style.background='rgba(239,68,68,0.1)'"
               onmouseout="this.style.background='transparent'">
                Cerrar sesión
            </a>
        </div>
    </aside>

    <main class="main-content">
        <!-- Desktop Theme Toggle -->
        <div class="top-right">
            <button class="icon-btn theme-toggle" onclick="toggleTheme()" title="Cambiar Tema">
                <svg class="light-icon" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
                <svg class="dark-icon" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
            </button>
        </div>

        @if(session('success'))
            <div class="alert alert-success">
                {{ session('success') }}
            </div>
        @endif
        @if(session('error'))
            <div class="alert alert-danger" style="background: rgba(239, 68, 68, 0.1); color: var(--danger); border: 1px solid rgba(239, 68, 68, 0.2);">
                {{ session('error') }}
            </div>
        @endif

        @yield('content')
    </main>

    <script>
        function toggleTheme() {
            const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            // Si hay alguna gráfica instalada de chart.js, necesitamos notificarle su nuevo color de borde
            if (typeof Chart !== 'undefined') {
                Chart.defaults.color = newTheme === 'light' ? '#64748b' : '#94a3b8';
                Object.values(Chart.instances).forEach(function(chart) {
                    if(chart.options.scales.y) {
                        chart.options.scales.y.grid.color = newTheme === 'light' ? 'rgba(0,0,0,0.05)' : 'rgba(255,255,255,0.05)';
                    }
                    chart.update();
                });
            }
        }

        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('show');
        }
    </script>

</body>
</html>
