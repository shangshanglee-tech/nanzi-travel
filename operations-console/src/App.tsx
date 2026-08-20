import { Result } from "antd";
import { useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import { operationsRequest } from "./api/client";
import { LoginPage } from "./features/auth/LoginPage";
import { DestinationListPage } from "./features/destinations/DestinationListPage";
import { OperationsLayout } from "./layout/OperationsLayout";

function PlaceholderPage({ title }: { title: string }) {
  return <Result status="info" title={title} subTitle="内容管理功能正在接入。" />;
}

export default function App() {
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    operationsRequest<{ username: string }>("auth/me")
      .then(() => setAuthenticated(true))
      .catch(() => setAuthenticated(false));
  }, []);

  if (authenticated === null) return null;
  if (!authenticated) return <LoginPage onLogin={() => setAuthenticated(true)} />;

  return (
    <Routes>
      <Route element={<OperationsLayout />}>
        <Route path="/products" element={<PlaceholderPage title="旅行产品" />} />
        <Route path="/destinations" element={<DestinationListPage />} />
        <Route path="/vessels" element={<PlaceholderPage title="船只" />} />
        <Route path="*" element={<Navigate to="/products" replace />} />
      </Route>
    </Routes>
  );
}
