/* Dashboard logic */
"use strict";

const API_BASE = "";
const token = localStorage.getItem("access_token");

const $ = (id) => document.getElementById(id);

const FIELDS = [
    ["status", "Status"], ["language", "Language"], ["name", "Name"], ["phone", "Phone"],
    ["purpose", "Purpose"], ["property_type", "Property type"], ["configuration", "Configuration"],
    ["preferred_location", "Preferred location"], ["budget_min", "Budget from"], ["budget_max", "Budget to"],
    ["currency", "Currency"], ["timeline", "Timeline"], ["questions_asked", "Questions asked"], ["notes", "Notes"],
    ["created_at", "Created"], ["call_id", "Call / Room ID"],
];

const SKIP = new Set(["transcript", "call_summary", "id", "updated_at"]);

function chip(status) {
    return `<span class="chip ${status}">${status.replace("_", " ")}</span>`;
}

function esc(s) {
    return String(s ?? "").replace(/[&<>"]/g, c => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;"
    }[c]));
}

async function load() {
    let leads = [];
    try {
        const res = await fetch(`${API_BASE}/api/v1/leads`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) leads = await res.json();
    } catch {}

    // Update stats
    $("statTotal").textContent = leads.length;
    $("statQualified").textContent = leads.filter(l => l.status === "qualified").length;

    const qualifiedCount = leads.filter(l => l.status === "qualified").length;
    const conversionRate = leads.length > 0 ? Math.round((qualifiedCount / leads.length) * 100) : 0;
    $("statConversion").textContent = `${conversionRate}%`;

    $("statHot").textContent = leads.filter(l => l.intent === "hot_lead").length;

    const tbody = $("leadTable").querySelector("tbody");
    if (!leads.length) {
        tbody.innerHTML = '<tr><td colspan="10" class="empty">No leads yet. Start a call from the demo page.</td></tr>';
        return;
    }

    tbody.innerHTML = "";
    leads.forEach((l) => {
        const tr = document.createElement("tr");
        tr.className = "row-click";
        tr.dataset.id = l.id;
        tr.innerHTML = [
            `<td>${l.id}</td>`,
            `<td>${esc((l.created_at || "").slice(0, 19).replace("T", " "))}</td>`,
            `<td>${chip(l.status)}</td>`,
            `<td>${esc(l.name)}</td>`,
            `<td>${esc(l.phone)}</td>`,
            `<td>${esc(l.purpose)}</td>`,
            `<td>${esc(l.configuration)}</td>`,
            `<td>${esc(l.preferred_location)}</td>`,
            `<td>${esc(l.budget_min)} - ${esc(l.budget_max)}</td>`,
            `<td>${esc(l.timeline)}</td>`,
        ].join("");
        tr.addEventListener("click", () => openModal(l));
        tbody.appendChild(tr);
    });
}

function openModal(l) {
    $("modalTitle").textContent = `Lead #${l.id}`;
    const grid = $("modalGrid");
    grid.innerHTML = "";
    for (const [key, label] of FIELDS) {
        if (SKIP.has(key)) continue;
        const val = l[key];
        if (val && val !== "Not specified" && val !== "INR") {
            const div = document.createElement("div");
            const dt = document.createElement("dt");
            dt.textContent = label;
            const dd = document.createElement("dd");
            dd.textContent = val;
            div.appendChild(dt);
            div.appendChild(dd);
            grid.appendChild(div);
        }
    }
    $("modalSummary").textContent = l.call_summary ? "CALL SUMMARY\n" + l.call_summary : "";
    $("modalTranscript").textContent = l.transcript && l.transcript.length
        ? "TRANSCRIPT\n" + l.transcript.map(t => `${t.role}: ${t.text}`).join("\n") : "";
    $("modal").classList.add("open");
}

function exportCSV() {
    const leads = [];
    document.querySelectorAll("#leadTable tbody tr").forEach(tr => {
        const cells = tr.querySelectorAll("td");
        if (cells.length >= 10) {
            leads.push([
                cells[0].textContent,
                cells[1].textContent,
                cells[2].textContent,
                cells[3].textContent,
                cells[4].textContent,
                cells[5].textContent,
                cells[6].textContent,
                cells[7].textContent,
                cells[8].textContent,
                cells[9].textContent,
            ].join(","));
        }
    });

    if (leads.length === 0) {
        alert("No data to export");
        return;
    }

    const csv = "ID,Time,Status,Name,Phone,Purpose,Config,Location,Budget,Timeline\n" + leads.join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `leads-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
}

$("modalClose").addEventListener("click", () => $("modal").classList.remove("open"));
$("modal").addEventListener("click", (e) => {
    if (e.target === $("modal")) $("modal").classList.remove("open");
});

$("exportBtn").addEventListener("click", exportCSV);

load();
setInterval(load, 3000);
