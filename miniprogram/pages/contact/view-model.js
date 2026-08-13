function buildConsultationCopy(productTitle) {
  return productTitle ? `我想咨询：${productTitle}` : "我想咨询小楠子的旅行产品";
}

function buildContactState(site, productTitle) {
  return {
    officialAccountName: site.official_account_name || "小楠子爱旅行俱乐部",
    officialAccountGuide:
      site.official_account_guide ||
      "请在微信中搜索公众号名称并关注，获取人工咨询服务。",
    consultationCopy: buildConsultationCopy(productTitle),
  };
}

module.exports = {buildConsultationCopy, buildContactState};

