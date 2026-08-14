const path = require("node:path");

function buildUploadConfig({appid, privateKeyPath, runNumber, sha}) {
  if (!appid || !privateKeyPath || !runNumber || !sha) {
    throw new Error("WECHAT_APPID, WECHAT_PRIVATE_KEY_PATH, GITHUB_RUN_NUMBER and GITHUB_SHA are required");
  }
  return {
    appid,
    privateKeyPath,
    version: `0.1.${runNumber}`,
    desc: `release ${sha.slice(0, 7)}`,
  };
}

async function uploadExperience() {
  const config = buildUploadConfig({
    appid: process.env.WECHAT_APPID,
    privateKeyPath: process.env.WECHAT_PRIVATE_KEY_PATH,
    runNumber: process.env.GITHUB_RUN_NUMBER,
    sha: process.env.GITHUB_SHA,
  });
  const ci = require("miniprogram-ci");
  await ci.upload({
    project: new ci.Project({
      appid: config.appid,
      type: "miniProgram",
      projectPath: path.resolve(__dirname, "../miniprogram"),
      privateKeyPath: config.privateKeyPath,
      ignores: ["node_modules/**/*"],
    }),
    version: config.version,
    desc: config.desc,
    setting: {es6: true, minify: true},
    onProgressUpdate: () => {},
  });
  console.log(`WeChat experience build uploaded: ${config.version} (${config.desc})`);
}

if (require.main === module) {
  uploadExperience().catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
  });
}

module.exports = {buildUploadConfig, uploadExperience};
