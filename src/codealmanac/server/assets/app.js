const state = {
  overview: null,
};

const el = {
  workspaceName: document.getElementById("workspace-name"),
  routeTitle: document.getElementById("route-title"),
  searchForm: document.getElementById("search-form"),
  searchInput: document.getElementById("search-input"),
  topicList: document.getElementById("topic-list"),
  pageList: document.getElementById("page-list"),
  main: document.getElementById("main"),
  navItems: Array.from(document.querySelectorAll("[data-nav-kind]")),
};

el.searchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const query = el.searchInput.value.trim();
  window.location.hash = query ? `#/search/${encodeURIComponent(query)}` : "#/";
});

window.addEventListener("hashchange", route);
loadOverview().then(route);

async function loadOverview() {
  state.overview = await getJson("/api/overview");
  el.workspaceName.textContent = state.overview.workspace.name;
  renderNav();
}

async function route() {
  if (!state.overview) return;
  const [kind, value] = parseHash();
  setActiveNav(kind);
  try {
    if (kind === "page" && value) {
      await renderPage(value);
      return;
    }
    if (kind === "topic" && value) {
      await renderTopic(value);
      return;
    }
    if (kind === "search") {
      await renderSearch(value);
      return;
    }
    if (kind === "file" && value) {
      await renderFile(value);
      return;
    }
    renderHome();
  } catch (error) {
    renderError(error);
  }
}

function parseHash() {
  const raw = window.location.hash.replace(/^#\/?/, "");
  if (!raw) return ["home", ""];
  const parts = raw.split("/");
  return [parts[0], decodeURIComponent(parts.slice(1).join("/"))];
}

async function getJson(url) {
  const response = await fetch(url);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail?.message || `Request failed: ${response.status}`);
  }
  return data;
}

function renderNav() {
  el.topicList.replaceChildren(
    ...state.overview.topics.map((topic) =>
      navLink(`#/topic/${encodeURIComponent(topic.slug)}`, topic.title || topic.slug),
    ),
  );
  el.pageList.replaceChildren(
    ...state.overview.pages.map((page) =>
      navLink(`#/page/${encodeURIComponent(page.slug)}`, page.title || page.slug),
    ),
  );
}

function setActiveNav(kind) {
  const active = kind === "search" ? "search" : "home";
  for (const item of el.navItems) {
    item.classList.toggle("is-active", item.dataset.navKind === active);
  }
}

function setRouteTitle(title) {
  document.title = `${title} | CodeAlmanac`;
  el.routeTitle.textContent = title;
}

function renderHome() {
  const title = state.overview.featured_page?.title || "Wiki";
  setRouteTitle(title);
  el.searchInput.value = "";
  el.main.innerHTML = "";
  el.main.append(
    pageIntro(
      "Local wiki",
      title,
      `${state.overview.page_count} pages across ${state.overview.topic_count} topics.`,
    ),
    statsGrid(),
    pageList(state.overview.pages),
  );
  el.main.focus();
}

async function renderPage(slug) {
  const page = await getJson(`/api/page/${encodeURIComponent(slug)}`);
  setRouteTitle(page.title || page.slug);
  el.main.innerHTML = "";

  const grid = document.createElement("div");
  grid.className = "wiki-detail-grid";

  const article = document.createElement("article");
  article.className = "wiki-page-card";
  article.append(pageTitleBlock(page), markdown(page.html));

  const sidePanel = document.createElement("aside");
  sidePanel.className = "wiki-side-panel";
  sidePanel.setAttribute("aria-label", "Page context");
  sidePanel.append(
    sideSection("Backlinks", page.backlinks.map((item) => pageSideLink(item, item))),
    sideSection(
      "Files",
      page.file_refs.map((file) =>
        sideLink(`#/file/${encodeURIComponent(file.path)}`, file.path),
      ),
    ),
    sideSection(
      "Related",
      page.related_pages.map((related) =>
        pageSideLink(related.slug, related.title || related.slug),
      ),
    ),
  );

  grid.append(article, sidePanel);
  el.main.append(grid);
  el.main.focus();
}

async function renderTopic(slug) {
  const topic = await getJson(`/api/topic/${encodeURIComponent(slug)}`);
  setRouteTitle(topic.title || topic.slug);
  el.main.innerHTML = "";
  el.main.append(
    pageIntro("Topic", topic.title || topic.slug, topic.description || ""),
    pageList(topic.pages),
  );
  el.main.focus();
}

async function renderSearch(query) {
  el.searchInput.value = query;
  setRouteTitle(query ? `Search: ${query}` : "Search");
  if (!query) {
    el.main.innerHTML = "";
    el.main.append(
      emptyState(
        "Search the wiki",
        "Search page titles, summaries, and page bodies in the local SQLite index.",
      ),
    );
    el.main.focus();
    return;
  }
  const result = await getJson(`/api/search?q=${encodeURIComponent(query)}`);
  el.main.innerHTML = "";
  el.main.append(
    pageIntro("Search", query, `${result.pages.length} results`),
    pageList(result.pages),
  );
  el.main.focus();
}

