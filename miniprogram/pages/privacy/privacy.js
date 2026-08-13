const {getSite} = require("../../services/api");
Page({data:{content:"",loading:true},onLoad(){getSite().then(site=>this.setData({content:site.privacy_text||"首版小程序不要求登录，不收集手机号，也不创建咨询表单。"})).finally(()=>this.setData({loading:false}));}});
