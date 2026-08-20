import { DeleteOutlined, EditOutlined, PlusOutlined } from "@ant-design/icons";
import { Button, Card, message, Popconfirm, Space, Table, Tag } from "antd";
import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { deleteProduct, listProducts, type Product } from "../../api/products";

export function ProductListPage() {
  const [items, setItems] = useState<Product[]>([]); const [loading, setLoading] = useState(true); const navigate = useNavigate(); const [messageApi, holder] = message.useMessage();
  const load = useCallback(async () => { setLoading(true); try { setItems((await listProducts()).results); } catch { messageApi.error("加载旅行产品失败"); } finally { setLoading(false); } }, [messageApi]);
  useEffect(() => { void load(); }, [load]);
  async function remove(item: Product) { try { await deleteProduct(item.id); messageApi.success("已删除"); await load(); } catch { messageApi.error("删除失败"); } }
  return <><>{holder}</><Card title="旅行产品" extra={<Button type="primary" icon={<PlusOutlined />} onClick={() => navigate("/products/new")}>新建产品</Button>}>
    <Table rowKey="id" loading={loading} dataSource={items} pagination={false} columns={[
      { title: "产品名称", dataIndex: "title" }, { title: "航季", dataIndex: "season" }, { title: "天数", dataIndex: "duration_days", width: 90 },
      { title: "状态", dataIndex: "status", render: (status: string) => <Tag color={status === "published" ? "green" : "default"}>{status === "published" ? "已发布" : "草稿"}</Tag> },
      { title: "操作", render: (_, item: Product) => <Space><Button type="link" icon={<EditOutlined />} onClick={() => navigate(`/products/${item.id}`)}>编辑</Button><Popconfirm title="确定删除这条产品？" onConfirm={() => void remove(item)}><Button type="link" danger icon={<DeleteOutlined />}>删除</Button></Popconfirm></Space> }
    ]} />
  </Card></>;
}
