const state = { user: null, lastTraceId: null, lastQuestion: "Score the bid for SOC monitoring and transition risk.", currentFiles: [], chatFiles: [] };
const navGroups = [
  ["DASHBOARD", ["Dashboard"]],
  ["OPPORTUNITIES", ["Opportunities", "Capture Pipeline"]],
  ["KNOWLEDGE & CONTENT", ["Documents", "Past Performance", "Content Library", "Templates", "Win Themes"]],
  ["ANALYSIS", ["Compliance Matrix", "Bid / No-Bid", "AI Assistant", "Eval / Trace", "Verification"]],
  ["WORKFLOW", ["Proposal Workspace", "Traceability", "Tasks", "Approvals", "Reviews", "Health Dashboard"]],
  ["ADMIN", ["Users & Roles", "Data Sources", "Audit Logs", "System Settings"]],
];
const view = document.getElementById("view");
const crumb = document.getElementById("crumb");

async function api(path, options = {}) {
  const res = await fetch(path, options);
  if (!res.ok) throw new Error(`${path} -> ${res.status}`);
  return res.json();
}

document.getElementById("login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  state.user = await api("/api/session/login", { method: "POST" });
  await api("/api/bootstrap", { method: "POST" });
  document.getElementById("login").classList.add("hidden");
  document.getElementById("app").classList.remove("hidden");
  renderNav("Dashboard");
  renderDashboard();
});

function renderNav(active) {
  const nav = document.getElementById("nav");
  nav.innerHTML = "";
  for (const [group, items] of navGroups) {
    const label = document.createElement("div");
    label.className = "nav-section";
    label.textContent = group;
    nav.appendChild(label);
    for (const item of items) {
      const node = document.createElement("div");
      node.className = `nav-item ${item === active ? "active" : ""}`;
      node.innerHTML = `<span class="nav-dot"></span><span>${item}</span>`;
      node.onclick = () => route(item);
      nav.appendChild(node);
    }
  }
}

function setPage(active, breadcrumb) {
  renderNav(active);
  crumb.textContent = breadcrumb;
}

function route(item) {
  if (item === "Dashboard") renderDashboard();
  else if (item === "Documents") renderDocuments();
  else if (item === "AI Assistant") renderAssistant();
  else if (item === "Bid / No-Bid") renderBid();
  else if (item === "Compliance Matrix") renderCompliance();
  else if (item === "Traceability") renderTraceability();
  else if (item === "Proposal Workspace") renderProposalWorkspace();
  else if (item === "Content Library") renderContentLibrary();
  else if (item === "Reviews") renderReviews();
  else if (item === "Health Dashboard") renderHealthDashboard();
  else if (item === "Audit Logs") renderAudit();
  else if (item === "Eval / Trace") renderTrace();
  else if (item === "Verification") renderVerification();
  else view.innerHTML = `<section class="page"><h2>${item}</h2><p class="sub">This screen is reserved for the production module.</p></section>`;
  setPage(item, `${item.includes("/") ? "Analysis" : "Home"} / ${item}`);
}

async function renderDashboard() {
  setPage("Dashboard", "Home / Dashboard");
  const review = await api("/api/review");
  view.innerHTML = `<section class="page">
    <div class="top-actions"><div><h2>Good morning, Adam</h2><p class="sub">Here's your capture pipeline at a glance.</p></div><button class="btn" onclick="route('Documents')">+ New Opportunity</button></div>
    <div class="grid cards">
      ${metric("ACTIVE OPPORTUNITIES", "12", "+3 this week")}
      ${metric("BID / NO-BID PENDING", "5", "2 due soon", "warn")}
      ${metric("COMPLIANCE RISKS", "7", "3 high", "bad")}
      ${metric("HUMAN REVIEW QUEUE", review.review_queue.length, "awaiting you")}
      ${metric("WIN RATE (TTM)", "41%", "+6% YoY", "good")}
    </div>
    <div class="grid three">
      <div class="panel"><h3>Human Review Queue</h3>${review.review_queue.map(r => `<div class="row"><div><strong>${r.title || r.id}</strong><br><span class="small-note">${r.reason || "needs review"}</span></div><span>›</span></div>`).join("")}</div>
      <div class="panel"><h3>Upcoming Deadlines</h3>${["DHS Cyber Modernization|2d left", "GSA MAS Refresh|8d left", "VA SOC Support|16d left", "Navy Cloud IDIQ|23d left"].map(x => {const [a,b]=x.split("|");return `<div class="row"><strong>${a}</strong><span class="pill warn">${b}</span></div>`}).join("")}</div>
      <div class="panel"><h3>Pipeline by Stage</h3><div class="bars">${["90","55","38","25","16"].map(w=>`<span><b style="width:${w}%"></b></span>`).join("")}</div><hr><p class="sub">Recent AI Activity</p><ul><li>Compliance matrix generated</li><li>Bid score 78</li><li>Guardrail blocked payroll query</li><li>Embedded document chunks</li></ul></div>
    </div>
  </section>`;
}

