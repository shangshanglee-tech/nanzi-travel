import "antd/dist/reset.css";
import "./styles.css";

import { ConfigProvider } from "antd";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import App from "./App";

createRoot(document.getElementById("operations-console")!).render(
  <ConfigProvider theme={{ token: { colorPrimary: "#1677ff", borderRadius: 6 } }}>
    <BrowserRouter><App /></BrowserRouter>
  </ConfigProvider>
);
