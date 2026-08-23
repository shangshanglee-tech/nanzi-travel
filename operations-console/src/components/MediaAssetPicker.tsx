import { PlusOutlined } from "@ant-design/icons";
import { Button, Card, Form, Image, Input, List, Modal, Space, Upload } from "antd";
import { useCallback, useEffect, useState } from "react";
import { listMediaAssets, uploadMediaAsset, type MediaAsset } from "../api/mediaAssets";

interface MediaAssetPickerProps { onSelect(asset: MediaAsset): void; }

export function MediaAssetPicker({ onSelect }: MediaAssetPickerProps) {
  const [open, setOpen] = useState(false); const [assets, setAssets] = useState<MediaAsset[]>([]); const [form] = Form.useForm<{ title: string; tags: string }>(); const [file, setFile] = useState<File | null>(null);
  const load = useCallback(async () => setAssets((await listMediaAssets()).results), []);
  useEffect(() => { if (open) void load(); }, [load, open]);
  async function upload(values: { title: string; tags: string }) { if (!file) return; const asset = await uploadMediaAsset(file, values.title, values.tags); setFile(null); form.resetFields(); await load(); onSelect(asset); setOpen(false); }
  return <><Button onClick={() => setOpen(true)}>从素材库选择</Button><Modal title="选择素材" open={open} onCancel={() => setOpen(false)} footer={null} width={760} destroyOnHidden><Card size="small" title="上传新素材" style={{ marginBottom: 16 }}><Form form={form} layout="inline" onFinish={(values) => void upload(values)}><Form.Item name="title"><Input placeholder="素材名称" /></Form.Item><Form.Item name="tags"><Input placeholder="标签，用逗号分隔" /></Form.Item><Upload beforeUpload={(selected) => { setFile(selected); return false; }} maxCount={1}><Button icon={<PlusOutlined />}>上传新素材</Button></Upload><Button type="primary" htmlType="submit" disabled={!file}>保存并使用</Button></Form></Card><List grid={{ gutter: 12, column: 4 }} dataSource={assets} locale={{ emptyText: "素材库暂时没有图片" }} renderItem={(asset) => <List.Item><Card hoverable cover={<Image preview={false} height={110} style={{ objectFit: "cover" }} src={asset.image} />} onClick={() => { onSelect(asset); setOpen(false); }}><Space direction="vertical" size={0}><strong>{asset.title || "未命名素材"}</strong><span>{asset.tags.join(" · ")}</span></Space></Card></List.Item>} /></Modal></>;
}
