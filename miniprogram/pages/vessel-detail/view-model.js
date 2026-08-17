function buildVesselDetailState(vessel = {}) {
  const facilities = [];
  if (vessel.year_refurbished) facilities.push({icon: "verified-badge", text: `${vessel.year_refurbished}年翻新`});
  else if (vessel.year_built) facilities.push({icon: "verified-badge", text: `建成于${vessel.year_built}年`});
  if (vessel.capacity) facilities.push({icon: "capacity", text: `最大载客量 ${vessel.capacity}`});
  if (vessel.has_science_center) facilities.push({icon: "science_center", text: "科研中心"});
  if (vessel.has_wifi) facilities.push({icon: "wifi", text: "免费 Wi-Fi"});
  if (vessel.is_hybrid) facilities.push({icon: "hybrid", text: "环保混合动力引擎"});
  if (vessel.has_stabilization_system) facilities.push({icon: "modern_stable_tech", text: "船身稳定技术"});
  if (vessel.restaurant_count) facilities.push({icon: "restaurants", text: `${vessel.restaurant_count} 个餐厅`});
  if (vessel.bar_count) facilities.push({icon: "bars", text: `${vessel.bar_count} 个酒吧`});
  if (vessel.has_executive_lounge) facilities.push({icon: "lounge", text: "行政酒廊"});
  if (vessel.has_sauna) facilities.push({icon: "spa", text: "桑拿房"});
  if (vessel.has_infinity_pool) facilities.push({icon: "swimming_pool", text: "无边泳池"});
  if (vessel.heated_pool_count) facilities.push({icon: "hot_tubs", text: `${vessel.heated_pool_count} 个恒温泳池`});
  if (vessel.has_fitness_center) facilities.push({icon: "fitness", text: "健身房"});

  return {
    facilities,
    experiences: (vessel.experiences || []).filter((item) => item.title_zh && item.body_zh),
    cabinGroups: (vessel.cabin_groups || [])
      .filter((group) => group.title_zh && (group.cabins || []).length)
      .map((group) => ({...group, title: group.title_zh || group.title_en})),
    gallery: vessel.media || [],
    products: vessel.products || [],
  };
}

module.exports = {buildVesselDetailState};
