import { Button, Card, Form, Image, Input, List, Popconfirm, Space, Upload, message } from "antd";
import type { UploadProps } from "antd";
import { deleteProductImage, uploadProductHero, uploadProductImage, type Product } from "../../api/products";

interface ProductImageEditorProps {
  product: Product;
  onChanged: () => Promise<void>;
}

const selectOnly: UploadProps["beforeUpload"] = () => false;

export function ProductImageEditor({ product, onChanged }: ProductImageEditorProps) {
  const [messageApi, holder] = message.useMessage();
  const [form] = Form.useForm<{ alt_text: string }>();

  async function uploadHero(file: File) {
    try {
      await uploadProductHero(product.id, file);
      await onChanged();
      messageApi.success("封面已更新");
    } catch {
      messageApi.error("封面上传失败");
    }
  }

  async function uploadGallery(file: File) {
    try {
      await uploadProductImage(product.id, file, form.getFieldValue("alt_text") ?? "");
      form.resetFields();
      await onChanged();
      messageApi.success("图库图片已添加");
    } catch {
      messageApi.error("图库图片上传失败");
    }
  }

  async function removeImage(imageId: number) {
    try {
      await deleteProductImage(product.id, imageId);
      await onChanged();
      messageApi.success("图片已删除");
    } catch {
      messageApi.error("图片删除失败");
    }
  }

  return <>{holder}<Space direction="vertical" size={16} style={{ width: "100%" }}>
    <Card title="产品封面">
      {product.hero_image ? <Image width={240} src={product.hero_image} alt="产品封面" /> : <p>暂未设置封面。</p>}
      <div style={{ marginTop: 12 }}><Upload accept="image/*" showUploadList={false} beforeUpload={selectOnly} onChange={({ file }) => file.originFileObj && void uploadHero(file.originFileObj)}><Button>上传或替换封面</Button></Upload></div>
    </Card>
    <Card title="图库图片">
      <Form form={form} layout="vertical"><Form.Item label="图片说明（可选）" name="alt_text"><Input placeholder="例如：登陆艇靠近冰山" /></Form.Item></Form>
      <Upload accept="image/*" showUploadList={false} beforeUpload={selectOnly} onChange={({ file }) => file.originFileObj && void uploadGallery(file.originFileObj)}><Button>添加图库图片</Button></Upload>
      <List
        style={{ marginTop: 16 }}
        dataSource={product.images ?? []}
        locale={{ emptyText: "暂无图库图片" }}
        renderItem={(item) => <List.Item actions={[<Popconfirm key="delete" title="确认删除这张图片？" onConfirm={() => void removeImage(item.id)}><Button danger type="text">删除</Button></Popconfirm>]}><Space><Image width={120} height={80} style={{ objectFit: "cover" }} src={item.image} alt={item.alt_text || "产品图库图片"} /><span>{item.alt_text || "未填写图片说明"}</span></Space></List.Item>}
      />
    </Card>
  </Space></>;
}
