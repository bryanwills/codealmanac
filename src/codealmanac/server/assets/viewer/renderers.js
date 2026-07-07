import { viewerApi } from "./api.js";
import {
  emptyState,
  fileSideLink,
  markdown,
  pageIntro,
  pageList,
  pageSideLink,
  pageTitleBlock,
  sideSection,
  sourceSideItem,
  statsGrid,
} from "./components.js";

export function renderHome(context) {
  const { elements, overview, setBreadcrumb } = context;
  const title = overview.featured_page?.title || "Wiki";
  setBreadcrumb([]);
  elements.searchInput.value = "";
  replaceMain(
    elements,
    pageIntro(
      "Local wiki",
      title,
      `${overview.page_count} pages across ${overview.topic_count} topics.`,
    ),
    statsGrid(overview),
    pageList(overview.pages),
  );
}

export async function renderPage(context, slug) {
  const { elements, setBreadcrumb, wiki } = context;
  const page = await viewerApi.page(slug, wiki);
  setBreadcrumb(pageTrail(page));

  const grid = document.createElement("div");
  grid.className = "wiki-detail-grid";

  const article = document.createElement("article");
  article.className = "wiki-page-card";
  article.append(pageTitleBlock(page), markdown(page.html, page.sources));

  const sidePanel = document.createElement("aside");
  sidePanel.className = "wiki-side-panel";
  sidePanel.setAttribute("aria-label", "Page context");
  sidePanel.append(
    sideSection("Backlinks", page.backlinks.map((item) => pageSideLink(item, item))),
    sideSection("Files", page.file_refs.map((file) => fileSideLink(file.path))),
    sideSection("Sources", page.sources.map((source) => sourceSideItem(source))),
    sideSection(
      "Related",
      page.related_pages.map((related) =>
        pageSideLink(related.slug, related.title || related.slug),
      ),
    ),
  );

  grid.append(article, sidePanel);
  replaceMain(elements, grid);
}

export async function renderTopic(context, slug) {
  const { elements, setBreadcrumb, wiki } = context;
  const topic = await viewerApi.topic(slug, wiki);
  setBreadcrumb([{ label: topic.title || topic.slug }]);
  replaceMain(
    elements,
    pageIntro("Topic", topic.title || topic.slug, topic.description || ""),
    pageList(topic.pages),
  );
}

export async function renderSearch(context, query) {
  const { elements, setBreadcrumb, wiki } = context;
  elements.searchInput.value = query;
  setBreadcrumb([{ label: query ? `Search: ${query}` : "Search" }]);
  if (!query) {
    replaceMain(
      elements,
      emptyState(
        "Search the wiki",
        "Search page titles, summaries, and page bodies in the local SQLite index.",
      ),
    );
    return;
  }
  const result = await viewerApi.search(query, wiki);
  replaceMain(
    elements,
    pageIntro("Search", query, `${result.pages.length} results`),
    pageList(result.pages),
  );
}

export async function renderFile(context, path) {
  const { elements, setBreadcrumb, wiki } = context;
  const result = await viewerApi.file(path, wiki);
  const noun = result.kind === "directory" ? "folder" : "file";
  setBreadcrumb([{ label: result.path }]);
  replaceMain(
    elements,
    pageIntro(
      `Referenced ${noun}`,
      result.path,
      `${result.pages.length} pages mention this ${noun}.`,
    ),
    pageList(result.pages),
  );
}

export function renderError(context, error) {
  const { elements, setBreadcrumb } = context;
  setBreadcrumb([{ label: "Error" }]);
  const message = document.createElement("p");
  message.className = "error";
  message.textContent = error.message;
  replaceMain(elements, pageIntro("Viewer error", "Error", ""), message);
}

function pageTrail(page) {
  const parts = page.slug.split("/").filter(Boolean);
  const folders = parts.slice(0, -1).map((name) => ({ label: name }));
  return [...folders, { label: page.title || page.slug }];
}

function replaceMain(elements, ...children) {
  elements.main.replaceChildren(...children);
  elements.main.focus();
}
