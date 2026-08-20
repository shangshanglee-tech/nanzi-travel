import { LockOutlined, UserOutlined } from "@ant-design/icons";
import { Alert, Button, Card, Form, Input, Typography } from "antd";
import { useState } from "react";

import { OperationsApiError, operationsRequest } from "../../api/client";

interface LoginPageProps {
  onLogin(): void;
}

export function LoginPage({ onLogin }: LoginPageProps) {
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function submit(values: { username: string; password: string }) {
    setSubmitting(true);
    setError("");
    try {
      await operationsRequest("auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values)
      });
      onLogin();
    } catch (requestError) {
      setError(requestError instanceof OperationsApiError ? requestError.message : "暂时无法登录，请稍后重试。");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="login-page">
      <Card className="login-card" bordered={false}>
        <Typography.Title level={2}>小楠子爱旅行</Typography.Title>
        <Typography.Paragraph type="secondary">运营后台</Typography.Paragraph>
        {error && <Alert type="error" showIcon message={error} className="login-error" />}
        <Form layout="vertical" onFinish={submit} requiredMark={false}>
          <Form.Item name="username" label="账号" rules={[{ required: true, message: "请输入账号" }]}>
            <Input prefix={<UserOutlined />} autoComplete="username" />
          </Form.Item>
          <Form.Item name="password" label="密码" rules={[{ required: true, message: "请输入密码" }]}>
            <Input.Password prefix={<LockOutlined />} autoComplete="current-password" />
          </Form.Item>
          <Button type="primary" htmlType="submit" block loading={submitting}>登录</Button>
        </Form>
      </Card>
    </main>
  );
}
