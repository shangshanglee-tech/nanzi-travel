import { DeleteOutlined, PlusOutlined } from "@ant-design/icons";
import { Button, Form, Input, InputNumber, Space } from "antd";

export function ItineraryEditor() {
  return <Form.List name="itinerary_days">{(fields, { add, remove }) => <>
    {fields.map((field, index) => <div className="nested-editor-row" key={field.key}>
      <Space align="baseline" wrap>
        <Form.Item {...field} name={[field.name, "day_number"]} initialValue={index + 1} rules={[{ required: true }]}><InputNumber min={1} placeholder="天数" /></Form.Item>
        <Form.Item {...field} name={[field.name, "title"]} rules={[{ required: true, message: "请输入标题" }]}><Input placeholder="当天标题" /></Form.Item>
        <Form.Item {...field} name={[field.name, "source_range"]}><Input placeholder="官方区间" /></Form.Item>
        <Form.Item {...field} name={[field.name, "accommodation"]}><Input placeholder="住宿" /></Form.Item>
        <Form.Item {...field} name={[field.name, "meals"]}><Input placeholder="餐食" /></Form.Item>
        <Button danger type="text" icon={<DeleteOutlined />} onClick={() => remove(field.name)} />
      </Space>
      <Form.Item {...field} name={[field.name, "description"]} rules={[{ required: true, message: "请输入行程内容" }]}><Input.TextArea rows={3} placeholder="当天行程内容" /></Form.Item>
    </div>)}
    <Button type="dashed" icon={<PlusOutlined />} onClick={() => add({ day_number: fields.length + 1 })}>添加每日行程</Button>
  </>}</Form.List>;
}
