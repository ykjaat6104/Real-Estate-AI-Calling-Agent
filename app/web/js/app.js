/* Live caller logic for the Real Estate AI Calling Agent */
"use strict";

const API_BASE = "";
const token = localStorage.getItem("access_token");

const state = {
    room: null,
    url: null,
    token: null,
    conn: null,
    inCall: false,
    audio: null,
    projectId: null,
};

const $ = (id) => document.getElementById(id);

const STATUS = {
    idle: ["idle", "Ready to start"],
    connecting: ["connecting", "Connecting..."],
    live: ["live", "In call — speak now"],
    ended: ["ended", "Call ended"],
};

function setStatus(key) {
    const [cls, text] = STATUS[key];
    $("statusDot").className = `dot ${cls}`;
    $("statusText").textContent = text;
}

/* ---------- Microphone selection ---------- */
async function loadMics() {
    try {
        await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch {
        /* will prompt on Start Call instead */
    }
    const devices = await navigator.mediaDevices.enumerateDevices();
    const mics = devices.filter((d) => d.kind === "audioinput");
    const sel = $("micSel");
    sel.innerHTML = "";
    mics.forEach((m, i) => {
        const opt = document.createElement("option");
        opt.value = m.deviceId;
        opt.textContent = m.label || `Microphone ${i + 1}`;
        sel.appendChild(opt);
    });
}

/* ---------- Project selection ---------- */
async function loadProjects() {
    try {
        const res = await fetch(`${API_BASE}/api/v1/projects`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
            const projects = await res.json();
            const sel = $("projectSel");
            sel.innerHTML = '<option value="">Select a project</option>';
            projects.forEach((p) => {
                const opt = document.createElement("option");
                opt.value = p.id;
                opt.textContent = p.name;
                sel.appendChild(opt);
            });
        }
    } catch (err) {
        console.error("Failed to load projects:", err);
    }
}

/* ---------- Transcript ---------- */
function addTurn(role, text) {
    const box = $("transcript");
    const placeholder = box.querySelector(".placeholder");
    if (placeholder) placeholder.remove();
    const div = document.createElement("div");
    div.className = `turn ${role}`;
    const who = document.createElement("div");
    who.className = "who";
    who.textContent = role === "user" ? "Customer" : role === "agent" ? "Agent" : "System";
    const txt = document.createElement("div");
    txt.className = "txt";
    txt.textContent = text;
    div.appendChild(who);
    div.appendChild(txt);
    box.appendChild(div);
    box.scrollTop = box.scrollHeight;
}

/* ---------- Live lead panel ---------- */
const FIELD_LABELS = [
    ["status", "Status"],
    ["language", "Language"],
    ["name", "Name"],
    ["phone", "Phone"],
    ["purpose", "Purpose"],
    ["property_type", "Property type"],
    ["configuration", "Configuration"],
    ["preferred_location", "Preferred location"],
    ["budget_min", "Budget (from)"],
    ["budget_max", "Budget (to)"],
    ["timeline", "Timeline"],
    ["questions_asked", "Questions"],
    ["notes", "Notes"],
];

function renderLead(lead) {
    const dl = $("leadFields");
    dl.innerHTML = "";
    let any = false;
    for (const [key, label] of FIELD_LABELS) {
        const val = lead[key];
        if (val && val !== "Not specified" && val !== "INR") {
            any = true;
            const row = document.createElement("div");
            row.className = "field";
            const dt = document.createElement("dt");
            dt.textContent = label;
            const dd = document.createElement("dd");
            dd.textContent = val;
            row.appendChild(dt);
            row.appendChild(dd);
            dl.appendChild(row);
        }
    }
    if (!any) {
        const div = document.createElement("div");
        div.className = "placeholder";
        div.textContent = "Collecting your requirements...";
        dl.appendChild(div);
    }

    const badge = $("liveState");
    if (lead.status === "qualified") {
        badge.textContent = "lead captured";
        badge.className = "live-badge active";
    } else if (lead.status === "in_progress") {
        badge.textContent = "in progress";
        badge.className = "live-badge";
    } else {
        badge.textContent = lead.status;
        badge.className = "live-badge ended";
    }

    const existing = dl.parentNode.querySelector(".summary-box");
    if (existing) existing.remove();
    if (lead.call_summary) {
        const box = document.createElement("div");
        box.className = "summary-box";
        const h = document.createElement("h3");
        h.textContent = "Call Summary";
        const pre = document.createElement("div");
        pre.textContent = lead.call_summary;
        box.appendChild(h);
        box.appendChild(pre);
        dl.parentNode.appendChild(box);
    }
}

/* ---------- Polling (live transcript + lead) ---------- */
let pollTimer = null;
function startPolling() {
    stopPolling();
    pollTimer = setInterval(async () => {
        try {
            const tRes = await fetch(`${API_BASE}/api/v1/leads/call/${state.room}/transcript`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (tRes.ok) {
                const { transcript } = await tRes.json();
                const known = new Set(
                    [...document.querySelectorAll("#transcript .turn")].map((n) => n.dataset.sig)
                );
                for (const turn of transcript) {
                    const sig = `${turn.role}|${turn.text}`;
                    if (!known.has(sig)) {
                        addTurn(turn.role, turn.text);
                    }
                }
            }
        } catch {}

        try {
            const lRes = await fetch(`${API_BASE}/api/v1/leads/call/${state.room}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (lRes.ok) renderLead(await lRes.json());
        } catch {}
    }, 1500);
}

function stopPolling() {
    if (pollTimer) clearInterval(pollTimer);
    pollTimer = null;
}

/* ---------- Call control ---------- */
async function startCall() {
    if (state.inCall) return;

    const projectId = $("projectSel").value;
    if (!projectId) {
        alert("Please select a project first");
        return;
    }

    $("startBtn").disabled = true;
    setStatus("connecting");

    try {
        const res = await fetch(`${API_BASE}/api/v1/token`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify({ project_id: projectId })
        });
        if (!res.ok) throw new Error((await res.json()).detail || "token request failed");
        const { url, token: lkToken, room } = await res.json();
        state.url = url;
        state.token = lkToken;
        state.room = room;
        state.projectId = projectId;

        const audio = getAudio();
        const roomConn = new LivekitClient.Room();
        state.conn = roomConn;

        roomConn.on("trackSubscribed", (track) => {
            if (track.kind === "audio") {
                audio.srcObject = new MediaStream([track.mediaStreamTrack]);
                audio.play();
            }
        });

        await roomConn.connect(url, lkToken, {
            audio: { deviceId: $("micSel").value || undefined },
            video: false,
        });

        state.inCall = true;
        setStatus("live");
        $("endBtn").disabled = false;
        startPolling();
    } catch (err) {
        console.error(err);
        setStatus("idle");
        $("startBtn").disabled = false;
        $("transcript").innerHTML = `<div class="turn system"><div class="who">System</div><div class="txt">Error starting call: ${err.message}</div></div>`;
    }
}

function getAudio() {
    if (!state.audio) {
        state.audio = document.createElement("audio");
        state.audio.autoplay = true;
        document.body.appendChild(state.audio);
    }
    return state.audio;
}

async function endCall() {
    if (!state.conn) return;
    await state.conn.disconnect();
    state.conn = null;
    state.inCall = false;
    if (state.audio) {
        state.audio.srcObject = null;
        state.audio.pause();
    }
    setStatus("ended");
    $("endBtn").disabled = true;
    $("startBtn").disabled = false;
    stopPolling();
    // Final snapshot of the lead
    setTimeout(async () => {
        try {
            const lRes = await fetch(`${API_BASE}/api/v1/leads/call/${state.room}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            if (lRes.ok) renderLead(await lRes.json());
        } catch {}
        setStatus("idle");
    }, 2500);
}

/* ---------- Init ---------- */
$("startBtn").addEventListener("click", startCall);
$("endBtn").addEventListener("click", endCall);
loadMics();
loadProjects();
setStatus("idle");
