export const RouteKind = Object.freeze({
  HOME: "home",
  PAGE: "page",
  TOPIC: "topic",
  SEARCH: "search",
  FILE: "file",
});

export function parseHash(hash) {
  const raw = hash.replace(/^#\/?/, "");
  if (!raw) return { kind: RouteKind.HOME, value: "" };
  const parts = raw.split("/");
  const kind = parts[0];
  const value = decodeURIComponent(parts.slice(1).join("/"));
  return { kind, value };
}

export function homeHref() {
  return "#/";
}

export function pageHref(slug) {
  return `#/page/${encodeURIComponent(slug)}`;
}

export function topicHref(slug) {
  return `#/topic/${encodeURIComponent(slug)}`;
}

export function searchHref(query) {
  return query ? `#/search/${encodeURIComponent(query)}` : homeHref();
}

export function fileHref(path) {
  return `#/file/${encodeURIComponent(path)}`;
}
