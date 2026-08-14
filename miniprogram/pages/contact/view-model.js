function buildConsultationCopy(productTitle, departure, vessel) {
  if (!productTitle && !vessel) return "我想咨询小楠子的旅行产品";
  const lines = [productTitle ? `我想咨询：${productTitle}` : `我想咨询：${vessel}`];
  if (departure) lines.push(`团期：${departure}`);
  if (vessel && productTitle) lines.push(`执行船只：${vessel}`);
  return lines.join("\n");
}

function buildContactState(site, productTitle, departure, vessel) {
  const sessionBits = [];
  if (productTitle) sessionBits.push(`产品=${productTitle}`);
  if (departure) sessionBits.push(`团期=${departure}`);
  if (vessel) sessionBits.push(`船只=${vessel}`);
  return {
    officialAccountName: site.official_account_name || "小楠子爱旅行俱乐部",
    officialAccountGuide:
      site.official_account_guide ||
      "请在微信中搜索公众号名称并关注，获取人工咨询服务。",
    consultationCopy: buildConsultationCopy(productTitle, departure, vessel),
    sessionFrom: sessionBits.join("；") || "咨询来源=小楠子爱旅行",
  };
}

module.exports = {buildConsultationCopy, buildContactState};