function metric(label, value, sub, color = "blue") {
  return `<div class="card metric"><span class="small-note">${label}</span><strong>${value}</strong><small class="${color}">${sub}</small></div>`;
}

async function renderDocuments() {
  setPage("Documents", "Documents / Add Document");
  const docs = await api("/api/documents");
  view.innerHTML = `<section class="page">
    <div class="panel"><div class="row"><strong>1 Upload File</strong><strong>2 Document Details</strong><span>3 Classification & Metadata</span><span>4 Review & Ingest</span></div></div>
    <div class="grid upload-grid">
      <div class="panel"><h3>Attach Documents & Images</h3><div class="drop" id="drop-zone"><input id="file" type="file" multiple accept=".txt,.md,.csv,.json,.pdf,.doc,.docx,image/png,image/jpeg,image/webp,image/tiff" /><p>Click Browse Files or drag PDFs, Word docs, text files, screenshots, and images here.</p><p class="small-note">Local build: images/PDFs use labeled OCR/extraction simulation. Production: Textract/OCR + malware/DLP scan.</p></div><div id="attachment-list" class="attachments"><p>No attachments selected.</p></div><pre id="upload-preview" class="code">No upload yet.</pre></div>
      <div class="panel form"><h3>Document Details</h3><label>Document Title<input id="doc-title" value="DHS Cybersecurity Modernization RFP"></label><label>Description<textarea>Solicitation for cybersecurity modernization support services.</textarea></label><label>Source File Name<input id="source-name" disabled value="No file attached yet"></label></div>
      <div class="panel form"><h3>Classification</h3><label>Document Type<select><option>RFP / Solicitation</option></select></label><label>Security Classification<select id="classification"><option value="cui">Controlled Unclassified (CUI)</option><option value="internal">Internal</option></select></label><label><input type="checkbox" checked> Allow for AI Retrieval</label><p><span class="pill blue">Proposal_Team</span> <span class="pill blue">Capture_Team</span></p></div>
      <div class="panel steps"><h3>What happens next</h3>${["Text extracted", "Document security scan", "Layered chunking", "Embeddings generated", "Metadata stored", "Available for RAG retrieval"].map((s,i)=>`<div class="step"><span class="check">${i<3?"✓":""}</span>${s}</div>`).join("")}<button class="btn" id="ingest">Review & Ingest -></button></div>
    </div>
    <div class="panel"><div class="top-actions"><h3>Document Inventory</h3><button class="btn" onclick="route('Documents')">+ Add Document</button></div><div id="doc-table">${docTable(docs.documents)}</div></div>
  </section>`;
  const dropZone = document.getElementById("drop-zone");
  document.getElementById("file").onchange = async (event) => {
    setAttachments(event.target.files);
  };
  dropZone.ondragover = (event) => {
    event.preventDefault();
    dropZone.classList.add("dragging");
  };
  dropZone.ondragleave = () => dropZone.classList.remove("dragging");
  dropZone.ondrop = (event) => {
    event.preventDefault();
    dropZone.classList.remove("dragging");
    setAttachments(event.dataTransfer.files);
  };
  document.getElementById("ingest").onclick = uploadCurrentDocument;
}

