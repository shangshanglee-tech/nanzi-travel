function buildVesselDetailState(vessel = {}) {
  const facts = [];
  if (vessel.capacity) facts.push({label: "载客", value: `约 ${vessel.capacity} 位`});
  if (vessel.year_built) facts.push({label: "建造", value: `${vessel.year_built} 年`});
  if (vessel.year_refurbished) facts.push({label: "翻新", value: `${vessel.year_refurbished} 年`});

  return {
    facts,
    experiences: (vessel.experiences || []).filter((item) => item.title_zh && item.body_zh),
    cabinGroups: (vessel.cabin_groups || [])
      .filter((group) => group.title_zh && (group.cabins || []).length)
      .map((group) => ({...group, title: group.title_zh || group.title_en})),
    gallery: vessel.media || [],
    products: vessel.products || [],
  };
}

module.exports = {buildVesselDetailState};
