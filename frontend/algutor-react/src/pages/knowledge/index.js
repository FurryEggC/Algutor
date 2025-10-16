import React from 'react';
import {
  LeftOutlined,
  BarsOutlined,
  BookOutlined,
  PlusOutlined,
  FieldTimeOutlined,
  HistoryOutlined,
  EditOutlined,
  DeleteOutlined
} from '@ant-design/icons';
import { Layout, Menu, theme, Button, Form, Modal, Input, Tooltip } from 'antd';
import { useSearchParams, useNavigate } from 'react-router-dom';
import './index.css';
import { useState, useEffect } from 'react';
import axios from 'axios';

const { Header, Content, Footer, Sider } = Layout;
// 异步请求



/* ② 两个子页面 ************************************************************/
function AllPage() {
  // 添加知识点功能变量和函数
  const [addForm] = Form.useForm();
  const [addOpen, setAddOpen] = useState(false);
  const [contentItem, setContentItem] = useState([]);
  async function addKnowledge(values) {
    try {
      await axios({
        url: 'https://30841f5ebb16.ngrok-free.app/api/knowledge',
        method: 'POST',
        data: {
          topic: values.topic,
          explanation: values.explanation
        },
        headers: {
          'ngrok-skip-browser-warning': 'true'
        }
      })
      const res = await axios({
        url: 'https://30841f5ebb16.ngrok-free.app/api/knowledge',
        method: 'GET',
        headers: {
          'ngrok-skip-browser-warning': 'true'
        }
      })
      setContentItem(res.data.data);
    } catch (error) {
      console.log(error);
    }
  }
  const setAddCreate = values => {
    console.log('Received values of form: ', values);
    addKnowledge(values);
    setAddOpen(false);
  };
  // 页面初次渲染获取所有知识点
  useEffect(() => {
    async function getKnowledge() {
      try {
        const res = await axios({
          url: 'https://30841f5ebb16.ngrok-free.app/api/knowledge',
          method: 'GET',
          headers: {
            'ngrok-skip-browser-warning': 'true'
          }
        })
        // console.log(res)
        setContentItem(res.data.data);
      } catch (error) {
        console.log(error)
      }
    }
    getKnowledge();
  }, []);
  // 修改知识点功能变量和函数
  const [editForm] = Form.useForm();
  const [editOpen, setEditOpen] = useState(false);
  async function editKnowledge(values) {
    try {
      await axios({
        url: `https://30841f5ebb16.ngrok-free.app/api/knowledge?topic=${values.topic}`,
        method: 'PUT',
        data: {
          explanation: values.explanation
        },
        headers: {
          'ngrok-skip-browser-warning': 'true'
        }
      })
      const res = await axios({
        url: 'https://30841f5ebb16.ngrok-free.app/api/knowledge',
        method: 'GET',
        headers: {
          'ngrok-skip-browser-warning': 'true'
        }
      })
      setContentItem(res.data.data);
    } catch (error) {
      console.log(error);
    }
  }
  const setEditCreate = values => {
    console.log('Received values of form: ', values);
    editKnowledge(values);
    setEditOpen(false);
  };
  // 表单中显示原默认值
  const handleEdit = (item) => {
    setEditOpen(true);
    editForm.setFieldsValue({
      topic: item.topic,
      explanation: item.explanation,
    });
  }
  // 删除知识点
  async function deleteKnowledge(item) {
    try {
      await axios({
        url: `https://30841f5ebb16.ngrok-free.app/api/knowledge?topic=${item.topic}`,
        method: 'DELETE',
        headers: {
          'ngrok-skip-browser-warning': 'true'
        }
      })
      const res2 = await axios({
        url: 'https://30841f5ebb16.ngrok-free.app/api/knowledge',
        method: 'GET',
        headers: {
          'ngrok-skip-browser-warning': 'true'
        }
      })
      setContentItem(res2.data.data);
    } catch (error) {
      console.log(error);
    }
  }
  // 路由跳转
  const navigate = useNavigate();
  return (
    <>
      {/* 表头 */}
      <div className="allpage-header">
        {/* 左侧内容布局 */}
        <div className="allpage-header-left">
          <div className="allpage-header-left-item">
            <Tooltip title="知识点" placement="top">
              <BarsOutlined /> 知识点
            </Tooltip>
          </div>
          <div className="allpage-header-left-item allpage-minner-hidden">
            <Tooltip title="创建时间" placement="top">
              <FieldTimeOutlined /> 创建时间
            </Tooltip>
          </div>
          <div className="allpage-header-left-item allpage-minner-hidden">
            <Tooltip title="最后一次更新时间" placement="top">
              <HistoryOutlined /> 最后一次更新时间
            </Tooltip>
          </div>
        </div>
        {/* 右侧内容布局 */}
        <div className="allpage-header-right">
          <Tooltip title="添加知识点" placement="top">
            <Button
              type="primary"
              shape="round"
              icon={<PlusOutlined />}
              size="default"
              onClick={() => setAddOpen(true)}
            >
              {/* 在 ≥992 时显示文字，<992 时自动隐藏 */}
              <span className="allpage-minner-hidden">添加知识点</span>
            </Button>
          </Tooltip>
          {/* 弹窗：添加知识点 */}
          <Modal
            open={addOpen}
            title="添加知识点"
            okText="确认"
            cancelText="取消"
            okButtonProps={{ autoFocus: true, htmlType: 'submit' }}
            onCancel={() => setAddOpen(false)}
            destroyOnHidden
            modalRender={dom => (
              <Form
                layout="vertical"
                form={addForm}
                name="form_in_modal"
                initialValues={{ modifier: 'public' }}
                clearOnDestroy
                onFinish={values => setAddCreate(values)}
              >
                {dom}
              </Form>
            )}
          >
            <Form.Item
              name="topic"
              label="知识点"
              rules={[{ required: true, message: '请输入知识点！' }]}
            >
              <Input />
            </Form.Item>
            <Form.Item name="explanation" label="内容" rules={[{ required: true, message: '请输入内容！' }]}>
              <Input.TextArea style={
                {
                  outline: 'none',
                  resize: 'none',
                  height: '100px',
                }
              } />
            </Form.Item>
          </Modal>
        </div>
      </div>
      {/* 内容 */}
      {contentItem.map(item => (
        <div className="allpage-content" key={item.id}>
          {/* 左侧内容布局 */}
          <div className="allpage-content-left">
            <div className="allpage-content-left-item" onClick={() => navigate(`/knowledge?key=${item.id}&topic=${item.topic}`)} style={{ cursor: 'pointer' }}>
              <Tooltip title={item.topic} placement="top">
                <BookOutlined /> {item.topic}
              </Tooltip>
            </div>
            <div className="allpage-content-left-item allpage-minner-hidden">
              {item.created_at}
            </div>
            <div className="allpage-content-left-item allpage-minner-hidden">
              {item.updated_at}
            </div>
          </div>
          {/* 右侧内容布局 */}
          <div className="allpage-content-right">
            <div className="allpage-content-right-item" onClick={() => { handleEdit(item) }}>
              <Tooltip title="编辑" placement="top">
                <EditOutlined /> <span className="allpage-minner-hidden">编辑</span>
              </Tooltip>
            </div>
            <div className="allpage-content-right-item" onClick={() => deleteKnowledge(item)}>
              <Tooltip title="删除" placement="top">
                <DeleteOutlined /> <span className="allpage-minner-hidden">删除</span>
              </Tooltip>
            </div>
          </div>
        </div>
      ))}
      {/* 弹窗：编辑知识点 */}
      <Modal
        open={editOpen}
        title="编辑知识点"
        okText="确认"
        cancelText="取消"
        okButtonProps={{ autoFocus: true, htmlType: 'submit' }}
        onCancel={() => setEditOpen(false)}
        destroyOnHidden
        modalRender={dom => (
          <Form
            layout="vertical"
            form={editForm}
            name="form_in_modal"
            initialValues={{ topic: '1111', explanation: '111' }}
            clearOnDestroy
            onFinish={values => setEditCreate(values)}
          >
            {dom}
          </Form>
        )}
      >
        <Form.Item
          name="topic"
          label="知识点"
          rules={[{ required: true, message: '请输入知识点！' }]}
        >
          <Input />
        </Form.Item>
        <Form.Item name="explanation" label="内容" rules={[{ required: true, message: '请输入内容！' }]}>
          <Input.TextArea style={
            {
              outline: 'none',
              resize: 'none',
              height: '100px',
            }
          }
          />
        </Form.Item>
      </Modal>
    </>
  );
}

