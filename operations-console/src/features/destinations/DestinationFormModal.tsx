import { Form, Input, InputNumber, Modal, Switch } from "antd";
import { useEffect } from "react";

import type { Destination, DestinationInput } from "../../api/destinations";

interface DestinationFormModalProps {
  destination: Destination | null;
  open: boolean;
  saving: boolean;
  onCancel(): void;
  onSave(values: DestinationInput): void;
}

export function DestinationFormModal({ destination, open, saving, onCancel, onSave }: DestinationFormModalProps) {
  const [form] = Form.useForm<DestinationInput>();

  useEffect(() => {
    form.setFieldsValue(destination ?? { name: "", slug: "", is_active: true, sort_order: 0 });
  }, [destination, form, open]);

  return (
    <Modal
      open={open}
      title={destination ? "编辑目的地" : "新建目的地"}
      okText="保存"
      cancelText="取消"
      confirmLoading={saving}
      destroyOnHidden
      onCancel={onCancel}
      onOk={() => form.submit()}
    >
      <Form form={form} layout="vertical" onFinish={onSave} requiredMark={false}>
        <Form.Item label="目的地名称" name="name" rules={[{ required: true, message: "请输入目的地名称" }]}>
          <Input maxLength={80} />
        </Form.Item>
        <Form.Item label="英文标识" name="slug" rules={[{ required: true, message: "请输入英文标识" }]}>
          <Input maxLength={80} />
        </Form.Item>
        <Form.Item label="排序" name="sort_order">
          <InputNumber min={0} precision={0} style={{ width: "100%" }} />
        </Form.Item>
        <Form.Item label="启用" name="is_active" valuePropName="checked">
          <Switch checkedChildren="启用" unCheckedChildren="停用" />
        </Form.Item>
      </Form>
    </Modal>
  );
}
