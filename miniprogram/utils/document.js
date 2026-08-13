async function loadDocument(fetchSite, field, fallback) {
  try {
    const site = await fetchSite();
    return site[field] || fallback;
  } catch (error) {
    return fallback;
  }
}

module.exports = {loadDocument};

