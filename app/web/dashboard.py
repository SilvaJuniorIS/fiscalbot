from fastapi.responses import HTMLResponse


def render_dashboard_page() -> HTMLResponse:
    html = """<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>FiscalBot Dashboard</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f6f7f9;
      --panel: #ffffff;
      --ink: #1d2430;
      --muted: #6d7480;
      --line: #dfe3e8;
      --accent: #0f766e;
      --accent-2: #1d4ed8;
      --warn: #b45309;
      --danger: #b91c1c;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    * { box-sizing: border-box; }
    body { margin: 0; background: var(--bg); color: var(--ink); }
    header {
      background: #102026;
      color: #fff;
      border-bottom: 4px solid var(--accent);
    }
    .wrap { width: min(1180px, calc(100% - 32px)); margin: 0 auto; }
    .topbar {
      min-height: 86px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
    }
    h1 { margin: 0; font-size: 26px; letter-spacing: 0; }
    .subtitle { margin: 6px 0 0; color: #cbd5e1; font-size: 14px; }
    .actions { display: flex; flex-wrap: wrap; gap: 10px; }
    .button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 38px;
      padding: 0 14px;
      border: 1px solid rgba(255,255,255,.22);
      color: #fff;
      text-decoration: none;
      border-radius: 6px;
      font-weight: 650;
      font-size: 14px;
    }
    main { padding: 28px 0 42px; }
    .status {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      margin-bottom: 18px;
      color: var(--muted);
      font-size: 14px;
    }
    .pill {
      display: inline-flex;
      align-items: center;
      min-height: 28px;
      padding: 0 10px;
      border-radius: 999px;
      background: #e8f5f3;
      color: #115e59;
      font-weight: 700;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
    }
    .card, .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: 0 1px 2px rgba(16, 24, 40, .04);
    }
    .card { padding: 16px; min-height: 118px; }
    .label { color: var(--muted); font-size: 13px; font-weight: 700; }
    .value { margin-top: 12px; font-size: 30px; font-weight: 800; letter-spacing: 0; }
    .hint { margin-top: 8px; color: var(--muted); font-size: 13px; }
    .danger { color: var(--danger); }
    .warn { color: var(--warn); }
    .accent { color: var(--accent); }
    .columns {
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(0, 1.35fr);
      gap: 14px;
      margin-top: 14px;
    }
    .panel { padding: 18px; }
    h2 { margin: 0 0 14px; font-size: 18px; }
    .bar-row {
      display: grid;
      grid-template-columns: 150px 1fr 42px;
      align-items: center;
      gap: 10px;
      margin: 12px 0;
      font-size: 14px;
    }
    .bar-track { height: 12px; background: #edf0f3; border-radius: 999px; overflow: hidden; }
    .bar-fill { height: 100%; background: var(--accent-2); border-radius: 999px; }
    table { width: 100%; border-collapse: collapse; font-size: 14px; }
    th, td { padding: 12px 10px; border-bottom: 1px solid var(--line); text-align: left; }
    th { color: var(--muted); font-size: 12px; text-transform: uppercase; }
    .empty { color: var(--muted); padding: 22px 0; }
    footer { color: var(--muted); font-size: 13px; padding: 8px 0 24px; }
    @media (max-width: 920px) {
      .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .columns { grid-template-columns: 1fr; }
      .topbar { align-items: flex-start; flex-direction: column; padding: 18px 0; }
    }
    @media (max-width: 560px) {
      .wrap { width: min(100% - 20px, 1180px); }
      .grid { grid-template-columns: 1fr; }
      .status { align-items: flex-start; flex-direction: column; }
      .bar-row { grid-template-columns: 104px 1fr 34px; }
      .value { font-size: 26px; }
      th:nth-child(2), td:nth-child(2) { display: none; }
    }
  </style>
</head>
<body>
  <header>
    <div class="wrap topbar">
      <div>
        <h1>FiscalBot</h1>
        <p class="subtitle">Painel executivo de contratos, prazos e riscos de fiscalizacao</p>
      </div>
      <nav class="actions" aria-label="Acoes">
        <a class="button" href="/docs">API</a>
        <a class="button" href="/api/v1/dashboard">Dados</a>
        <a class="button" href="/health">Status</a>
      </nav>
    </div>
  </header>
  <main class="wrap">
    <section class="status">
      <span id="status-text">Carregando indicadores...</span>
      <span class="pill" id="mode">conectando</span>
    </section>
    <section class="grid" id="cards"></section>
    <section class="columns">
      <div class="panel">
        <h2>Contratos por secretaria</h2>
        <div id="secretarias"></div>
      </div>
      <div class="panel">
        <h2>Proximos vencimentos</h2>
        <div id="vencimentos"></div>
      </div>
    </section>
  </main>
  <footer class="wrap">FiscalBot MVP - Sprint 2 operacional</footer>
  <script>
    const labels = {
      total_contratos: ["Contratos cadastrados", "Base total em acompanhamento"],
      contratos_ativos: ["Contratos ativos", "Execucao ou vigencia em aberto"],
      vencendo_30_dias: ["Vencendo em 30 dias", "Prioridade maxima"],
      vencendo_90_dias: ["Vencendo em 90 dias", "Janela de planejamento"],
      valor_total: ["Valor contratado", "Soma dos contratos"],
      alertas_pendentes: ["Alertas pendentes", "Acoes aguardando tratamento"],
      ocorrencias_abertas: ["Ocorrencias abertas", "Fiscalizacao operacional"],
      fornecedores: ["Fornecedores", "Cadastro ativo"]
    };

    const formatNumber = new Intl.NumberFormat("pt-BR");
    const formatMoney = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });
    const formatDate = (value) => new Date(value + "T00:00:00").toLocaleDateString("pt-BR");

    function renderCards(cards) {
      const order = [
        "total_contratos", "contratos_ativos", "vencendo_30_dias", "vencendo_90_dias",
        "valor_total", "alertas_pendentes", "ocorrencias_abertas", "fornecedores"
      ];
      document.querySelector("#cards").innerHTML = order.map((key) => {
        const [title, hint] = labels[key];
        const raw = cards[key] ?? 0;
        const value = key === "valor_total" ? formatMoney.format(raw) : formatNumber.format(raw);
        const tone = key.includes("30") || key.includes("pendentes") ? "danger" :
          key.includes("90") || key.includes("abertas") ? "warn" : "accent";
        return `<article class="card">
          <div class="label">${title}</div>
          <div class="value ${tone}">${value}</div>
          <div class="hint">${hint}</div>
        </article>`;
      }).join("");
    }

    function renderSecretarias(rows) {
      if (!rows.length) {
        document.querySelector("#secretarias").innerHTML = '<div class="empty">Sem contratos por secretaria.</div>';
        return;
      }
      const max = Math.max(...rows.map((row) => row.contratos), 1);
      document.querySelector("#secretarias").innerHTML = rows.map((row) => {
        const width = Math.max(6, Math.round((row.contratos / max) * 100));
        return `<div class="bar-row">
          <span>${row.secretaria}</span>
          <div class="bar-track"><div class="bar-fill" style="width:${width}%"></div></div>
          <strong>${row.contratos}</strong>
        </div>`;
      }).join("");
    }

    function renderVencimentos(rows) {
      if (!rows.length) {
        document.querySelector("#vencimentos").innerHTML = '<div class="empty">Nenhum vencimento futuro encontrado.</div>';
        return;
      }
      document.querySelector("#vencimentos").innerHTML = `<table>
        <thead><tr><th>Contrato</th><th>Objeto</th><th>Termino</th><th>Status</th></tr></thead>
        <tbody>${rows.map((row) => `<tr>
          <td>${row.numero}</td>
          <td>${row.objeto}</td>
          <td>${formatDate(row.termino)}</td>
          <td>${row.status}</td>
        </tr>`).join("")}</tbody>
      </table>`;
    }

    async function loadDashboard() {
      try {
        const response = await fetch("/api/v1/dashboard");
        const data = await response.json();
        renderCards(data.cards);
        renderSecretarias(data.por_secretaria);
        renderVencimentos(data.proximos_vencimentos);
        document.querySelector("#mode").textContent = data.mode === "live" ? "dados reais" : "modo demonstracao";
        document.querySelector("#status-text").textContent = `Atualizado em ${formatDate(data.generated_at)}`;
      } catch (error) {
        document.querySelector("#status-text").textContent = "Nao foi possivel carregar os indicadores.";
        document.querySelector("#mode").textContent = "offline";
      }
    }

    loadDashboard();
  </script>
</body>
</html>"""
    return HTMLResponse(content=html)

