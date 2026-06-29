import { viewerApi } from "./api.js";
import { navLink } from "./components.js";
import {
  renderError,
  renderFile,
  renderHome,
  renderPage,
  renderSearch,
  renderTopic,
} from "./renderers.js";
import {
  pageHref,
  parseHash,
  RouteKind,
  searchHref,
  topicHref,
} from "./routes.js";

const state = {
  overview: null,
};

export function startViewer() {
  const elements = readElements();
  elements.searchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    window.location.hash = searchHref(elements.searchInput.value.trim());
  });

  window.addEventListener("hashchange", () => route(elements));
  loadOverview(elements).then(() => route(elements));
}

async function loadOverview(elements) {
  state.overview = await viewerApi.overview();
  elements.workspaceName.textContent = state.overview.workspace.name;
  renderNav(elements, state.overview);
}

async function route(elements) {
  if (!state.overview) return;
  const context = {
    elements,
    overview: state.overview,
    setRouteTitle: (title) => setRouteTitle(elements, title),
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
    renderHome(context);
  } catch (error) {
    renderError(context, error);
  }
}

function readElements() {
  return {
    workspaceName: document.getElementById("workspace-name"),
    routeTitle: document.getElementById("route-title"),
    searchForm: document.getElementById("search-form"),
    searchInput: document.getElementById("search-input"),
    topicList: document.getElementById("topic-list"),
    pageList: document.getElementById("page-list"),
    main: document.getElementById("main"),
    navItems: Array.from(document.querySelectorAll("[data-nav-kind]")),
    railLinks: () => Array.from(document.querySelectorAll("[data-rail-kind]")),
  };
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
    ...overview.pages.map((page) =>
      navLink(pageHref(page.slug), page.title || page.slug, {
        kind: RouteKind.PAGE,
        value: page.slug,
        title: page.summary || `${page.slug}.md`,
      }),
    ),
  );
}

function setActiveNav(elements, routeState) {
  const active =
    routeState.kind === RouteKind.HOME || routeState.kind === RouteKind.SEARCH
      ? routeState.kind
      : "";
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

function setRouteTitle(elements, title) {
  document.title = `${title} | CodeAlmanac`;
  elements.routeTitle.textContent = title;
}
