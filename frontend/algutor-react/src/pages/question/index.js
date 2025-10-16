import React from 'react';
// 响应式布局
import { UploadOutlined, UserOutlined, VideoCameraOutlined, /*按钮*/SearchOutlined, LeftOutlined } from '@ant-design/icons';
import { Layout, Menu, theme, /*文本域*/ Input, /*按钮*/ Button, Flex, Tooltip } from 'antd';
import './index.css'
import { useNavigate } from 'react-router-dom';

const { Header, Content, Footer, Sider } = Layout;
// 文本域输入框
const { TextArea } = Input;
// 侧边栏内容
const items = [UserOutlined, VideoCameraOutlined, UploadOutlined, UserOutlined].map(
  (icon, index) => ({
    key: String(index + 1),
    icon: React.createElement(icon),
    label: `nav ${index + 1}`,
  }),
);
const Question = () => {
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();
  const navigate = useNavigate();
  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* 左侧边栏内容 */}
      <Sider
        breakpoint="lg"
        collapsedWidth="0"
        onBreakpoint={broken => {
          console.log(broken);
        }}
        onCollapse={(collapsed, type) => {
          console.log(collapsed, type);
        }}
      >
        <div className="demo-logo-vertical" />
        <div className="knowledge-return" onClick={() => navigate('/')}><span>{React.createElement(LeftOutlined)}</span><span>返回</span></div>
        <Menu theme="dark" mode="inline" defaultSelectedKeys={['4']} items={items} />
      </Sider>
      {/* 右侧主内容 */}
      <Layout>
        {/* 头部内容 */}
        <Header style={{ padding: 0, background: colorBgContainer }}><span className='question-index-header'>Algutor编程小助手</span></Header>
        {/* 主内容区 */}
        <Content style={{ margin: '24px 16px 0' }}>
          <div
            style={{
              padding: 24,
              minHeight: '100%',
              background: colorBgContainer,
              borderRadius: borderRadiusLG,
              display: 'flex',
              justifyContent: 'center',/* 横向居中 */
              alignItems: 'center',/* 纵向居中 */
              flexDirection: 'column'/* 纵向排列 */
            }}
          >
            {/* content */}
            <div className="question-input-title"><h1>Algutor</h1></div>
            <div className="question-input-box" style={{ position: 'relative', right: '0' }}>
              <TextArea name="#" id="question-input-box" placeholder="请输入您的问题..."></TextArea>
              <Flex gap="small" vertical>
                <Flex wrap gap="small">
                  <Tooltip title="search">
                    <Button type="primary" shape="round" icon={<SearchOutlined />} id='question-submit-button' />
                  </Tooltip>
                </Flex>
              </Flex>
            </div>
          </div>
        </Content>
        {/* 尾部内容 */}
        <Footer style={{ textAlign: 'center' }}>
          Ant Design ©{new Date().getFullYear()} Created by Ant UED
        </Footer>
      </Layout>
    </Layout >
  );
};
export default Question;