async function renderFile(path) {
  const result = await getJson(`/api/file?path=${encodeURIComponent(path)}`);
  const noun = result.kind === "directory" ? "folder" : "file";
  setRouteTitle(result.path);
  el.main.innerHTML = "";
  el.main.append(
    pageIntro(
      `Referenced ${noun}`,
      result.path,
      `${result.pages.length} pages mention this ${noun}.`,
    ),
    pageList(result.pages),
  );
  el.main.focus();
}

function pageIntro(eyebrow, title, copy) {
  const section = document.createElement("section");
  section.className = "dashboard-page-intro";
  if (eyebrow) {
    const label = document.createElement("p");
    label.className = "dashboard-page-eyebrow";
    label.textContent = eyebrow;
    section.append(label);
  }
  const h1 = document.createElement("h1");
  h1.className = "dashboard-page-title";
  h1.textContent = title;
  section.append(h1);
  if (copy) {
    const p = document.createElement("p");
    p.className = "dashboard-page-copy";
    p.textContent = copy;
    section.append(p);
  }
  return section;
}

function statsGrid() {
  const grid = document.createElement("section");
  grid.className = "wiki-stats";
  grid.append(
    statCard(String(state.overview.page_count), "Pages"),
    statCard(String(state.overview.topic_count), "Topics"),
    statCard(state.overview.workspace.name, "Current wiki"),
  );
  return grid;
}

function statCard(value, label) {
  const card = document.createElement("div");
  card.className = "wiki-stat";
  const strong = document.createElement("strong");
  strong.textContent = value;
  const span = document.createElement("span");
  span.textContent = label;
  card.append(strong, span);
  return card;
}

function pageTitleBlock(page) {
  const header = document.createElement("header");
  header.className = "wiki-page-title-block";

  const path = document.createElement("p");
  path.className = "wiki-page-path";
  path.textContent = `${page.slug}.md`;

  const title = document.createElement("h1");
  title.className = "wiki-page-title";
  title.textContent = page.title || page.slug;

  header.append(path, title);
  if (page.summary) {
    const summary = document.createElement("p");
    summary.className = "wiki-page-summary";
    summary.textContent = page.summary;
    header.append(summary);
  }
  header.append(pageFacts(page));
  return header;
}

function pageFacts(page) {
  const row = document.createElement("div");
  row.className = "wiki-page-facts";
  const allPages = document.createElement("a");
  allPages.href = "#/";
  allPages.textContent = "All pages";
  row.append(allPages);
  for (const topic of page.topics) {
    const link = document.createElement("a");
    link.href = `#/topic/${encodeURIComponent(topic)}`;
    link.textContent = topic;
    row.append(link);
  }
  return row;
}

function markdown(html) {
  const article = document.createElement("article");
  article.className = "wiki-markdown";
  article.innerHTML = html;
  return article;
}

function pageList(pages) {
  if (pages.length === 0) {
    return emptyState("No pages found", "Try a different search or topic.");
  }
  const list = document.createElement("nav");
  list.className = "wiki-page-list";
  list.setAttribute("aria-label", "Wiki pages");
  for (const page of pages) {
    const item = document.createElement("a");
    item.className = "wiki-page-row";
    item.href = `#/page/${encodeURIComponent(page.slug)}`;

    const main = document.createElement("span");
    main.className = "wiki-page-row-main";
    const title = document.createElement("span");
    title.className = "wiki-page-row-title";
    title.textContent = page.title || page.slug;
    const summary = document.createElement("span");
    summary.className = "wiki-page-row-summary";
    summary.textContent = page.summary || "No summary";
    main.append(title, summary);

    const meta = document.createElement("span");
    meta.className = "wiki-page-row-meta";
    const slug = document.createElement("span");
    slug.textContent = `${page.slug}.md`;
    const topics = document.createElement("span");
    topics.textContent = page.topics.slice(0, 3).join(", ") || "untagged";
    meta.append(slug, topics);

    item.append(main, meta);
    list.append(item);
  }
  return list;
}

function navLink(href, label) {
  const link = document.createElement("a");
  link.href = href;
  link.textContent = label;
  return link;
}

function sideSection(title, children) {
  const section = document.createElement("section");
  section.className = "wiki-side-section";
  const heading = document.createElement("h2");
  heading.textContent = title;
  const list = document.createElement("div");
  list.className = "wiki-link-list";
  if (children.length === 0) {
    list.append(sidebarEmpty());
  } else {
    list.append(...children);
  }
  section.append(heading, list);
  return section;
}

function sideLink(href, label) {
  const link = document.createElement("a");
  link.href = href;
  link.textContent = label;
  return link;
}

function pageSideLink(slug, label) {
  return sideLink(`#/page/${encodeURIComponent(slug)}`, label);
}

function sidebarEmpty() {
  const empty = document.createElement("span");
  empty.textContent = "None";
  return empty;
}

function emptyState(title, body) {
  const box = document.createElement("section");
  box.className = "app-empty";
  const h2 = document.createElement("h2");
  h2.className = "app-empty-title";
  h2.textContent = title;
  const p = document.createElement("p");
  p.className = "app-empty-body";
  p.textContent = body;
  box.append(h2, p);
  return box;
}

function renderError(error) {
  setRouteTitle("Error");
  el.main.innerHTML = "";
  const message = document.createElement("p");
  message.className = "error";
  message.textContent = error.message;
  el.main.append(pageIntro("Viewer error", "Error", ""), message);
}
