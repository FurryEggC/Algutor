import React from 'react';
import {
  LeftOutlined,
  BarsOutlined,
  BookOutlined,
  PlusOutlined,
  FieldTimeOutlined,
  HistoryOutlined,
  EditOutlined,
  DeleteOutlined,
  InboxOutlined
} from '@ant-design/icons';
import { Layout, Menu, theme, Button, Form, Modal, Input, Tooltip, Select } from 'antd';
import { useSearchParams, useNavigate } from 'react-router-dom';
import './index.css';
import { useState, useEffect } from 'react';
import axios from 'axios';
import Editor from '@monaco-editor/react';

const { Header, Content, Footer, Sider } = Layout;

/* ② 两个子页面 ************************************************************/
function AllPage({ setNav }) {
  // 添加知识点功能变量和函数
  const [addForm] = Form.useForm();
  const [addOpen, setAddOpen] = useState(false);
  const [contentItem, setContentItem] = useState([]);
  async function getKnowledge() {
    try {
      const res = await axios({
        url: 'https://algutor.xyz/api/knowledge',
        method: 'GET'
      })
      setContentItem(res.data.data);
      const items = res.data.data.map(item => ({
        key: String(item.id),
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
      navigate('/error');
    }
  }
  async function addKnowledge(values) {
    try {
      await axios({
        url: 'https://algutor.xyz/api/knowledge',
        method: 'POST',
        data: {
          topic: values.topic,
          explanation: values.explanation
        }
      })
      getKnowledge();
    } catch (error) {
      console.log(error);
      navigate('/error');;
    }
  }
  const setAddCreate = values => {
    console.log('Received values of form: ', values);
    addKnowledge(values);
    setAddOpen(false);
  };
  // 页面初次渲染获取所有知识点
  useEffect(() => {
    getKnowledge();
  }, []);
  // 修改知识点功能变量和函数
  const [editForm] = Form.useForm();
  const [editOpen, setEditOpen] = useState(false);
  async function editKnowledge(values) {
    try {
      await axios({
        url: `https://algutor.xyz/api/knowledge?topic=${values.topic}`,
        method: 'PUT',
        data: {
          explanation: values.explanation
        }
      })
      getKnowledge();
    } catch (error) {
      navigate('/error');;
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
        url: `https://algutor.xyz/api/knowledge?topic=${item.topic}`,
        method: 'DELETE'
      })
      getKnowledge();
    } catch (error) {
      navigate('/error');;
    }
  }
  const [deleteItem, setDeleteItem] = useState([]);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const showModal = (item) => {
    setDeleteItem(item);
    setDeleteOpen(true);
  };
  const handleDeleteOk = () => {
    deleteKnowledge(deleteItem);
    setDeleteOpen(false);
  };
  const handleDeleteCancel = () => {
    setDeleteOpen(false);
  };
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
              <BarsOutlined /> <span className="allpage-knowledge-minner-hidden">知识点</span>
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
        </div>
      </div>
      {/* 内容 */}
      {contentItem.length > 0 ? contentItem.map(item => (
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
            <div className="allpage-content-right-item" onClick={() => showModal(item)}>
              <Tooltip title="删除" placement="top">
                <DeleteOutlined /> <span className="allpage-minner-hidden">删除</span>
              </Tooltip>
            </div>
          </div>
        </div>
      )) : (
        <div className="allpage-no-knowledge">
          <InboxOutlined />
          <p className="empty-title">暂无知识点</p>
          <p className="empty-desc">点击右上角「添加知识点」创建第一条记录</p>
        </div>
      )}
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
          <Input
            autoComplete="off"        // 1. 关闭自动填充
            spellCheck="false"        // 2. 关闭拼写检查 
          />
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
          <Input
            autoComplete="off"        // 1. 关闭自动填充
            spellCheck="false"        // 2. 关闭拼写检查
            readOnly
          />
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
      {/* 弹窗：删除知识点 */}
      <Modal
        title="再次确认"
        open={deleteOpen}
        onOk={handleDeleteOk}
        onCancel={handleDeleteCancel}
        okText="确认"
        cancelText="取消"
      >
        <p>确认删除该知识点吗？</p>
      </Modal>
    </>
  );
}

