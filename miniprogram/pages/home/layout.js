function getHomeTopPadding(statusBarHeight = 0) {
  return Math.max(statusBarHeight + 18, 38);
}

module.exports = {getHomeTopPadding};