function docTable(docs) {
  return `<table><thead><tr><th>DOC ID</th><th>TITLE</th><th>FILE</th><th>KIND</th><th>EXTRACTION</th><th>STATUS</th><th>EMBEDDED</th></tr></thead><tbody>${docs.map(d=>`<tr><td><a>${d.document_id}</a></td><td>${d.title}</td><td>${d.filename || "uploaded"}</td><td>${d.attachment_kind || "text"}</td><td>${d.extraction_mode || "direct_text_decode"}</td><td><span class="pill good">${d.status}</span></td><td>${d.chunk_count} chunks</td></tr>`).join("")}</tbody></table>`;
}

function setAttachments(fileList) {
  state.currentFiles = Array.from(fileList || []);
  const list = document.getElementById("attachment-list");
  const sourceName = document.getElementById("source-name");
  if (!state.currentFiles.length) {
    list.innerHTML = "<p>No attachments selected.</p>";
    sourceName.value = "No file attached yet";
    document.getElementById("upload-preview").textContent = "No upload yet.";
    return;
  }
  sourceName.value = state.currentFiles.map(file => file.name).join(", ");
  list.innerHTML = state.currentFiles.map(file => {
    const kind = file.type.startsWith("image/") ? "Image/OCR" : file.name.toLowerCase().endsWith(".pdf") ? "PDF" : file.name.toLowerCase().endsWith(".docx") ? "Word doc" : "Document";
    return `<div class="attachment-row"><span>${file.name}</span><span class="pill blue">${kind}</span><small>${Math.ceil(file.size / 1024)} KB</small></div>`;
  }).join("");
  document.getElementById("upload-preview").textContent = `${state.currentFiles.length} attachment(s) ready. Click Review & Ingest.`;
}

async function uploadCurrentDocument() {
  const text = `1.1 Purpose\nThe purpose of this solicitation is cybersecurity modernization.\n3.1 Technical Approach\nThe contractor shall provide 24/7 SOC monitoring services.\nM.1 Evaluation\nTechnical approach is weighted 40 percent. Past performance is weighted 30 percent.`;
  const files = state.currentFiles.length ? state.currentFiles : [new File([text], "DHS_Cyber_Mod_RFP.txt", { type: "text/plain" })];
  const form = new FormData();
  for (const file of files) form.append("files", file);
  form.append("title", document.getElementById("doc-title").value);
  form.append("classification", document.getElementById("classification").value);
  const result = await api("/api/upload", { method: "POST", body: form });
  document.getElementById("upload-preview").textContent = JSON.stringify(result, null, 2);
  const docs = await api("/api/documents");
  document.getElementById("doc-table").innerHTML = docTable(docs.documents);
}

async function renderAssistant() {
  setPage("AI Assistant", "Analysis / AI Assistant");
  view.innerHTML = `<section class="page"><div class="grid two">
    <div class="panel chat"><div><span class="small-note">Opportunity:</span> <span class="pill blue">DHS Cyber Modernization</span></div><div id="chat-body"><div class="bubble question">Find past proposal language for cybersecurity SOC modernization.</div><div class="bubble">Ask a question to run query guard, hybrid retrieval, RRF, reranker, context builder, Claude Sonnet Bedrock mock, output guard, citations, RAGAS score, and Phoenix trace.</div></div><div class="chat-attach"><label class="attach-label">Attach evidence to this question<input id="chat-files" type="file" multiple accept=".txt,.md,.csv,.json,.pdf,.doc,.docx,image/png,image/jpeg,image/webp,image/tiff"></label><div id="chat-file-list" class="attachments"><p>No chat attachments.</p></div></div><div class="row"><input id="question" value="Find past proposal language for cybersecurity SOC modernization." /><button class="btn" id="ask">Ask</button></div></div>
    <div class="panel"><h3>Retrieved Context</h3><p class="sub">Role-filtered · RRF fused · reranked top 4</p><div id="context"></div><hr><h3>Phoenix trace</h3><div class="tracebar"><i></i><i></i><i></i><i></i></div><pre id="trace" class="code">Waiting for ask...</pre></div>
  </div></section>`;
  document.getElementById("chat-files").onchange = (event) => {
    state.chatFiles = Array.from(event.target.files || []);
    document.getElementById("chat-file-list").innerHTML = state.chatFiles.length
      ? state.chatFiles.map(file => `<div class="attachment-row"><span>${file.name}</span><span class="pill blue">${file.type.startsWith("image/") ? "Image/OCR" : "Document"}</span><small>${Math.ceil(file.size / 1024)} KB</small></div>`).join("")
      : "<p>No chat attachments.</p>";
  };
  document.getElementById("ask").onclick = askQuestion;
}

