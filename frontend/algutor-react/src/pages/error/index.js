import React from 'react';
import { Layout, theme, Tooltip, Button } from 'antd';
import { LeftOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import './index.css'

const { Header, Content, Footer } = Layout;

const ErrorPage = () => {
  const navigate = useNavigate();
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();
  return (
    <Layout style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header
        style={{
          position: 'sticky',
          top: 0,
          zIndex: 1,
          width: '100%',
          display: 'flex',
          alignItems: 'center',
        }}
      >
        <div className="demo-logo" />
        <div className="error-return" onClick={() => navigate('/')}>
          <Tooltip title="返回首页" placement="right">
            <LeftOutlined />返回首页
          </Tooltip>
        </div>
      </Header>
      <Content style={{ flex: 1, padding: '0 48px', display: 'flex', flexDirection: 'column' }}>
        <div className="error-h2"><h2>出现错误</h2></div>
        <div
          style={{
            padding: 24,
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
          }}
        >
          <div className="error-content">
            <ExclamationCircleOutlined className="error-icon" />
            <h3 className="error-title">出现错误</h3>
            <p className="error-desc">
              很抱歉，系统遇到了一些问题，未找到相关资源。请联系管理员或稍后重试。
            </p>
            <Button
              type="primary"
              shape="round"
              icon={<LeftOutlined />}
              onClick={() => navigate('/')}
              className="error-back-btn"
              size='large'
            >
              返回首页
            </Button>
          </div>
        </div>
      </Content>
      <Footer style={{ textAlign: 'center' }}>
        Ant Design ©{new Date().getFullYear()} Created by Ant UED
      </Footer>
    </Layout>
  );
};
export default ErrorPage;
