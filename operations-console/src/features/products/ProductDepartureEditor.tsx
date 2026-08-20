import { DeleteOutlined, PlusOutlined } from "@ant-design/icons";
import { Button, DatePicker, Form, Input, Select, Space } from "antd";

export function ProductDepartureEditor({ vessels }: { vessels: Array<{ id: number; name: string }> }) {
  return <Form.List name="departures">{(fields, { add, remove }) => <>
    {fields.map((field) => <Space key={field.key} align="baseline" wrap>
      <Form.Item {...field} name={[field.name, "label"]} rules={[{ required: true, message: "请输入团期说明" }]}><Input placeholder="团期说明" /></Form.Item>
      <Form.Item {...field} name={[field.name, "start_date"]}><DatePicker placeholder="出发日期" /></Form.Item>
      <Form.Item {...field} name={[field.name, "end_date"]}><DatePicker placeholder="结束日期" /></Form.Item>
      <Form.Item {...field} name={[field.name, "vessel_id"]}><Select allowClear placeholder="执行船只" style={{ width: 160 }} options={vessels.map((v) => ({ value: v.id, label: v.name }))} /></Form.Item>
      <Form.Item {...field} name={[field.name, "consultation_status"]} initialValue="可咨询"><Input placeholder="咨询状态" /></Form.Item>
      <Button danger type="text" icon={<DeleteOutlined />} onClick={() => remove(field.name)} />
    </Space>)}
    <Button type="dashed" icon={<PlusOutlined />} onClick={() => add({ consultation_status: "可咨询" })}>添加团期</Button>
  </>}</Form.List>;
}