async function askQuestion() {
  const question = document.getElementById("question").value;
  state.lastQuestion = question;
  let packet;
  if (state.chatFiles.length) {
    const form = new FormData();
    form.append("question", question);
    for (const file of state.chatFiles) form.append("files", file);
    packet = await api("/api/chat/attach-ask", { method: "POST", body: form });
  } else {
    packet = await api("/api/ask", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({ question }) });
  }
  if (packet.blocked) {
    document.getElementById("chat-body").insertAdjacentHTML("beforeend", `<div class="bubble guard">Blocked by guardrails: ${packet.guard.reason}</div>`);
    document.getElementById("trace").textContent = JSON.stringify(packet.trace, null, 2);
    return;
  }
  state.lastTraceId = packet.trace.trace_id;
  const attachmentProof = packet.chat_attachments?.length
    ? `<p><strong>Chat attachment workflows:</strong> ${packet.chat_attachments.map(a=>`<span class="pill ${a.workflow_status === "stored" ? "good" : "bad"}">${a.workflow_status} ${a.workflow_id?.slice(0,8) || ""}</span>`).join(" ")}</p>`
    : "";
  document.getElementById("chat-body").insertAdjacentHTML("beforeend", `<div class="bubble"><strong>BidIntel Assistant</strong><p>${packet.answer}</p>${attachmentProof}<p><strong>Sources:</strong> ${packet.citations.map(c=>`<span class="pill blue">${c.document} ${c.section}</span>`).join(" ")}</p><div class="bars"><span><b style="width:${packet.eval.faithfulness*100}%"></b></span><span><b style="width:${packet.eval.answer_relevance*100}%"></b></span><span><b style="width:${packet.eval.context_precision*100}%"></b></span></div></div>`);
  document.getElementById("context").innerHTML = packet.retrieved_context.map(c => `<div class="context-card"><strong>${c.document_title} ${c.section}</strong><span class="pill good">${c.rerank_score}</span><p>${c.text.slice(0, 120)}...</p></div>`).join("");
  document.getElementById("trace").textContent = JSON.stringify(packet.trace, null, 2);
}

async function renderBid() {
  setPage("Bid / No-Bid", "Analysis / Bid / No-Bid");
  const bid = await api("/api/bid-score");
  view.innerHTML = `<section class="page">
    <div class="panel"><h2>DHS Cybersecurity Modernization Support</h2><p class="sub">Solicitation HSEC-24-RFP-0421 · GSA MAS · Est. $50M</p></div>
    <div class="panel"><h3>Score From RAG Evidence</h3><p class="sub">This uses the same retrieval pipeline as the assistant: BM25 + pgvector + RRF + reranker, then scores the bid from retrieved evidence.</p><div class="row"><input id="score-question" value="${state.lastQuestion}" /><button class="btn" id="score-from-rag">Score From RAG Evidence</button></div><pre id="rag-score-proof" class="code">Click the button to prove the score is tied to retrieved chunks.</pre></div>
    <div class="grid two"><div class="panel gauge"><span>STATIC BASELINE SCORE</span><strong>${bid.score}</strong><p>out of 100</p><span class="pill good">RECOMMENDATION: ${bid.recommendation}</span><p>Win probability ${bid.win_probability}% · Confidence ${bid.confidence}</p></div><div class="panel"><h3>Weighted Score Breakdown</h3>${Object.entries(bid.factors).map(([k,v])=>`<div class="factor"><span>${k.replaceAll("_"," ")}</span><div class="track"><div class="fill" style="width:${v}%"></div></div><strong>${v}</strong></div>`).join("")}</div></div>
    <div id="rag-score-view"></div>
    <div class="grid three"><div class="panel"><h3>Key Risks</h3><ul>${bid.risks.map(x=>`<li>${x}</li>`).join("")}</ul></div><div class="panel"><h3>Missing Info</h3><ul><li>Updated DHS past performance</li><li>Confirmed pricing from finance</li><li>Teaming partner LOIs</li></ul></div><div class="panel"><h3>Next Steps</h3><ul>${bid.next_steps.map(x=>`<li>${x}</li>`).join("")}</ul></div></div>
  </section>`;
  document.getElementById("score-from-rag").onclick = scoreBidFromRag;
}

