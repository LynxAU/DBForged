(function () {
  var state = {
    tab: "abilities",
    search: "",
    groupByOwner: true,
    selectedTypes: {},
    selectedOwners: {},
    selectedRaces: {},
    selectedEras: {},
    data: {
      abilities: [],
      top50: [],
      racials: [],
      transformations: [],
    },
  };

  var el = {
    tabs: document.getElementById("tabs"),
    searchInput: document.getElementById("searchInput"),
    typeFilters: document.getElementById("typeFilters"),
    ownerFilters: document.getElementById("ownerFilters"),
    raceFilters: document.getElementById("raceFilters"),
    eraFilters: document.getElementById("eraFilters"),
    resetFilters: document.getElementById("resetFilters"),
    viewTitle: document.getElementById("viewTitle"),
    viewSubtitle: document.getElementById("viewSubtitle"),
    resultCount: document.getElementById("resultCount"),
    groupToggle: document.getElementById("groupToggle"),
    viewRoot: document.getElementById("viewRoot"),
    statAbilities: document.getElementById("statAbilities"),
    statTop50: document.getElementById("statTop50"),
    statRacials: document.getElementById("statRacials"),
    statTransforms: document.getElementById("statTransforms"),
  };

  var TAB_META = {
    abilities: {
      title: "All Abilities",
      subtitle: "Expanded shared roster parsed from the current DBForged draft.",
    },
    top50: {
      title: "Top 50",
      subtitle: "Curated roster from the expanded draft (transformations excluded).",
    },
    racials: {
      title: "Racial Baselines",
      subtitle: "Three racials per race for the expanded playable race roster.",
    },
    transformations: {
      title: "Transformations",
      subtitle: "Race-by-race form list parsed from the expanded draft.",
    },
  };

  window.addEventListener("error", function (event) {
    showFatal("JavaScript error: " + (event && event.message ? event.message : "unknown"));
  });
  window.addEventListener("unhandledrejection", function (event) {
    var msg = event && event.reason ? String(event.reason) : "Unhandled promise rejection";
    showFatal(msg);
  });

  init();

  function init() {
    bindUI();
    renderLoading();
    loadMarkdown()
      .then(function (markdown) {
        state.data = parseExpandedDraft(markdown);
        updateStats();
        render();
      })
      .catch(function (err) {
        showFatal("Failed to load/parse draft: " + (err && err.message ? err.message : String(err)));
      });
  }

  function bindUI() {
    if (el.tabs) {
      el.tabs.addEventListener("click", function (event) {
        var btn = event.target.closest("[data-tab]");
        if (!btn) return;
        state.tab = btn.getAttribute("data-tab");
        var buttons = el.tabs.querySelectorAll(".tab");
        for (var i = 0; i < buttons.length; i++) {
          buttons[i].classList.toggle("is-active", buttons[i] === btn);
        }
        render();
      });
    }

    if (el.searchInput) {
      el.searchInput.addEventListener("input", function () {
        state.search = (el.searchInput.value || "").trim().toLowerCase();
        render();
      });
    }

    if (el.resetFilters) {
      el.resetFilters.addEventListener("click", function () {
        state.selectedTypes = {};
        state.selectedOwners = {};
        state.selectedRaces = {};
        state.selectedEras = {};
        render();
      });
    }

    if (el.groupToggle) {
      el.groupToggle.addEventListener("click", function () {
        state.groupByOwner = !state.groupByOwner;
        render();
      });
    }
  }

  function loadMarkdown() {
    return fetch("../DBFORGED_EXPANDED_RACES_ABILITY_RACIAL_TRANSFORM_DRAFT.md").then(function (res) {
      if (!res.ok) throw new Error("HTTP " + res.status);
      return res.text();
    });
  }

  function parseExpandedDraft(md) {
    var lines = md.replace(/\r\n/g, "\n").split("\n");
    var abilities = parseAbilities(lines);
    var racials = parseRacials(lines);
    var transformations = parseTransformations(lines);

    var top50 = abilities.slice(0, 50).map(function (a, idx) {
      return {
        rank: idx + 1,
        name: a.name,
        ownerGroup: a.ownerGroup || "Shared Roster",
        kind: a.kind || "utility",
        era: a.era || "DBForged Draft",
        race: a.race || "",
        port: a.port || "",
      };
    });

    return {
      abilities: abilities,
      top50: top50,
      racials: racials,
      transformations: transformations,
    };
  }

  function parseAbilities(lines) {
    var out = [];
    var inSection = false;
    var bucket = "utility";
    var current = null;

    for (var i = 0; i < lines.length; i++) {
      var line = lines[i].trim();
      if (line.indexOf("## 2) Shared Ability Roster") === 0) {
        inSection = true;
        continue;
      }
      if (inSection && line.indexOf("## 3) Racial Baselines") === 0) break;
      if (!inSection) continue;

      var bucketMatch = line.match(/^##\s+[A-D]\)\s+(.+)$/);
      if (bucketMatch) {
        var b = bucketMatch[1].toLowerCase();
        if (b.indexOf("blast") >= 0 || b.indexOf("beam") >= 0) bucket = "beam";
        else if (b.indexOf("melee") >= 0 || b.indexOf("interrupt") >= 0) bucket = "melee";
        else if (b.indexOf("control") >= 0 || b.indexOf("defense") >= 0) bucket = "control";
        else if (b.indexOf("support") >= 0 || b.indexOf("spectacle") >= 0) bucket = "support";
        else bucket = "utility";
        continue;
      }

      var item = line.match(/^(\d+)\.\s+\*\*(.+?)\*\*(?:\s+\((.+?)\))?$/);
      if (item) {
        current = {
          rank: parseInt(item[1], 10),
          name: item[2].trim(),
          ownerGroup: inferOwnerFromName(item[2].trim()),
          kind: bucket,
          era: "DBForged Draft",
          race: inferRace("", item[2].trim(), ""),
          effectText: "",
          scaling: "",
          chargeCd: "",
          port: "",
          tags: [],
        };
        out.push(current);
        continue;
      }

      if (!current) continue;

      var metaBold = line.match(/^- \*\*(.+?)\*\*: (.+)$/);
      if (metaBold) {
        applyAbilityMeta(current, metaBold[1], metaBold[2]);
        continue;
      }
      var metaCode = line.match(/^- `([^`]+)`: (.+)$/);
      if (metaCode) {
        applyAbilityMeta(current, metaCode[1], metaCode[2]);
        continue;
      }
    }

    for (var j = 0; j < out.length; j++) {
      out[j].port = [out[j].effectText, out[j].scaling ? "Scaling " + out[j].scaling : "", out[j].chargeCd ? "Cost/CD/Cast " + out[j].chargeCd : ""]
        .filter(Boolean)
        .join(" | ");
      out[j].tags = inferTags(out[j].name, out[j].port);
    }
    return out;
  }

  function applyAbilityMeta(rec, labelRaw, valueRaw) {
    var label = String(labelRaw || "").toLowerCase();
    var value = String(valueRaw || "").trim();
    if (label.indexOf("category") >= 0) rec.kind = value.replace(/`/g, "").toLowerCase();
    else if (label.indexOf("scaling") >= 0) rec.scaling = value;
    else if (label.indexOf("cost/cd/cast") >= 0) rec.chargeCd = value;
    else if (label.indexOf("effect") >= 0) rec.effectText = value;
  }

  function parseRacials(lines) {
    var out = [];
    var inSection = false;
    var currentRace = "";
    var current = null;

    for (var i = 0; i < lines.length; i++) {
      var line = lines[i].trim();
      if (line.indexOf("## 3) Racial Baselines") === 0 || line.indexOf("## 3) 3 Racial Baseline") === 0) {
        inSection = true;
        continue;
      }
      if (inSection && (line.indexOf("## 4) Transformations") === 0 || line.indexOf("## 4) Updated Transformations") === 0)) break;
      if (!inSection) continue;

      var h = line.match(/^##\s+(.+)$/);
      if (h) {
        currentRace = mapRaceHeading(h[1]);
        if (!currentRace) current = null;
        continue;
      }

      var num = line.match(/^\d+\.\s+\*\*(.+?)\*\*\s+\((.+)\)$/);
      if (num && currentRace) {
        current = {
          race: currentRace,
          name: num[1].trim(),
          kind: num[2].trim(),
          balance: "",
          port: "",
        };
        out.push(current);
        continue;
      }

      var bullet = line.match(/^- (.+)$/);
      if (bullet && current) {
        var text = bullet[1].trim();
        if (!current.balance) current.balance = text;
        else if (!current.port) current.port = text;
        else current.port += " " + text;
      }
    }

    return out;
  }

  function mapRaceHeading(raw) {
    var h = String(raw || "").toLowerCase().trim();
    if (h.indexOf("saiyan") === 0) return "saiyan";
    if (h.indexOf("human") === 0) return "human";
    if (h.indexOf("namekian") === 0) return "namekian";
    if (h.indexOf("frost demon") === 0) return "frost_demon";
    if (h.indexOf("android") === 0) return "android";
    if (h.indexOf("majin") === 0) return "majin";
    if (h.indexOf("half breed") === 0) return "half_breed";
    if (h.indexOf("truffle") === 0) return "truffle";
    if (h.indexOf("grey") === 0) return "grey";
    if (h.indexOf("bio android") === 0) return "bio_android";
    return "";
  }

  function parseTransformations(lines) {
    var out = [];
    var inSection = false;
    var group = "";

    for (var i = 0; i < lines.length; i++) {
      var line = lines[i].trim();
      if (line.indexOf("## 4) Updated Transformations") === 0 || line.indexOf("## 4) Transformations") === 0) {
        inSection = true;
        continue;
      }
      if (inSection && (line.indexOf("## 5) Transformation Stat Slice") === 0 || line.indexOf("## 5) Practical Buildout Plan") === 0)) break;
      if (!inSection) continue;

      var g = line.match(/^##\s+(.+)$/);
      if (g) {
        group = g[1].trim();
        continue;
      }

      var formBullet = line.match(/^- \*\*(.+?)\*\*(?:\s+\((.+?)\))?$/);
      if (formBullet && group) {
        var formName = formBullet[1].trim();
        out.push({
          raceGroup: group,
          name: formName,
          ownerGroup: inferOwnerFromName(formName),
          race: inferRace(group, formName, ""),
          kind: "transformation",
          era: inferEra(formName, group),
          description: "Form listing from expanded race draft.",
          gameSlice: "",
          stats: "",
        });
      }
    }

    return out;
  }

  function updateStats() {
    if (el.statAbilities) el.statAbilities.textContent = state.data.abilities.length + " abilities";
    if (el.statTop50) el.statTop50.textContent = state.data.top50.length + " top picks";
    if (el.statRacials) el.statRacials.textContent = state.data.racials.length + " racials";
    if (el.statTransforms) el.statTransforms.textContent = state.data.transformations.length + " transformations";
  }

  function render() {
    var meta = TAB_META[state.tab];
    if (el.viewTitle) el.viewTitle.textContent = meta.title;
    if (el.viewSubtitle) el.viewSubtitle.textContent = meta.subtitle;
    if (el.groupToggle) {
      var groupVisible = state.tab === "abilities" || state.tab === "transformations";
      el.groupToggle.style.display = groupVisible ? "" : "none";
      el.groupToggle.textContent = "Group by Owner: " + (state.groupByOwner ? "On" : "Off");
    }

    var records = getCurrentRecords();
    var filtered = applyFilters(records);
    if (el.resultCount) el.resultCount.textContent = filtered.length + " result" + (filtered.length === 1 ? "" : "s");

    renderFilterChips(records);
    renderRecords(filtered);
  }

  function getCurrentRecords() {
    if (state.tab === "top50") return state.data.top50;
    if (state.tab === "racials") return state.data.racials;
    if (state.tab === "transformations") return state.data.transformations;
    return state.data.abilities;
  }

  function applyFilters(records) {
    var out = [];
    for (var i = 0; i < records.length; i++) {
      var r = records[i];
      var hay = JSON.stringify(r).toLowerCase();
      if (state.search && hay.indexOf(state.search) < 0) continue;
      if (!passesSet(state.selectedTypes, (r.kind || "").toLowerCase())) continue;
      if (!passesSet(state.selectedOwners, (r.ownerGroup || r.raceGroup || "").toLowerCase())) continue;
      if (!passesSet(state.selectedRaces, (r.race || "").toLowerCase())) continue;
      if (!passesSet(state.selectedEras, (r.era || "").toLowerCase())) continue;
      out.push(r);
    }
    return out;
  }

  function passesSet(setObj, value) {
    var keys = Object.keys(setObj);
    if (!keys.length) return true;
    return !!setObj[value];
  }

  function renderFilterChips(records) {
    paintChips(el.typeFilters, uniqueSorted(records, "kind"), state.selectedTypes);
    paintChips(el.ownerFilters, uniqueSortedMulti(records, ["ownerGroup", "raceGroup"]), state.selectedOwners);
    paintChips(el.raceFilters, uniqueSorted(records, "race"), state.selectedRaces);
    paintChips(el.eraFilters, uniqueSorted(records, "era"), state.selectedEras);
  }

  function uniqueSorted(records, key) {
    var seen = {};
    for (var i = 0; i < records.length; i++) {
      var v = (records[i][key] || "").toLowerCase();
      if (v) seen[v] = true;
    }
    return Object.keys(seen).sort();
  }

  function uniqueSortedMulti(records, keys) {
    var seen = {};
    for (var i = 0; i < records.length; i++) {
      var value = "";
      for (var j = 0; j < keys.length; j++) {
        value = records[i][keys[j]] || "";
        if (value) break;
      }
      value = String(value).toLowerCase();
      if (value) seen[value] = true;
    }
    return Object.keys(seen).sort();
  }

  function paintChips(root, values, selectedStore) {
    if (!root) return;
    root.innerHTML = "";
    if (!values.length) {
      root.innerHTML = '<span class="small muted">No values in this view</span>';
      return;
    }
    for (var i = 0; i < values.length; i++) {
      (function (value) {
        var chip = document.createElement("button");
        chip.className = "chip" + (selectedStore[value] ? " is-active" : "");
        chip.textContent = pretty(value);
        chip.addEventListener("click", function () {
          if (selectedStore[value]) delete selectedStore[value];
          else selectedStore[value] = true;
          render();
        });
        root.appendChild(chip);
      })(values[i]);
    }
  }

  function renderRecords(records) {
    if (!el.viewRoot) return;
    el.viewRoot.innerHTML = "";
    if (!records.length) {
      el.viewRoot.innerHTML = '<div class="empty">No results match the current filters/search.</div>';
      return;
    }

    var shouldGroup = (state.tab === "abilities" || state.tab === "transformations") && state.groupByOwner;
    if (!shouldGroup) {
      var grid = document.createElement("div");
      grid.className = "card-grid";
      for (var i = 0; i < records.length; i++) grid.appendChild(renderCard(records[i]));
      el.viewRoot.appendChild(grid);
      return;
    }

    var groupKey = state.tab === "transformations" ? "raceGroup" : "ownerGroup";
    var grouped = {};
    for (var j = 0; j < records.length; j++) {
      var key = records[j][groupKey] || "Other";
      if (!grouped[key]) grouped[key] = [];
      grouped[key].push(records[j]);
    }
    var names = Object.keys(grouped).sort();
    for (var k = 0; k < names.length; k++) {
      el.viewRoot.appendChild(renderGroupBlock(names[k], grouped[names[k]]));
    }
  }

  function renderGroupBlock(title, records) {
    var wrap = document.createElement("section");
    wrap.className = "group-block";
    wrap.setAttribute("data-group", cssSafe(title));
    var dominantRace = "";
    for (var i = 0; i < records.length; i++) {
      if (records[i].race) {
        dominantRace = records[i].race;
        break;
      }
    }
    if (dominantRace) wrap.setAttribute("data-race", cssSafe(dominantRace));

    var head = document.createElement("div");
    head.className = "group-head";
    head.innerHTML = "<h3>" + escapeHtml(title) + "</h3><span class=\"count\">" + records.length + " item" + (records.length === 1 ? "" : "s") + "</span>";
    wrap.appendChild(head);

    var grid = document.createElement("div");
    grid.className = "card-grid";
    for (var j = 0; j < records.length; j++) grid.appendChild(renderCard(records[j]));
    wrap.appendChild(grid);

    return wrap;
  }

  function renderCard(r) {
    var card = document.createElement("article");
    card.className = "card";
    if (r.race) card.setAttribute("data-race", cssSafe(r.race));
    if (r.kind) card.setAttribute("data-kind", cssSafe(r.kind));

    var subtitle = r.ownerGroup || r.raceGroup || r.race || "";
    var topRight = state.tab === "top50" && r.rank ? '<span class="rank">#' + r.rank + "</span>" : "";

    var badges = [];
    if (r.kind) badges.push(badge(r.kind, "type-" + cssSafe(r.kind)));
    if (r.era) badges.push(badge(r.era, ""));
    if (r.race) badges.push(badge(pretty(r.race), "race-" + cssSafe(r.race)));
    if (Array.isArray(r.tags)) {
      for (var i = 0; i < Math.min(4, r.tags.length); i++) badges.push(badge(r.tags[i], ""));
    }

    var body = "";
    if (state.tab === "racials") {
      body += "<p>" + escapeHtml(r.balance || "") + "</p>";
      body += "<p class=\"muted\">" + escapeHtml(r.port || "") + "</p>";
    } else if (state.tab === "transformations") {
      body += "<p>" + escapeHtml(r.description || "") + "</p>";
      if (r.gameSlice) body += "<p class=\"muted\">" + escapeHtml(r.gameSlice) + "</p>";
      if (r.stats) body += '<div class="meta-list"><div><strong>Suggested Stats:</strong> ' + escapeHtml(r.stats) + "</div></div>";
    } else {
      body += "<p>" + escapeHtml(r.port || "") + "</p>";
      if (r.chargeCd) body += '<div class="meta-list"><div><strong>Cost/CD/Cast:</strong> ' + escapeHtml(r.chargeCd) + "</div></div>";
    }

    card.innerHTML =
      '<div class="card__top">' +
      "<div>" +
      '<h3 class="card__title">' + escapeHtml(r.name || "") + "</h3>" +
      (subtitle ? '<p class="card__subtitle">' + escapeHtml(pretty(subtitle)) + "</p>" : "") +
      "</div>" +
      topRight +
      "</div>" +
      '<div class="badge-row">' + badges.join("") + "</div>" +
      body;
    return card;
  }

  function badge(text, extraClass) {
    var cls = "badge";
    if (extraClass) cls += " " + extraClass;
    return '<span class="' + cls + '">' + escapeHtml(pretty(String(text))) + "</span>";
  }

  function renderLoading() {
    if (el.viewRoot) {
      el.viewRoot.innerHTML = '<div class="empty">Loading catalog from <code>docs/DBFORGED_EXPANDED_RACES_ABILITY_RACIAL_TRANSFORM_DRAFT.md</code>...</div>';
    }
  }

  function showFatal(message) {
    if (!el.viewRoot) return;
    el.viewRoot.innerHTML =
      '<div class="empty">' +
      "<p><strong>Webapp Error</strong></p>" +
      '<p class="small muted">' + escapeHtml(message) + "</p>" +
      "</div>";
  }

  function inferKind(name, text) {
    var hay = (name + " " + text).toLowerCase();
    if (hay.indexOf("barrier") >= 0 || hay.indexOf("shield") >= 0 || hay.indexOf("defense") >= 0) return "defense";
    if (hay.indexOf("seal") >= 0 || hay.indexOf("bind") >= 0 || hay.indexOf("blind") >= 0 || hay.indexOf("trap") >= 0 || hay.indexOf("control") >= 0) return "control";
    if (hay.indexOf("heal") >= 0 || hay.indexOf("support") >= 0 || hay.indexOf("buff") >= 0 || hay.indexOf("regen") >= 0) return "support";
    if (hay.indexOf("ultimate") >= 0 || hay.indexOf("nuke") >= 0 || hay.indexOf("raid") >= 0) return "ultimate";
    if (hay.indexOf("beam") >= 0) return "beam";
    if (hay.indexOf("projectile") >= 0 || hay.indexOf("orb") >= 0 || hay.indexOf("blast") >= 0 || hay.indexOf("barrage") >= 0) return "projectile";
    if (hay.indexOf("rush") >= 0 || hay.indexOf("melee") >= 0 || hay.indexOf("sword") >= 0 || hay.indexOf("strike") >= 0) return "melee";
    return "utility";
  }

  function inferEra(name, text) {
    var hay = (name + " " + text).toLowerCase();
    if (hay.indexOf("dbforged") >= 0) return "DBForged Draft";
    if (hay.indexOf("manga") >= 0) return "Super (manga)";
    if (hay.indexOf("super") >= 0 && hay.indexOf("z") >= 0) return "Z/Super";
    if (hay.indexOf("super") >= 0) return "Super";
    if (hay.indexOf("z") >= 0) return "Z";
    return "DBForged Draft";
  }

  function inferRace(owner, name, text) {
    var hay = (owner + " " + name + " " + text).toLowerCase();
    if (hay.indexOf("bio android") >= 0 || hay.indexOf("cell") >= 0) return "bio_android";
    if (hay.indexOf("half breed") >= 0 || hay.indexOf("hybrid") >= 0) return "half_breed";
    if (hay.indexOf("truffle") >= 0) return "truffle";
    if (hay.indexOf("grey") >= 0 || hay.indexOf("jiren") >= 0) return "grey";
    if (hay.indexOf("saiyan") >= 0 || hay.indexOf("goku") >= 0 || hay.indexOf("vegeta") >= 0 || hay.indexOf("gohan") >= 0 || hay.indexOf("trunks") >= 0) return "saiyan";
    if (hay.indexOf("human") >= 0 || hay.indexOf("krillin") >= 0 || hay.indexOf("yamcha") >= 0 || hay.indexOf("tien") >= 0 || hay.indexOf("roshi") >= 0) return "human";
    if (hay.indexOf("namekian") >= 0 || hay.indexOf("piccolo") >= 0) return "namekian";
    if (hay.indexOf("frost demon") >= 0 || hay.indexOf("frieza") >= 0 || hay.indexOf("frost ") >= 0) return "frost_demon";
    if (hay.indexOf("android") >= 0) return "android";
    if (hay.indexOf("majin") >= 0 || hay.indexOf("buu") >= 0) return "majin";
    return "";
  }

  function inferOwnerFromName(name) {
    var n = String(name || "").toLowerCase();
    if (n.indexOf("kame") >= 0 || n.indexOf("dragon fist") >= 0 || n.indexOf("spirit") >= 0) return "Shared / Saiyan";
    if (n.indexOf("galick") >= 0 || n.indexOf("final flash") >= 0 || n.indexOf("big bang") >= 0 || n.indexOf("gamma") >= 0) return "Vegeta Family";
    if (n.indexOf("special beam cannon") >= 0 || n.indexOf("hellzone") >= 0) return "Piccolo / Namekian";
    if (n.indexOf("death beam") >= 0 || n.indexOf("death ball") >= 0 || n.indexOf("supernova") >= 0) return "Frieza Family";
    if (n.indexOf("barrier") >= 0 || n.indexOf("android") >= 0) return "Android";
    if (n.indexOf("buu") >= 0 || n.indexOf("vanishing ball") >= 0 || n.indexOf("ghost") >= 0) return "Majin / Chaos";
    return "Shared Roster";
  }

  function inferTags(name, text) {
    var hay = (name + " " + text).toLowerCase();
    var tags = [];
    var checks = ["beam", "charge", "aoe", "bind", "blind", "heal", "regen", "barrier", "summon", "sword"];
    for (var i = 0; i < checks.length; i++) {
      if (hay.indexOf(checks[i]) >= 0) tags.push(checks[i]);
    }
    return tags;
  }

  function pretty(value) {
    return String(value)
      .replace(/_/g, " ")
      .replace(/\bdbforged\b/gi, "DBForged")
      .replace(/\bdbs\b/g, "DBS")
      .replace(/\b\w/g, function (m) { return m.toUpperCase(); });
  }

  function cssSafe(value) {
    return String(value || "").toLowerCase().replace(/[^a-z0-9_-]+/g, "-");
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }
})();

