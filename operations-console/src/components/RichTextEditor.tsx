import { BoldOutlined, OrderedListOutlined, UnorderedListOutlined } from "@ant-design/icons";
import { Button, Space } from "antd";
import { useEffect, useRef } from "react";

interface RichTextEditorProps {
  value?: string;
  onChange?(value: string): void;
}

function escapeText(value: string) {
  return value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function normalizeMarkup(value: string) {
  const source = new DOMParser().parseFromString(value, "text/html");
  function render(node: Node): string {
    if (node.nodeType === Node.TEXT_NODE) return escapeText(node.textContent ?? "");
    if (node.nodeType !== Node.ELEMENT_NODE) return "";
    const element = node as HTMLElement;
    const children = Array.from(element.childNodes).map(render).join("");
    if (["STRONG", "B"].includes(element.tagName)) return `<strong>${children}</strong>`;
    if (["UL", "OL", "LI"].includes(element.tagName)) return `<${element.tagName.toLowerCase()}>${children}</${element.tagName.toLowerCase()}>`;
    if (element.tagName === "BR") return "<br>";
    if (["DIV", "P", "H1", "H2", "H3", "H4", "H5", "H6"].includes(element.tagName)) return `${children}<br>`;
    return children;
  }
  return Array.from(source.body.childNodes).map(render).join("").replace(/(<br>)+$/, "");
}

export function RichTextEditor({ value = "", onChange }: RichTextEditorProps) {
  const editorRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const normalized = normalizeMarkup(value);
    if (editorRef.current && editorRef.current.innerHTML !== normalized) editorRef.current.innerHTML = normalized;
    if (normalized !== value) onChange?.(normalized);
  }, [onChange, value]);

  function command(name: string, commandValue?: string) {
    editorRef.current?.focus();
    document.execCommand(name, false, commandValue);
    onChange?.(normalizeMarkup(editorRef.current?.innerHTML ?? ""));
  }

  function pastePlainText(event: React.ClipboardEvent<HTMLDivElement>) {
    event.preventDefault();
    document.execCommand("insertText", false, event.clipboardData.getData("text/plain"));
  }

  return <div>
    <Space size={4} style={{ marginBottom: 8 }}>
      <Button size="small" icon={<BoldOutlined />} onClick={() => command("bold")}>加粗</Button>
      <Button size="small" icon={<UnorderedListOutlined />} onClick={() => command("insertUnorderedList")}>项目符号</Button>
      <Button size="small" icon={<OrderedListOutlined />} onClick={() => command("insertOrderedList")}>编号列表</Button>
    </Space>
    <div
      ref={editorRef}
      contentEditable
      suppressContentEditableWarning
      onInput={() => onChange?.(normalizeMarkup(editorRef.current?.innerHTML ?? ""))}
      onPaste={pastePlainText}
      onBlur={() => onChange?.(normalizeMarkup(editorRef.current?.innerHTML ?? ""))}
      style={{ minHeight: 180, padding: 12, border: "1px solid #d9d9d9", borderRadius: 6, lineHeight: 1.7 }}
    />
  </div>;
}
