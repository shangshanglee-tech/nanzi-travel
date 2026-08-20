import { AppstoreOutlined, EnvironmentOutlined, RocketOutlined } from "@ant-design/icons";
import { Layout, Menu, Typography } from "antd";
import { Link, Outlet, useLocation } from "react-router-dom";

const menuItems = [
  { key: "/products", icon: <RocketOutlined />, label: <Link to="/products">旅行产品</Link> },
  { key: "/destinations", icon: <EnvironmentOutlined />, label: <Link to="/destinations">目的地</Link> },
  { key: "/vessels", icon: <AppstoreOutlined />, label: <Link to="/vessels">船只</Link> }
];

export function OperationsLayout() {
  const location = useLocation();

  return (
    <Layout className="operations-layout">
      <Layout.Sider width={232} theme="light" className="operations-sidebar">
        <div className="operations-brand">小楠子爱旅行</div>
        <div className="operations-menu-label">内容配置</div>
        <Menu mode="inline" selectedKeys={[location.pathname]} items={menuItems} />
      </Layout.Sider>
      <Layout>
        <Layout.Header className="operations-header">
          <Typography.Text>运营后台</Typography.Text>
        </Layout.Header>
        <Layout.Content className="operations-content"><Outlet /></Layout.Content>
      </Layout>
    </Layout>
  );
}
