import { DeleteOutlined, EditOutlined, PlusOutlined } from "@ant-design/icons";
import { Button, Card, Popconfirm, Space, Table, Tag } from "antd";
import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { deleteActivity, listActivities, type Activity } from "../../api/activities";

export function ActivityListPage() {
  const [items, setItems] = useState<Activity[]>([]); const [loading, setLoading] = useState(true); const navigate = useNavigate();
  const load = useCallback(async () => { setLoading(true); try { setItems((await listActivities()).results); } finally { setLoading(false); } }, []);
  useEffect(() => { void load(); }, [load]);
  return <Card title="活动" extra={<Button type="primary" icon={<PlusOutlined />} onClick={() => navigate("/activities/new")}>新建活动</Button>}><Table rowKey="id" loading={loading} dataSource={items} pagination={false} columns={[{ title:"标题",dataIndex:"title" },{ title:"状态",dataIndex:"status",render:(value:string)=><Tag color={value==="published"?"green":"default"}>{value==="published"?"已发布":"草稿"}</Tag> },{ title:"操作",render:(_,item:Activity)=><Space><Button type="link" icon={<EditOutlined/>} onClick={()=>navigate(`/activities/${item.id}`)}>编辑</Button><Popconfirm title="确定删除这个活动？" onConfirm={()=>void deleteActivity(item.id).then(load)}><Button type="link" danger icon={<DeleteOutlined/>}>删除</Button></Popconfirm></Space> }]} /></Card>;
}