function TopicPage({ topic }) {
  return <div> {/* 内容代码区 */}
    <p>long content</p>
    {
      // indicates very long content
      Array.from({ length: 100 }, (_, index) => (
        <React.Fragment key={index}>
          {index % 20 === 0 && index ? 'more' : '...'}
          <br />
        </React.Fragment>
      ))
    }</div>;
}

/* ③ 主组件 ***************************************************************/
function Knowledge() {
  const [search, setSearch] = useSearchParams();
  const navigate = useNavigate();
  const selectedKey = search.get('key') ?? '0';   // 默认全部

  const { token } = theme.useToken();

  const [nav, setNav] = useState([]);
  useEffect(() => {
    async function getKnowledge() {
      try {
        const res = await axios({
          url: 'https://30841f5ebb16.ngrok-free.app/api/knowledge',
          method: 'GET',
          headers: {
            'ngrok-skip-browser-warning': 'true'
          }
        })
        // console.log(res)
        const items = res.data.data.map(item => ({
          key: item.id,
          icon: <BookOutlined />,
          label: item.topic,
          topic: item.topic,
        }))
        items.unshift({                     // key = 0  →  “全部”
          key: '0',
          icon: <BarsOutlined />,
          label: '全部',
          topic: '全部',
        });
        setNav(items);
      } catch (error) {
        console.log(error)
      }
    }
    getKnowledge();
  }, []);

  /* 点击菜单：只改查询参数 → 不刷新页面 */
  const onMenuClick = (e) => {
    const key = e.key;
    const topic = e.item.props.topic;
    if (key === '0') {
      setSearch({});              // 地址栏 /knowledge
    } else {
      setSearch({ key, topic });
    }
  };

  /* 根据 key 决定渲染哪块“子页面” */
  const renderContent = () =>
    selectedKey === '0' ? (
      <AllPage />
    ) : (
      <TopicPage topic={nav.find((i) => i.key === selectedKey)?.label} />
    );

  return (
    <Layout hasSider>
      <Sider
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'sticky',
          left: 0,
          top: 0,
          bottom: 0,
        }}
        breakpoint="lg"
      >
        <div className="demo-logo-vertical" />
        <div className="knowledge-return" onClick={() => navigate('/')}>
          <Tooltip title="返回首页" placement="right">
            <LeftOutlined /><span className="allpage-minner-hidden">返回首页</span>
          </Tooltip>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selectedKey]}
          items={nav}
          onClick={onMenuClick}
        />
      </Sider>

      <Layout style={{ display: 'flex', flexDirection: 'column' }}>
        <Header style={{ padding: 0, background: token.colorBgContainer }} >
          <h2 className="knowledge-title">{nav.find((i) => i.key === selectedKey)?.label}</h2>
        </Header>
        <Content style={{ flex: 1, margin: '24px 16px 0' }}>
          <div
            style={{
              padding: 24,
              background: token.colorBgContainer,
              borderRadius: token.borderRadiusLG,
              height: '100%',
            }}
          >
            {renderContent()}
          </div>
        </Content>
        <Footer style={{ textAlign: 'center' }}>
          Ant Design ©{new Date().getFullYear()} Created by Ant UED
        </Footer>
      </Layout>
    </Layout>
  );
}

export default Knowledge;
