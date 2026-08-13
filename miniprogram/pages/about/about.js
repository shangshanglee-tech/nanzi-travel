const {getSite} = require("../../services/api");
Page({data:{content:"",loading:true},onLoad(){getSite().then(site=>this.setData({content:site.about_us||site.brand_summary||"小楠子爱旅行，专注值得出发的旅行体验。"})).finally(()=>this.setData({loading:false}));}});
