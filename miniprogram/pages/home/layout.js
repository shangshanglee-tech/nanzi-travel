function getHomeTopPadding(statusBarHeight = 0) {
  return Math.max(statusBarHeight + 30, 50);
}

module.exports = {getHomeTopPadding};
