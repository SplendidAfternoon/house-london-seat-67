const COLORS = {
  extend: "extend",
  convert: "convert",
  replace: "replace",
  ldc: "ldc",
};

const ORDER = ["extend", "convert", "replace", "ldc"];

async function loadData() {
  if (window.EMBEDDED_DATA) return window.EMBEDDED_DATA;
  const res = await fetch("data.json");
  if (!res.ok) throw new Error("data.json missing — run python run.py first");
  return res.json();
}

function pack(area) {
  return ORDER.map((key) => ({ key, ...area[key] }));
}

function pct(n, total) {
  if (!total) return "0%";
  return `${Math.round((n / total) * 100)}%`;
}

function renderBars(area) {
  const rows = pack(area);
  const total = rows.reduce((s, r) => s + r.count, 0);
  const bars = document.getElementById("bars");
  bars.innerHTML = "";
  const bar = document.createElement("div");
  bar.className = "bar";

  for (const row of rows) {
    const seg = document.createElement("button");
    seg.type = "button";
    seg.className = `seg ${COLORS[row.key]}`;
    seg.style.flex = String(Math.max(row.count, 0));
    const rate = Math.round((row.approval_rate || 0) * 100);
    seg.textContent = row.count ? `${pct(row.count, total)}` : "";
    seg.title = `${row.label}: ${row.count.toLocaleString()} applications, ${rate}% approved`;
    seg.addEventListener("click", () => showExamples(row));
    bar.appendChild(seg);
  }
  bars.appendChild(bar);

  const replace = area.replace?.count || 0;
  const extend = area.extend?.count || 0;
  const ratio = replace > 0 ? (extend / replace).toFixed(1) : "—";
  document.getElementById("summary").textContent = total
    ? `${total.toLocaleString()} housing-related applications. ${extend.toLocaleString()} extend vs ${replace.toLocaleString()} knock-down & rebuild (${ratio} to 1).`
    : "No applications in this view.";
  const legend = document.getElementById("legend");
  if (legend) {
    legend.innerHTML = rows
      .filter((r) => r.count)
      .map(
        (r) =>
          `<span class="leg-${r.key}"><strong>${r.label}</strong> ${pct(r.count, total)} · ${Math.round((r.approval_rate || 0) * 100)}% approved</span>`
      )
      .join("");
  }
}

function showExamples(row) {
  document.querySelectorAll(".seg").forEach((el) => el.classList.remove("active"));
  document.querySelector(`.seg.${row.key}`)?.classList.add("active");
  const box = document.getElementById("examples");
  const list = document.getElementById("example-list");
  document.getElementById("examples-title").textContent = `${row.label} examples`;
  list.innerHTML = "";
  if (!row.examples?.length) {
    list.innerHTML = "<li>No example descriptions in this cut.</li>";
  } else {
    for (const ex of row.examples) {
      const li = document.createElement("li");
      const link = ex.url
        ? `<p><a href="${ex.url}" target="_blank" rel="noreferrer">Foreman record</a></p>`
        : "";
      li.innerHTML = `<p>${ex.description || "(no description)"}</p><p>${ex.decision || "decision unknown"}</p>${link}`;
      list.appendChild(li);
    }
  }
  box.hidden = false;
}

function fillSelect(data) {
  const select = document.getElementById("borough");
  const names = ["London (all)", ...Object.keys(data.boroughs)];
  select.innerHTML = names
    .map((name, i) => `<option value="${i === 0 ? "__london__" : name}">${name}</option>`)
    .join("");
  return select;
}

function areaFor(data, value) {
  return value === "__london__" ? data.london : data.boroughs[value];
}

loadData()
  .then((data) => {
    document.getElementById("honesty").textContent = data.honesty || "";
    const hero = document.getElementById("hero-stat");
    if (hero && data.london) {
      const t = ORDER.reduce((s, k) => s + data.london[k].count, 0);
      const extShare = Math.round((100 * data.london.extend.count) / t);
      const repShare = Math.round((100 * data.london.replace.count) / t);
      const extAp = Math.round(data.london.extend.approval_rate * 100);
      const repAp = Math.round(data.london.replace.approval_rate * 100);
      hero.textContent = `${extShare}% of apps extend in place · ${repShare}% knock down & rebuild · both ~${extAp}–${repAp}% approved`;
    }
    const insight = document.getElementById("insight");
    if (insight && data.takeaways?.headline) {
      insight.textContent = data.takeaways.headline;
    }
    const select = fillSelect(data);
    const redraw = () => renderBars(areaFor(data, select.value));
    select.addEventListener("change", redraw);
    redraw();
  })
  .catch((err) => {
    document.getElementById("summary").textContent = err.message;
  });
