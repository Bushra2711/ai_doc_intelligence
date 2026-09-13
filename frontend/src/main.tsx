import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./styles/globals.css";
import "./styles/confidence.css";
import "./styles/dashboard-analytics.css";
import "./styles/audit-trail.css";
import "./styles/calm-ui.css";
import "./styles/reference-ui.css";
import "./styles/upload-reference.css";
import "./styles/reference-order.css";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode><BrowserRouter><App /></BrowserRouter></React.StrictMode>
);