async function scoreBidFromRag() {
  const question = document.getElementById("score-question").value;
  state.lastQuestion = question;
  const packet = await api("/api/bid-score/from-rag", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({ question }) });
  const bid = packet.score;
  document.getElementById("rag-score-proof").textContent = JSON.stringify({ retrieval: packet.retrieval, proof: bid.proof, evidence_used: bid.evidence_used }, null, 2);
  document.getElementById("rag-score-view").innerHTML = `<div class="grid two"><div class="panel gauge"><span>RAG-GROUNDED SCORE</span><strong>${bid.score}</strong><p>out of 100</p><span class="pill good">RECOMMENDATION: ${bid.recommendation}</span><p>Win probability ${bid.win_probability}% · Confidence ${bid.confidence}</p></div><div class="panel"><h3>Evidence-Based Breakdown</h3>${Object.entries(bid.factors).map(([k,v])=>`<div class="factor"><span>${k.replaceAll("_"," ")}</span><div class="track"><div class="fill" style="width:${v}%"></div></div><strong>${v}</strong></div>`).join("")}</div></div><div class="panel"><h3>Retrieved Evidence Used For Score</h3>${bid.evidence_used.map(e=>`<div class="context-card"><strong>${e.document_title} ${e.section}</strong><span class="pill blue">chunk ${e.chunk_id}</span><p>${e.text_preview}</p></div>`).join("")}</div>`;
}

async function renderCompliance() {
  setPage("Compliance Matrix", "Analysis / Compliance Matrix");
  const c = await api("/api/compliance");
  view.innerHTML = `<section class="page"><div class="panel"><div class="top-actions"><div><h2>Compliance Matrix · DHS Cyber Modernization RFP</h2><p class="sub">Extracted from uploaded RFP text and persisted in the proposal workflow.</p></div><div><strong>${c.summary.total}</strong> Total &nbsp; <strong>${c.summary.high}</strong> High risk &nbsp; <strong>${c.summary.open}</strong> Open &nbsp; <strong>${c.summary.complete}</strong> Complete</div></div></div><div class="panel"><div class="row"><input id="matrix-file" type="file" accept=".txt,.md,.pdf"><button class="btn" id="extract-matrix">Upload RFP & Extract Requirements</button><button class="btn light" onclick="route('Traceability')">Open Traceability</button></div><pre id="matrix-proof" class="code">Good output: extracted requirements appear in the table, then survive refresh because they live in application state / DB equivalent.</pre></div><div class="panel"><table><thead><tr><th>ID</th><th>RFP §</th><th>Requirement</th><th>Owner</th><th>Evidence</th><th>Risk</th><th>Status</th><th>Trace</th></tr></thead><tbody>${c.rows.map(r=>`<tr><td>${r[0]}</td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td><td>${r[4]}</td><td><span class="pill ${r[5]==="High"?"bad":r[5]==="Medium"?"warn":"good"}">${r[5]}</span></td><td><button class="btn light" onclick="assignRequirement('${r[7]}')">${r[6]}</button></td><td><button class="btn" onclick="openTrace('${r[7]}')">Build Trace</button></td></tr>`).join("")}</tbody></table></div></section>`;
  document.getElementById("extract-matrix").onclick = extractComplianceMatrix;
}

