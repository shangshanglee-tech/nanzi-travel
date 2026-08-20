import { DeleteOutlined, EditOutlined, PlusOutlined } from "@ant-design/icons";
import { Button, Card, message, Popconfirm, Space, Switch, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import { useCallback, useEffect, useState } from "react";

import {
  createDestination,
  deleteDestination,
  listDestinations,
  type Destination,
  type DestinationInput,
  updateDestination
} from "../../api/destinations";
import { OperationsApiError } from "../../api/client";
import { DestinationFormModal } from "./DestinationFormModal";

function errorText(error: unknown) {
  return error instanceof OperationsApiError ? error.message : "操作未能完成，请稍后重试。";
}

export function DestinationListPage() {
  const [items, setItems] = useState<Destination[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState<Destination | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [messageApi, contextHolder] = message.useMessage();

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setItems((await listDestinations()).results);
    } catch (error) {
      messageApi.error(errorText(error));
    } finally {
      setLoading(false);
    }
  }, [messageApi]);

  useEffect(() => { void load(); }, [load]);

  async function save(values: DestinationInput) {
    setSaving(true);
    try {
      if (editing) await updateDestination(editing.id, values);
      else await createDestination(values);
      messageApi.success("已保存");
      setModalOpen(false);
      setEditing(null);
      await load();
    } catch (error) {
      messageApi.error(errorText(error));
    } finally {
      setSaving(false);
    }
  }

  async function changeActive(destination: Destination, isActive: boolean) {
    try {
      await updateDestination(destination.id, { is_active: isActive });
      await load();
    } catch (error) {
      messageApi.error(errorText(error));
    }
  }

  async function remove(destination: Destination) {
    try {
      await deleteDestination(destination.id);
      messageApi.success("已删除");
      await load();
    } catch (error) {
      messageApi.error(errorText(error));
    }
  }

  const columns: ColumnsType<Destination> = [
    { title: "目的地", dataIndex: "name" },
    { title: "英文标识", dataIndex: "slug", render: (slug) => <Typography.Text type="secondary">{slug}</Typography.Text> },
    { title: "排序", dataIndex: "sort_order", width: 100 },
    {
      title: "状态",
      dataIndex: "is_active",
      width: 130,
      render: (isActive: boolean, destination) => (
        <Space size="small"><Switch checked={isActive} onChange={(value) => void changeActive(destination, value)} /><Tag color={isActive ? "green" : "default"}>{isActive ? "启用" : "停用"}</Tag></Space>
      )
    },
    {
      title: "操作",
      width: 160,
      render: (_, destination) => (
        <Space>
          <Button type="link" icon={<EditOutlined />} onClick={() => { setEditing(destination); setModalOpen(true); }}>编辑</Button>
          <Popconfirm title="确定删除这个目的地？" okText="删除" cancelText="取消" onConfirm={() => void remove(destination)}>
            <Button type="link" danger icon={<DeleteOutlined />}>删除</Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <>
      {contextHolder}
      <Card title="目的地" extra={<Button type="primary" icon={<PlusOutlined />} onClick={() => { setEditing(null); setModalOpen(true); }}>新建目的地</Button>}>
        <Table rowKey="id" columns={columns} dataSource={items} loading={loading} pagination={false} />
      </Card>
      <DestinationFormModal
        destination={editing}
        open={modalOpen}
        saving={saving}
        onCancel={() => { setModalOpen(false); setEditing(null); }}
        onSave={(values) => void save(values)}
      />
    </>
  );
}
