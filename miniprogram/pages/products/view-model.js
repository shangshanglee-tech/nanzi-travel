const {formatDuration} = require("../../utils/format");


function toProductCard(product) {
  return {
    ...product,
    durationLabel: formatDuration(product.duration_days),
    priceLabel: "价格咨询",
  };
}

function collectFilterOptions(products) {
  const destinations = new Map();
  const tags = new Set();
  products.forEach((product) => {
    if (product.destination && product.destination.slug) {
      destinations.set(product.destination.slug, product.destination);
    }
    (product.tags || []).forEach((tag) => tags.add(tag));
  });
  return {destinations: [...destinations.values()], tags: [...tags]};
}

function normalizeFilterOptions(filters = {}) {
  return {
    destinations: filters.destinations || [],
    months: (filters.months || []).map((value) => {
      const [year, month] = value.split("-");
      return {value, label: `${year}年${Number(month)}月`};
    }),
    durations: (filters.durations || []).map((value) => ({
      value,
      label: formatDuration(value),
    })),
    tags: filters.tags || [],
  };
}

module.exports = {toProductCard, collectFilterOptions, normalizeFilterOptions};
