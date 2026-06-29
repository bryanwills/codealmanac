export const viewerApi = {
  overview() {
    return getJson("/api/overview");
  },

  page(slug) {
    return getJson(`/api/page/${encodeURIComponent(slug)}`);
  },

  search(query) {
    return getJson(`/api/search?q=${encodeURIComponent(query)}`);
  },

  topic(slug) {
    return getJson(`/api/topic/${encodeURIComponent(slug)}`);
  },

  file(path) {
    return getJson(`/api/file?path=${encodeURIComponent(path)}`);
  },
};

async function getJson(url) {
  const response = await fetch(url);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail?.message || `Request failed: ${response.status}`);
  }
  return data;
}