async function extractComplianceMatrix() {
  const fileInput = document.getElementById("matrix-file");
  const fallback = "C.3.1 The contractor shall provide 24/7 cybersecurity monitoring services. C.3.2 The offeror must document incident escalation procedures. M.1 The proposal must show transition risk controls.";
  const file = fileInput.files[0] || new File([fallback], "sample_rfp_requirements.txt", { type: "text/plain" });
  const form = new FormData();
  form.append("rfp_file", file);
  const result = await api("/api/compliance/extract", { method: "POST", body: form });
  document.getElementById("matrix-proof").textContent = JSON.stringify(result, null, 2);
  setTimeout(renderCompliance, 450);
}

async function assignRequirement(id) {
  await api(`/api/compliance/requirements/${id}/assign`, { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({ owner: "Tech Lead", status: "In progress" }) });
  renderCompliance();
}

async function openTrace(id) {
  state.activeRequirementId = id;
  renderTraceability();
}

async function renderTraceability() {
  setPage("Traceability", "Workflow / Requirement Traceability");
  const c = await api("/api/compliance/requirements");
  const first = state.activeRequirementId || c.requirements[0]?.id;
  let trace = first ? await api(`/api/compliance/requirements/${first}/trace`) : null;
  view.innerHTML = `<section class="page"><div class="top-actions"><div><h2>Requirement Traceability</h2><p class="sub">Click a requirement and prove source RFP text -> RAG evidence -> proposed response -> confidence.</p></div><button class="btn light" onclick="route('Compliance Matrix')">Back to Matrix</button></div><div class="grid two"><div class="panel"><h3>Requirements</h3>${c.requirements.map(r=>`<div class="row"><div><strong>${r.requirement_id}</strong><br><span>${r.requirement_text}</span></div><button class="btn" onclick="openTrace('${r.id}')">Build Trace</button></div>`).join("") || "<p>No requirements yet. Extract the matrix first.</p>"}</div><div class="panel"><h3>Trace Proof</h3>${trace ? `<h4>Source RFP Text</h4><p>${trace.source_rfp_text}</p><h4>Retrieved Evidence</h4>${trace.retrieved_evidence.map(e=>`<div class="context-card"><strong>${e.document} ${e.section}</strong><span class="pill good">${e.score}</span><p>${e.snippet}</p></div>`).join("")}<h4>Proposed Response Section</h4><textarea readonly>${trace.proposed_response_section}</textarea><h4>Confidence</h4><p><span class="pill good">${trace.confidence_score}</span> ${trace.score_reason}</p>` : "<p>Choose a requirement to build a trace.</p>"}</div></div></section>`;
}

async function renderProposalWorkspace() {
  setPage("Proposal Workspace", "Workflow / Proposal Workspace");
  const workspace = await api("/api/proposals/workspace");
  view.innerHTML = `<section class="page"><div class="top-actions"><div><h2>${workspace.proposal.name}</h2><p class="sub">Technical, Management, Past Performance, and Pricing volumes with owners and completion.</p></div><button class="btn" onclick="updateFirstSection()">Save Example Section</button></div><div class="grid three">${workspace.sections.map(s=>`<div class="panel"><span class="small-note">${s.volume}</span><h3>${s.section_title}</h3><p>Owner: <strong>${s.assigned_to}</strong></p><p>Status: ${s.status}</p><div class="factor"><span>Complete</span><div class="track"><div class="fill" style="width:${s.percent_complete}%"></div></div><strong>${s.percent_complete}</strong></div><textarea id="section-${s.id}">${s.content || "Draft content will appear here after trace/content reuse."}</textarea><p class="small-note">Section ID: ${s.id}</p></div>`).join("")}</div></section>`;
  state.firstSectionId = workspace.sections[0]?.id;
}

async function updateFirstSection() {
  if (!state.firstSectionId) return;
  await api(`/api/proposals/sections/${state.firstSectionId}`, { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({ percent_complete: 65, status: "In review", content: "Draft technical approach with SOC monitoring evidence and escalation workflow." }) });
  renderProposalWorkspace();
}

