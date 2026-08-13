const {getSite} = require("../../services/api");
Page({data:{content:"",loading:true},onLoad(){getSite().then(site=>this.setData({content:site.agreement_text||"小程序展示的旅行信息用于咨询参考，具体服务内容以双方最终确认文件为准。"})).finally(()=>this.setData({loading:false}));}});