function TopicPage({ topic: propTopic, setNav }) {
  const navigate = useNavigate();
  const saveTopic = (t) => localStorage.setItem('lastTopic', t);
  const loadTopic = () => localStorage.getItem('lastTopic') || '全部';
  // 若 propTopic 为空，就读本地缓存
  const [topic, setTopic] = useState(() => propTopic || loadTopic());
  const [explanation, setExplanation] = useState('');
  async function getExplanationAndCode() {
    try {
      const res = await axios({
        url: `https://algutor.xyz/api/knowledge?topic=${topic}`,
        method: 'GET'
      })
      setExplanation(res.data.data.explanation);
      setExample(res.data.data.example);
    } catch (error) {
      navigate('/error');
    }
  }
  async function getNav() {
    try {
      const res = await axios({
        url: 'https://algutor.xyz/api/knowledge',
        method: 'GET'
      })
      const items = res.data.data.map(item => ({
        key: String(item.id),
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
      navigate('/error');
    }
  }
  useEffect(() => {
    getExplanationAndCode();
    getNav();
  }, [topic])
  // 只要 topic 变化，就写回 localStorage
  useEffect(() => {
    saveTopic(topic);
  }, [topic]);
  // 代码编辑器
  const [language, setLanguage] = useState('python');
  const [example, setExample] = useState([]);
  // 添加代码
  const [addForm] = Form.useForm();
  const [addOpen, setAddOpen] = useState(false);
  async function addCode(values) {
    if (example.find(item => item.language === values.language)) {
      return alert('该语言的示例代码已存在，请不要重复添加');
    }
    try {
      const newExample = [...example, {
        language: values.language,
        code: values.code,
      }]
      await axios({
        url: `https://algutor.xyz/api/knowledge?topic=${topic}`,
        method: 'PUT',
        data: {
          example: newExample,
        }
      })
      getExplanationAndCode();
    } catch (error) {
      console.log(error);
      navigate('/error');;
    }
  }
  const setAddCreate = values => {
    console.log('Received values of form: ', values);
    addCode(values);
    getExplanationAndCode();
    setAddOpen(false);
  };
  const LINE_HEIGHT = 19;   // Monaco 默认 19px（14px 字号）
  const HEADER_HEIGHT = 22; // 行号栏高度（可选）
  const MIN_LINES = 3;      // 最少保留 3 行
  const MAX_LINES = 25;     // 最多 25 行（防止过长）
  // 修改代码功能变量和函数
  const [code, setCode] = useState('');
  const [editForm] = Form.useForm();
  const [editOpen, setEditOpen] = useState(false);
  async function editCode(values) {
    try {
      const newExample = example.map(item => item.language === values.language ? {
        language: values.language,
        code: values.code,
      } : item);
      await axios({
        url: `https://algutor.xyz/api/knowledge?topic=${topic}`,
        method: 'PUT',
        data: {
          example: newExample,
        }
      })
      getExplanationAndCode();
    } catch (error) {
      console.log(error);
      navigate('/error');;
    }
  }
  const setEditCreate = values => {
    console.log('Received values of form: ', values);
    editCode(values);
    setEditOpen(false);
  };
  // 表单中显示默认值
  const handleEdit = (item) => {
    setEditOpen(true);
    setCode(item.code);
    editForm.setFieldsValue({
      language: item.language,
      code: item.code,
    });
  }
  // 删除代码
  const [deleteItem, setDeleteItem] = useState([]);
  const [deleteOpen, setDeleteOpen] = useState(false);
  async function deleteCode(item) {
    try {
      const newExample = example.filter(i => i.language !== item.language);
      await axios({
        url: `https://algutor.xyz/api/knowledge?topic=${topic}`,
        method: 'PUT',
        data: {
          example: newExample,
        }
      })
      getExplanationAndCode();
    } catch (error) {
      console.log(error);
      navigate('/error');;
    }
  }
  const showModal = (item) => {
    setDeleteItem(item);
    setDeleteOpen(true);
  };
  const handleDeleteOk = () => {
    deleteCode(deleteItem);
    setDeleteOpen(false);
  };
  const handleDeleteCancel = () => {
    setDeleteOpen(false);
  };
  return (
    <>
      {/* 内容代码区 */}
      <h3 className="knowledge-title">简介</h3>
      <div className="topicpage-explanation">{explanation}</div>
      <div className="topicpage-code-header">
        <div className="topicpage-code-header-left"><h3 className="knowledge-title">示例代码</h3></div>
        <div className="topicpage-code-header-right">
          <Tooltip title="添加代码" placement="top">
            <Button
              type="primary"
              shape="round"
              icon={<PlusOutlined />}
              size="default"
              onClick={() => setAddOpen(true)}
            >
              {/* 在 ≥992 时显示文字，<992 时自动隐藏 */}
              <span className="allpage-minner-hidden">添加代码</span>
            </Button>
          </Tooltip>
        </div>
      </div>
      <div className="topicpage-code">
        {example.length > 0 ? example.map((item, index) => (
          <div className="topicpage-code-item" key={index}>
            <div className="topcipage-code-language">
              <div className="topicpage-code-language-left">{item.language}</div>
              <div className="topicpage-code-language-right">
                <div className="topicpage-code-language-right-item" onClick={() => handleEdit(item)}>
                  <Tooltip title="编辑" placement="top">
                    <EditOutlined /> <span className="allpage-minner-hidden">编辑</span>
                  </Tooltip>
                </div>
                <div className="topicpage-code-language-right-item" onClick={() => showModal(item)}>
                  <Tooltip title="删除" placement="top">
                    <DeleteOutlined /> <span className="allpage-minner-hidden">删除</span>
                  </Tooltip>
                </div>
              </div>
            </div>
            <div className="topicpage-code-content">
              <Editor
                height={Math.min(
                  Math.max(item.code.split('\n').length, MIN_LINES),
                  MAX_LINES
                ) * LINE_HEIGHT + HEADER_HEIGHT}
                language={item.language}
                theme="vs"
                value={item.code}
                options={{
                  tabSize: 2,
                  insertSpaces: true,
                  wordWrap: 'on',
                  minimap: { enabled: false },
                  fontSize: 14,
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                  readOnly: true,
                }}
              />
            </div>
          </div>
        )) : (
          <div className="topicpage-no-code">
            <InboxOutlined />
            <p className="empty-title">暂无示例代码</p>
            <p className="empty-desc">点击右上角「添加代码」创建第一条记录</p>
          </div>
        )}
      </div>
      {/* 弹窗：添加代码 */}
      <Modal
        open={addOpen}
        title="添加代码"
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
        <div className='allpage-addKnowledge-code'>
          <Form.Item name="language" label="编程语言" initialValue="python">
            <Select
              style={{ width: 120 }}
              onChange={(value) => {
                setLanguage(value);
              }}
              options={[
                { value: 'python', label: 'Python' },
                { value: 'c', label: 'C' },
                { value: 'cpp', label: 'C++' },
                { value: 'javascript', label: 'JavaScript' },
                { value: 'java', label: 'Java' },
              ]}
            />
          </Form.Item>
          <Form.Item
            name="code"
            label="代码"
            rules={[{ required: true, message: '请输入代码！' }]}
          >
            <div style={{
              padding: '16px',
              border: '1px solid #e5e5e5',
              borderRadius: '8px',
            }}>
              <Editor
                height="200px"
                language={language}
                theme="vs"
                onChange={(value) => {
                  setCode(value);
                  addForm.setFieldValue('code', value);
                }}
                options={{
                  tabSize: 2,
                  insertSpaces: true,
                  wordWrap: 'on',
                  minimap: { enabled: false },
                  fontSize: 14,
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                }}
              />
            </div>
          </Form.Item>
        </div>
      </Modal>
      {/* 弹窗：修改代码 */}
      <Modal
        open={editOpen}
        title="编辑代码"
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
        <div className='allpage-addKnowledge-code'>
          <Form.Item name="language" label="编程语言" initialValue="python">
            <Select
              style={{ width: 120 }}
              options={[
                { value: 'python', label: 'Python', disabled: true },
                { value: 'c', label: 'C', disabled: true },
                { value: 'cpp', label: 'C++', disabled: true },
                { value: 'javascript', label: 'JavaScript', disabled: true },
                { value: 'java', label: 'Java', disabled: true },
              ]}
            />
          </Form.Item>
          <Form.Item
            name="code"
            label="代码"
            rules={[{ required: true, message: '请输入代码！' }]}
          >
            <div style={{
              padding: '16px',
              border: '1px solid #e5e5e5',
              borderRadius: '8px',
            }}>
              <Editor
                height="200px"
                language={language}
                theme="vs"
                value={code}
                onChange={(value) => {
                  setCode(value);
                  editForm.setFieldValue('code', value);
                }}
                options={{
                  tabSize: 2,
                  insertSpaces: true,
                  wordWrap: 'on',
                  minimap: { enabled: false },
                  fontSize: 14,
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                }}
              />
            </div>
          </Form.Item>
        </div>
      </Modal>
      {/* 弹窗：删除代码 */}
      <Modal
        title="再次确认"
        open={deleteOpen}
        onOk={handleDeleteOk}
        onCancel={handleDeleteCancel}
        okText="确认"
        cancelText="取消"
      >
        <p>确认删除该示例代码吗？</p>
      </Modal>
    </>
  );
}

/* ③ 主组件 ***************************************************************/
function Knowledge() {
  const [search, setSearch] = useSearchParams();
  const navigate = useNavigate();
  const selectedKey = search.get('key') ?? '0';   // 默认全部

  const { token } = theme.useToken();

  const [nav, setNav] = useState([{                     // key = 0  →  “全部”
    key: '0',
    icon: <BarsOutlined />,
    label: '全部',
    topic: '全部',
  }]);
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
      <AllPage setNav={setNav} />
    ) : (
      <TopicPage topic={nav.find((i) => i.key === selectedKey)?.label} setNav={setNav} key={selectedKey} />
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