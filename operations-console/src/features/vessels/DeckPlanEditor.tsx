import { DeleteOutlined, PlusOutlined } from "@ant-design/icons";
import { Button, Form, Image, Input, List, Modal, Popconfirm, Upload, message } from "antd";
import type { UploadProps } from "antd";
import { useCallback, useEffect, useState } from "react";
import { createDeckPlan, deleteDeckPlan, listDeckPlans, type DeckPlan } from "../../api/vessels";

const selectOnly: UploadProps["beforeUpload"] = () => false;

export function DeckPlanEditor({ vesselId }: { vesselId: number }) {
  const [items, setItems] = useState<DeckPlan[]>([]); const [open, setOpen] = useState(false); const [file, setFile] = useState<File | null>(null); const [form] = Form.useForm<{ title: string }>(); const [messageApi, holder] = message.useMessage();
  const load = useCallback(async () => { try { setItems((await listDeckPlans(vesselId)).results); } catch { messageApi.error("加载甲板示意图失败"); } }, [messageApi, vesselId]);
  useEffect(() => { void load(); }, [load]);
  async function save({ title }: { title: string }) { if (!file) { messageApi.error("请选择甲板示意图文件"); return; } try { await createDeckPlan(vesselId, title, file); setOpen(false); await load(); messageApi.success("甲板示意图已添加"); } catch { messageApi.error("保存失败，请上传 SVG、PNG、JPG 或 WEBP 文件"); } }
  async function remove(item: DeckPlan) { try { await deleteDeckPlan(vesselId, item.id); await load(); messageApi.success("已删除"); } catch { messageApi.error("删除失败"); } }
  return <>{holder}<Button type="primary" icon={<PlusOutlined />} onClick={() => { form.resetFields(); setFile(null); setOpen(true); }} style={{ marginBottom: 16 }}>添加甲板示意图</Button><List bordered dataSource={items} locale={{ emptyText: "暂无甲板示意图" }} renderItem={(item) => <List.Item actions={[<Popconfirm key="delete" title="确定删除这张甲板示意图？" onConfirm={() => void remove(item)}><Button danger type="link" icon={<DeleteOutlined />}>删除</Button></Popconfirm>]}><Image width={200} height={150} style={{ objectFit: "contain", background: "#fff" }} src={item.image} alt={item.title} /><strong>{item.title || "未命名甲板"}</strong></List.Item>} />
    <Modal title="添加甲板示意图" open={open} onCancel={() => setOpen(false)} onOk={() => form.submit()} destroyOnHidden><Form form={form} layout="vertical" onFinish={(values) => void save(values)}><Form.Item label="甲板名称" name="title" rules={[{ required: true }]}><Input placeholder="例如：Deck 3" /></Form.Item><Form.Item label="甲板示意图（SVG、PNG、JPG、WEBP）" required><Upload accept=".svg,.png,.jpg,.jpeg,.webp" maxCount={1} beforeUpload={selectOnly} onChange={({ file }) => setFile(file.originFileObj ?? null)}><Button>选择文件</Button></Upload></Form.Item></Form></Modal></>;
}
