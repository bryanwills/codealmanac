import { viewerApi } from "./api.js";
import { navLink } from "./components.js";
import { clearJobPolling, renderJob, renderJobs } from "./jobs.js";
import {
  renderError,
  renderFile,
  renderHome,
  renderPage,
  renderSearch,
  renderTopic,
} from "./renderers.js";
import {
  homeHref,
  pageHref,
  parseHash,
  RouteKind,
  searchHref,
  topicHref,
} from "./routes.js";

const state = {
  overview: null,
  selectedRepository: "",
};

const FOLDER_TITLE_WORDS = new Map([
  ["ai", "AI"],
  ["rls", "RLS"],
]);

const FOLDER_SORT_PRIORITY = new Map([["start-here", -1]]);

export function startViewer() {
  const elements = readElements();
  elements.searchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    window.location.hash = searchHref(elements.searchInput.value.trim());
  });
  elements.repositorySelect.addEventListener("change", async () => {
    clearJobPolling();
    state.selectedRepository = elements.repositorySelect.value;
    await loadOverview(elements, state.selectedRepository);
    await route(elements);
  });

  window.addEventListener("hashchange", () => route(elements));
  loadOverview(elements).then(() => route(elements));
}

async function loadOverview(elements, wiki = state.selectedRepository) {
  state.overview = await viewerApi.overview(wiki);
  state.selectedRepository = state.overview.repository.name;
  renderRepositoryOptions(elements, state.overview);
  renderNav(elements, state.overview);
}

async function route(elements) {
  if (!state.overview) return;
  clearJobPolling();
  const context = {
    elements,
    overview: state.overview,
    wiki: state.selectedRepository,
    setBreadcrumb: (trail) => renderBreadcrumb(elements, trail),
  };
  try {
    const routeState = parseHash(window.location.hash);
    setActiveNav(elements, routeState);
    if (routeState.kind === RouteKind.PAGE && routeState.value) {
      await renderPage(context, routeState.value);
      return;
    }
    if (routeState.kind === RouteKind.TOPIC && routeState.value) {
      await renderTopic(context, routeState.value);
      return;
    }
    if (routeState.kind === RouteKind.SEARCH) {
      await renderSearch(context, routeState.value);
      return;
    }
    if (routeState.kind === RouteKind.FILE && routeState.value) {
      await renderFile(context, routeState.value);
      return;
    }
    if (routeState.kind === RouteKind.JOBS) {
      await renderJobs(context);
      return;
    }
    if (routeState.kind === RouteKind.JOB && routeState.value) {
      await renderJob(context, routeState.value);
      return;
    }
    renderHome(context);
  } catch (error) {
    renderError(context, error);
  }
}

function readElements() {
  return {
    repositorySelect: document.getElementById("repository-select"),
    routeCrumb: document.getElementById("route-crumb"),
    searchForm: document.getElementById("search-form"),
    searchInput: document.getElementById("search-input"),
    topicList: document.getElementById("topic-list"),
    pageList: document.getElementById("page-list"),
    main: document.getElementById("main"),
    navItems: Array.from(document.querySelectorAll("[data-nav-kind]")),
    railLinks: () => Array.from(document.querySelectorAll("[data-rail-kind]")),
  };
}

function renderRepositoryOptions(elements, overview) {
  elements.repositorySelect.replaceChildren(
    ...overview.repositories.map((repository) => {
      const option = document.createElement("option");
      option.value = repository.name;
      option.textContent = repository.name;
      return option;
    }),
  );
  elements.repositorySelect.value = overview.repository.name;
  elements.repositorySelect.disabled = overview.repositories.length <= 1;
}

function renderNav(elements, overview) {
  elements.topicList.replaceChildren(
    ...overview.topics.map((topic) =>
      navLink(topicHref(topic.slug), topic.title || topic.slug, {
        kind: RouteKind.TOPIC,
        value: topic.slug,
        title: `${topic.page_count} pages`,
      }),
    ),
  );
  elements.pageList.replaceChildren(
    ...pageTree(overview.navigation_pages || overview.pages),
  );
}

function pageTree(pages) {
  const root = createFolderNode("");
  for (const page of pages) {
    insertPage(root, page);
  }
  return renderFolderChildren(root, 0);
}

function createFolderNode(name) {
  return {
    name,
    folders: new Map(),
    pages: [],
  };
}