async function renderContentLibrary() {
  setPage("Content Library", "Knowledge / Content Library");
  const workspace = await api("/api/proposals/workspace");
  const data = await api("/api/content-library/search?q=monitoring");
  view.innerHTML = `<section class="page"><div class="top-actions"><div><h2>Content Library Reuse</h2><p class="sub">Approved language can be reused only with evidence references attached.</p></div><button class="btn" onclick="searchLibrary()">Search Approved Content</button></div><div class="panel row"><input id="library-query" value="monitoring"><select id="target-section">${workspace.sections.map(s=>`<option value="${s.id}">${s.volume} - ${s.section_title}</option>`).join("")}</select></div><div id="library-results" class="grid two">${libraryCards(data.results)}</div></section>`;
}

function libraryCards(results) {
  return results.map(r=>`<div class="panel"><span class="pill blue">${r.content_type}</span><h3>${r.title}</h3><p>${r.body}</p><p>Approved: <strong>${r.approved ? "Yes" : "No"}</strong></p><pre class="code">${JSON.stringify(r.evidence_refs, null, 2)}</pre><button class="btn" onclick="insertLibraryContent('${r.id}')">Insert Into Proposal</button></div>`).join("");
}

async function searchLibrary() {
  const q = document.getElementById("library-query").value;
  const data = await api(`/api/content-library/search?q=${encodeURIComponent(q)}`);
  document.getElementById("library-results").innerHTML = libraryCards(data.results);
}

async function insertLibraryContent(contentId) {
  const sectionId = document.getElementById("target-section").value;
  await api("/api/content-library/insert", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({ section_id: sectionId, content_id: contentId }) });
  route("Proposal Workspace");
}

async function renderReviews() {
  setPage("Reviews", "Workflow / Red Pink Gold Reviews");
  const issues = await api("/api/reviews/issues");
  view.innerHTML = `<section class="page"><div class="top-actions"><div><h2>Red / Pink / Gold Team Review</h2><p class="sub">Issues keep severity, owner, status, evidence, and response history.</p></div><button class="btn" onclick="createReviewIssue()">Create High Severity Issue</button></div><div class="grid two">${issues.issues.map(i=>`<div class="panel"><span class="pill ${i.severity==="High"?"bad":"warn"}">${i.severity}</span><h3>${i.issue}</h3><p>Owner: <strong>${i.owner}</strong> · Status: <strong>${i.status}</strong></p><p>${i.comment}</p><pre class="code">${JSON.stringify(i.response_history, null, 2)}</pre><button class="btn" onclick="resolveIssue('${i.id}')">Mark Resolved</button></div>`).join("")}</div></section>`;
}

async function createReviewIssue() {
  await api("/api/reviews/issues", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({ issue: "Red Team: technical response needs stronger citation coverage.", severity: "High", owner: "adam.davis", comment: "Tie claim to requirement trace evidence." }) });
  renderReviews();
}

async function resolveIssue(id) {
  await api(`/api/reviews/issues/${id}`, { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({ status: "Resolved", comment: "Added evidence-backed SOC monitoring language." }) });
  renderReviews();
}

async function renderHealthDashboard() {
  setPage("Health Dashboard", "Workflow / Proposal Health Dashboard");
  const h = await api("/api/proposal-health");
  view.innerHTML = `<section class="page"><div class="panel"><h2>Proposal Health Dashboard</h2><p class="sub">Calculated from requirements, traces, proposal sections, content reuse, and review issues.</p></div><div class="grid two"><div class="panel gauge"><span>READINESS SCORE</span><strong>${h.readiness_score}</strong><p>out of 100</p><span class="pill ${h.readiness_score >= 70 ? "good" : "warn"}">${h.bid_no_bid_impact}</span></div><div class="panel"><h3>Live Factors</h3>${Object.entries({requirements_complete_pct:h.requirements_complete_pct,evidence_coverage_pct:h.evidence_coverage_pct,review_resolution_pct:h.review_resolution_pct,section_completion_pct:h.section_completion_pct}).map(([k,v])=>`<div class="factor"><span>${k.replaceAll("_"," ")}</span><div class="track"><div class="fill" style="width:${v}%"></div></div><strong>${v}</strong></div>`).join("")}</div></div><div class="grid three"><div class="panel"><h3>Missing Items</h3><strong>${h.missing_items}</strong></div><div class="panel"><h3>High Risk Requirements</h3><strong>${h.high_risk_requirements}</strong></div><div class="panel"><h3>Review Queue</h3><strong>${h.review_queue}</strong><p>Schedule risk: ${h.schedule_risk}</p></div></div></section>`;
}

