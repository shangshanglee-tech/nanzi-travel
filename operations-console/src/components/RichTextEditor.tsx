import { BoldOutlined, OrderedListOutlined, UnorderedListOutlined } from "@ant-design/icons";
import { Button, Space } from "antd";
import { useEffect, useRef } from "react";

interface RichTextEditorProps {
  value?: string;
  onChange?(value: string): void;
}

export function RichTextEditor({ value = "", onChange }: RichTextEditorProps) {
  const editorRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (editorRef.current && editorRef.current.innerHTML !== value) editorRef.current.innerHTML = value;
  }, [value]);

  function command(name: string, commandValue?: string) {
    editorRef.current?.focus();
    document.execCommand(name, false, commandValue);
    onChange?.(editorRef.current?.innerHTML ?? "");
  }

  return <div>
    <Space size={4} style={{ marginBottom: 8 }}>
      <Button size="small" icon={<BoldOutlined />} onClick={() => command("bold")}>加粗</Button>
      <Button size="small" onClick={() => command("formatBlock", "h3")}>小标题</Button>
      <Button size="small" icon={<UnorderedListOutlined />} onClick={() => command("insertUnorderedList")}>项目符号</Button>
      <Button size="small" icon={<OrderedListOutlined />} onClick={() => command("insertOrderedList")}>编号列表</Button>
    </Space>
    <div
      ref={editorRef}
      contentEditable
      suppressContentEditableWarning
      onInput={() => onChange?.(editorRef.current?.innerHTML ?? "")}
      style={{ minHeight: 180, padding: 12, border: "1px solid #d9d9d9", borderRadius: 6, lineHeight: 1.7 }}
    />
  </div>;
}
