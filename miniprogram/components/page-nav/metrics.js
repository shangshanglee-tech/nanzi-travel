function getNavigationMetrics(capsule, statusBarHeight = 0, windowWidth = 375) {
  const safeGap = Math.max(windowWidth - (capsule && capsule.right ? capsule.right : windowWidth), 8);
  return {
    topPadding: statusBarHeight,
    height: Math.max((capsule && capsule.height ? capsule.height : 32) + 12, 44),
    rightPadding: safeGap + 8,
  };
}

module.exports = {getNavigationMetrics};
