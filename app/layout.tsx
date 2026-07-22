import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "精品旅行 H5 原型",
  description: "用于模拟精品旅行与搭子小程序页面跳转的本地手机原型。",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
