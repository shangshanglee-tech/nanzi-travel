function formatDuration(days) {
  return Number.isFinite(days) && days > 0 ? `${days}天` : "";
}

module.exports = {formatDuration};