async function renderAudit() {
  setPage("Audit Logs", "Admin / Audit Logs");
  const audit = await api("/api/audit");
  view.innerHTML = `<section class="page"><div class="top-actions"><div><h2>Audit Logs</h2><p class="sub">Every query, retrieval, and guardrail decision - immutable and exportable.</p></div><span class="pill blue">Admin only</span></div><div class="panel"><button class="btn light">All users</button> <button class="btn light">All roles</button> <button class="btn light">Guardrail: any</button> <button class="btn">Export log</button></div><div class="panel"><table><thead><tr><th>TIME</th><th>USER</th><th>ROLE</th><th>QUERY / ACTION</th><th>STATUS</th><th>DETAILS</th></tr></thead><tbody>${audit.events.map(e=>`<tr class="${e.status==="blocked"?"guard":""}"><td>${e.time}</td><td>${e.user}</td><td>${e.role}</td><td>${e.action}</td><td><span class="pill ${e.status==="blocked"?"bad":"good"}">${e.status}</span></td><td>${JSON.stringify(e.details).slice(0,90)}</td></tr>`).join("")}</tbody></table></div></section>`;
}

async function renderTrace() {
  setPage("Eval / Trace", "Analysis / Eval / Trace");
  const trace = state.lastTraceId ? await api(`/api/trace/${state.lastTraceId}`) : null;
  view.innerHTML = `<section class="page"><h2>RAGAS + Phoenix Trace</h2><p class="sub">Local simulation matching production observability concepts.</p><div class="grid two"><div class="panel"><h3>Trace</h3><pre class="code">${JSON.stringify(trace || {message:"Ask a question first to create a trace."}, null, 2)}</pre></div><div class="panel"><h3>What this proves</h3><ul><li>query guard runs before retrieval</li><li>hybrid search and RRF run before rerank</li><li>context builder feeds Claude Sonnet Bedrock mock</li><li>RAGAS-style score and Phoenix-style spans are returned</li></ul></div></div></section>`;
}

async function renderVerification() {
  setPage("Verification", "Analysis / Internal Verification");
  const iam = await api("/api/iam/simulation");
  const traces = await api("/api/verification/ingestion-traces");
  const vector = await api("/api/vector-db");
  view.innerHTML = `<section class="page">
    <div class="top-actions"><div><h2>Internal Workflow Verification</h2><p class="sub">Prove the hidden mechanics: IAM simulation, ingestion trace, and vector-store rows.</p></div><button class="btn" onclick="renderVerification()">Refresh Proof</button></div>
    <div class="grid three">
      <div class="panel"><h3>IAM / RBAC Simulation</h3><p><strong>${iam.user}</strong> · ${iam.role} · ${iam.tenant_id}</p>${iam.checks.map(c=>`<div class="row"><span>${c.action}</span><span class="pill ${c.allowed ? "good" : "bad"}">${c.allowed ? "allowed" : "blocked"}</span></div>`).join("")}<p class="small-note">${iam.production_equivalent}</p></div>
      <div class="panel"><h3>Latest Ingestion Trace</h3><pre class="code">${JSON.stringify(traces.traces[0] || {message:"Upload or chat-attach a document first."}, null, 2)}</pre></div>
      <div class="panel"><h3>Vector DB Viewer</h3><p><strong>${vector.row_count}</strong> local vector rows · ${vector.store}</p><p class="small-note">${vector.production_equivalent}</p><div class="vector-rows">${vector.rows.slice(0,6).map(r=>`<div class="context-card"><strong>chunk ${r.chunk_id}</strong> ${r.document_title}<br><span class="pill blue">${r.embedding_dimensions} dims</span> <span class="pill blue">${r.section}</span><p>${r.text_preview}</p></div>`).join("")}</div></div>
    </div>
  </section>`;
}