function insertPage(root, page) {
  const path = page.path || `${page.slug}.md`;
  const parts = path.split("/").filter(Boolean);
  const filename = parts.pop() || `${page.slug}.md`;
  let cursor = root;
  for (const part of parts) {
    if (!cursor.folders.has(part)) {
      cursor.folders.set(part, createFolderNode(part));
    }
    cursor = cursor.folders.get(part);
  }
  cursor.pages.push({ ...page, filename });
}

function renderFolderChildren(folder, depth) {
  const children = [];
  for (const child of sortedFolders(folder)) {
    children.push(renderFolder(child, depth));
  }
  for (const page of sortedPages(folder.pages)) {
    children.push(renderPageLink(page, depth));
  }
  return children;
}

function renderFolder(folder, depth) {
  const details = document.createElement("details");
  details.className = "wiki-rail-folder";

  const summary = document.createElement("summary");
  summary.className = "wiki-rail-folder-summary";
  setRailIndent(summary, depth);
  summary.textContent = folderTitle(folder.name);

  const children = document.createElement("div");
  children.className = "wiki-rail-folder-children";
  children.append(...renderFolderChildren(folder, depth + 1));

  details.append(summary, children);
  return details;
}

function renderPageLink(page, depth) {
  const link = navLink(pageHref(page.slug), page.title || page.slug, {
    kind: RouteKind.PAGE,
    value: page.slug,
    title: page.summary || page.path || `${page.slug}.md`,
  });
  link.classList.add("wiki-rail-page");
  setRailIndent(link, depth);
  return link;
}

function setRailIndent(element, depth) {
  element.style.setProperty("--rail-indent", `${depth * 14}px`);
}

function sortedFolders(folder) {
  return Array.from(folder.folders.values()).sort(compareFolders);
}

function sortedPages(pages) {
  return [...pages].sort((a, b) => {
    const aTitle = a.title || a.filename || a.slug;
    const bTitle = b.title || b.filename || b.slug;
    return aTitle.localeCompare(bTitle);
  });
}

function folderTitle(name) {
  return name
    .split(/[-_]/)
    .filter(Boolean)
    .map((part) => FOLDER_TITLE_WORDS.get(part) || titleWord(part))
    .join(" ");
}

function compareFolders(a, b) {
  const priority = folderPriority(a.name) - folderPriority(b.name);
  if (priority !== 0) return priority;
  return folderTitle(a.name).localeCompare(folderTitle(b.name));
}

function folderPriority(name) {
  return FOLDER_SORT_PRIORITY.get(name) || 0;
}

function titleWord(value) {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function setActiveNav(elements, routeState) {
  const active = activeNavKind(routeState);
  for (const item of elements.navItems) {
    item.classList.toggle("is-active", item.dataset.navKind === active);
  }
  for (const link of elements.railLinks()) {
    const routeMatches =
      link.dataset.railKind === routeState.kind &&
      link.dataset.railValue === routeState.value;
    link.classList.toggle("is-active", routeMatches);
  }
}

function activeNavKind(routeState) {
  if (
    routeState.kind === RouteKind.HOME ||
    routeState.kind === RouteKind.SEARCH ||
    routeState.kind === RouteKind.JOBS
  ) {
    return routeState.kind;
  }
  if (routeState.kind === RouteKind.JOB) {
    return RouteKind.JOBS;
  }
  return "";
}

function renderBreadcrumb(elements, trail) {
  const leaf = trail[trail.length - 1];
  document.title = leaf ? `${leaf.label} | CodeAlmanac` : "CodeAlmanac";

  const crumbs = [{ label: "CodeAlmanac", href: homeHref() }, ...trail];
  const nodes = [];
  crumbs.forEach((crumb, index) => {
    if (index > 0) nodes.push(crumbSeparator());
    nodes.push(crumbNode(crumb, index === crumbs.length - 1));
  });
  elements.routeCrumb.replaceChildren(...nodes);
}

function crumbNode(crumb, isCurrent) {
  if (!isCurrent && crumb.href) {
    const link = document.createElement("a");
    link.className = "dashboard-crumb";
    link.href = crumb.href;
    link.textContent = crumb.label;
    return link;
  }
  const span = document.createElement("span");
  span.className = "dashboard-crumb";
  if (isCurrent) {
    span.classList.add("is-current");
    span.setAttribute("aria-current", "page");
  }
  span.textContent = crumb.label;
  return span;
}

function crumbSeparator() {
  const sep = document.createElement("span");
  sep.className = "dashboard-crumb-sep";
  sep.setAttribute("aria-hidden", "true");
  sep.textContent = "›";
  return sep;
}
