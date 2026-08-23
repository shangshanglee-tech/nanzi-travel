import { Button, Card, Checkbox, Col, Form, Image, Input, InputNumber, Row, Select, Space, Spin, Tabs, message } from "antd";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { createVessel, getVessel, updateVessel, useVesselCardMediaAsset, type Vessel, type VesselInput } from "../../api/vessels";
import { PageBlockEditor } from "./PageBlockEditor";
import { CabinEditor } from "./CabinEditor";
import { DeckPlanEditor } from "./DeckPlanEditor";
import { MediaAssetPicker } from "../../components/MediaAssetPicker";

const booleanFacts: Array<[keyof VesselInput, string]> = [
  ["is_hybrid", "混合动力"], ["has_science_center", "科研中心"], ["has_wifi", "无线网络"], ["has_stabilization_system", "船身稳定技术"],
  ["has_fitness_center", "健身中心"], ["has_infinity_pool", "无边泳池"], ["has_sauna", "桑拿房"], ["has_executive_lounge", "行政酒廊"],
];

export function VesselEditorPage() {
  const { id } = useParams(); const creating = id === "new"; const navigate = useNavigate(); const [form] = Form.useForm<VesselInput>(); const [vessel, setVessel] = useState<Vessel | null>(null); const [loading, setLoading] = useState(true); const [saving, setSaving] = useState(false); const [messageApi, holder] = message.useMessage();
  async function load() { if (creating) { setLoading(false); return; } if (!id) return; setLoading(true); try { const value = await getVessel(id); setVessel(value); form.setFieldsValue(value); } catch { messageApi.error("加载船只资料失败"); } finally { setLoading(false); } }
  useEffect(() => { void load(); }, [id]);
  async function save(values: VesselInput) { setSaving(true); try { if (creating) { const created = await createVessel(values); messageApi.success("已创建"); navigate(`/vessels/${created.id}`); } else if (vessel) { await updateVessel(vessel.id, values); await load(); messageApi.success("已保存"); } } catch { messageApi.error("保存失败，请检查必填信息"); } finally { setSaving(false); } }
  async function selectCardAsset(assetId: number) { if (!vessel) return; try { await useVesselCardMediaAsset(vessel.id, assetId); await load(); messageApi.success("已使用素材库图片"); } catch { messageApi.error("素材图片设置失败"); } }
  if (loading) return <Spin />;
  if (creating) return <>{holder}<Space style={{ marginBottom: 16 }}><Button onClick={() => navigate("/vessels")}>取消</Button><Button type="primary" loading={saving} onClick={() => form.submit()}>保存</Button></Space><Form form={form} layout="vertical" onFinish={(values) => void save(values)} initialValues={{ content_status: "draft" }}><Card title="新建船只"><Row gutter={16}><Col span={12}><Form.Item label="中文名称" name="name" rules={[{ required: true }]}><Input /></Form.Item></Col><Col span={12}><Form.Item label="官方名称" name="official_name"><Input /></Form.Item></Col><Col span={12}><Form.Item label="英文标识" name="slug" rules={[{ required: true }]}><Input /></Form.Item></Col><Col span={12}><Form.Item label="所属公司" name="operator_name"><Input /></Form.Item></Col></Row><Form.Item label="中文简介" name="summary"><Input.TextArea rows={3} /></Form.Item></Card></Form></>;
  if (!vessel) return <Spin />;
  return <>{holder}<Space style={{ marginBottom: 16 }}><Button onClick={() => navigate("/vessels")}>返回列表</Button><Button type="primary" loading={saving} onClick={() => form.submit()}>保存</Button></Space><Form form={form} layout="vertical" onFinish={(values) => void save(values)}><Tabs items={[
    { key: "basic", label: "基础信息", children: <Card><Row gutter={16}><Col span={12}><Form.Item label="中文名称" name="name" rules={[{ required: true }]}><Input /></Form.Item></Col><Col span={12}><Form.Item label="官方名称" name="official_name"><Input /></Form.Item></Col><Col span={12}><Form.Item label="英文标识" name="slug" rules={[{ required: true }]}><Input /></Form.Item></Col><Col span={12}><Form.Item label="所属公司" name="operator_name"><Input /></Form.Item></Col><Col span={12}><Form.Item label="发布状态" name="content_status"><Select options={[{ value: "draft", label: "草稿" }, { value: "published", label: "已发布" }]} /></Form.Item></Col><Col span={12}><Form.Item label="排序" name="sort_order"><InputNumber min={0} /></Form.Item></Col></Row><Form.Item label="中文简介" name="summary"><Input.TextArea rows={3} /></Form.Item><Form.Item label="中文完整介绍" name="intro_zh"><Input.TextArea rows={7} /></Form.Item></Card> },
    { key: "card", label: "首页卡片", children: <Card><Form.Item label="卡片底色" name="card_tone" rules={[{ pattern: /^#[0-9A-Fa-f]{6}$/, message: "请输入 #071A32 格式色值" }]}><Input placeholder="#071A32" /></Form.Item>{vessel.card_image ? <Image width={280} src={vessel.card_image} alt="船只卡片图" /> : <p>暂未设置卡片图。</p>}<div style={{ marginTop: 16 }}><MediaAssetPicker onSelect={(asset) => void selectCardAsset(asset.id)} /></div></Card> },
    { key: "facts", label: "结构化事实", children: <Card><Row gutter={16}><Col span={8}><Form.Item label="最大载客量" name="capacity"><InputNumber min={0} /></Form.Item></Col><Col span={8}><Form.Item label="建造年份" name="year_built"><InputNumber min={1800} max={2200} /></Form.Item></Col><Col span={8}><Form.Item label="翻新年份" name="year_refurbished"><InputNumber min={1800} max={2200} /></Form.Item></Col><Col span={8}><Form.Item label="餐厅数量" name="restaurant_count"><InputNumber min={0} /></Form.Item></Col><Col span={8}><Form.Item label="酒吧数量" name="bar_count"><InputNumber min={0} /></Form.Item></Col><Col span={8}><Form.Item label="恒温泳池数量" name="heated_pool_count"><InputNumber min={0} /></Form.Item></Col></Row><Row gutter={[16, 12]}>{booleanFacts.map(([key, label]) => <Col span={8} key={key}><Form.Item name={key} valuePropName="checked" noStyle><Checkbox>{label}</Checkbox></Form.Item></Col>)}</Row></Card> },
    { key: "page-content", label: "页面内容", children: <Card><PageBlockEditor vesselId={vessel.id} /></Card> },
    { key: "cabins", label: "舱位", children: <Card><CabinEditor vesselId={vessel.id} /></Card> },
    { key: "deck-plans", label: "甲板图", children: <Card><DeckPlanEditor vesselId={vessel.id} /></Card> },
  ]} /></Form></>;
}
