import { EditOutlined } from "@ant-design/icons";
import { Button, Card, Space, Table, Tag } from "antd";
import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { listVessels, type Vessel } from "../../api/vessels";

export function VesselListPage() {
  const [items, setItems] = useState<Vessel[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const load = useCallback(async () => { setLoading(true); try { setItems((await listVessels()).results); } finally { setLoading(false); } }, []);
  useEffect(() => { void load(); }, [load]);
  return <Card title="船只"><Table rowKey="id" loading={loading} dataSource={items} pagination={false} columns={[
    { title: "中文名称", dataIndex: "name" }, { title: "官方名称", dataIndex: "official_name" }, { title: "所属公司", dataIndex: "operator_name" },
    { title: "状态", dataIndex: "content_status", render: (value: string) => <Tag color={value === "published" ? "green" : "default"}>{value === "published" ? "已发布" : "草稿"}</Tag> },
    { title: "操作", render: (_, item: Vessel) => <Space><Button type="link" icon={<EditOutlined />} onClick={() => navigate(`/vessels/${item.id}`)}>编辑</Button></Space> },
  ]} /></Card>;
}
