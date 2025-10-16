import React from 'react';
import {
  AppstoreOutlined,
  BarChartOutlined,
  CloudOutlined,
  ShopOutlined,
  TeamOutlined,
  UploadOutlined,
  UserOutlined,
  VideoCameraOutlined,
  /*按钮*/SearchOutlined,
  LeftOutlined,
} from '@ant-design/icons';
import { Layout, Menu, theme, /*文本域*/ Input, /*按钮*/ Button, Flex, Tooltip } from 'antd';
import './index.css';
import { useNavigate } from 'react-router-dom';

const { TextArea } = Input;

const { Header, Content, Sider } = Layout;
const siderStyle = {
  // overflow: 'auto',
  height: '100vh',
  position: 'sticky',
  insetInlineStart: 0,
  top: 0,
  bottom: 0,
  scrollbarWidth: 'thin',
  scrollbarGutter: 'stable',
};
const items = [
  UserOutlined,
  VideoCameraOutlined,
  UploadOutlined,
  BarChartOutlined,
  CloudOutlined,
  AppstoreOutlined,
  TeamOutlined,
  ShopOutlined,
].map((icon, index) => ({
  key: String(index + 1),
  icon: React.createElement(icon),
  label: `nav ${index + 1}`,
}));
const Answer = () => {
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();
  const navigate = useNavigate();
  return (
    <Layout hasSider>
      <Sider
        style={siderStyle}
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
        {/* 侧边栏历史记录区 */}
        <div className="history"><h2>历史记录</h2></div>
        <Menu theme="dark" mode="inline" defaultSelectedKeys={['1']} items={items} />
      </Sider>
      <Layout>
        <Header style={{ padding: 0, background: colorBgContainer }} >
          <h2 className='answer-index-header'>Algutor编程小助手</h2>
          {/* 头部代码区 */}
        </Header>
        <Content style={{ margin: '24px 16px 0', overflow: 'initial' }} className='content'>
          <div
            style={{
              padding: 24,
              textAlign: 'center',
              background: colorBgContainer,
              borderRadius: borderRadiusLG,
            }}
            className='content'
          >
            <div className="answer-input-box">
              <TextArea name="#" id="answer-input-box" placeholder="请输入您的问题..."></TextArea>
              <Flex gap="small" vertical>
                <Flex wrap gap="small">
                  <Tooltip title="search">
                    <Button type="primary" shape="round" icon={<SearchOutlined />} id='answer-submit-button' />
                  </Tooltip>
                </Flex>
              </Flex>
            </div>
            {/* 内容代码区 */}
            <p>long content</p>
            {
              // indicates very long content
              Array.from({ length: 100 }, (_, index) => (
                <React.Fragment key={index}>
                  {index % 20 === 0 && index ? 'more' : '...'}
                  <br />
                </React.Fragment>
              ))
            }
          </div>
        </Content>
      </Layout>
    </Layout>
  );
};
export default Answer;