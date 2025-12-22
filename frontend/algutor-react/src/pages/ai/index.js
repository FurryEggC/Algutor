import React from 'react';
import { Layout, theme, Tooltip, Button, Menu } from 'antd';
import { LeftOutlined } from '@ant-design/icons';
import { useNavigate, Outlet, Link } from 'react-router-dom';
import './index.css'

const { Header, Content, Footer } = Layout;
const items = [
  {
    key: '1',
    label: <Link to="/ai/explain">代码解释</Link>,
  },
  {
    key: '2',
    label: <Link to="/ai/generate">代码生成</Link>,
  },
  {
    key: '3',
    label: <Link to="/ai/debug">代码调试</Link>,
  },
  {
    key: '4',
    label: <Link to="/ai/solve">算法求解</Link>,
  }
]
const AI = () => {
  const navigate = useNavigate();
  const [selectedKey, setSelectedKey] = React.useState('1');
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  // 监听路由变化，更新选中的菜单项
  React.useEffect(() => {
    const path = window.location.pathname;
    if (path.includes('/ai/explain')) setSelectedKey('1');
    else if (path.includes('/ai/generate')) setSelectedKey('2');
    else if (path.includes('/ai/debug')) setSelectedKey('3');
    else if (path.includes('/ai/solve')) setSelectedKey('4');
    else setSelectedKey('1');
  }, [window.location.pathname]);

  // 获取当前选中项的标题
  const getCurrentTitle = () => {
    const keyToTitle = {
      '1': '代码解释',
      '2': '代码生成',
      '3': '代码调试',
      '4': '算法求解'
    };
    return keyToTitle[selectedKey] || 'AI编程助手';
  };
  return (
    <Layout style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header
        style={{
          position: 'sticky',
          top: 0,
          zIndex: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          position: 'relative',
        }}
        className='ai-header'
      >
        <div className="demo-logo" />
        <div className="ai-return" onClick={() => navigate('/')}>
          <Tooltip title="返回首页" placement="right">
            <LeftOutlined /><span className="ai-hidden">返回首页</span>
          </Tooltip>
        </div>
        <Menu
          theme="dark"
          mode="horizontal"
          defaultSelectedKeys={['1']}
          selectedKeys={[selectedKey]}
          items={items}
          onClick={(e) => {
            setSelectedKey(e.key);
          }}
        />
      </Header>
      <Content style={{ flex: 1, padding: '0 48px', display: 'flex', flexDirection: 'column' }}>
        <div className="ai-h2"><h2>{getCurrentTitle()}</h2></div>
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
          <Outlet></Outlet>
        </div>
      </Content>
      <Footer style={{ textAlign: 'center' }}>
        Ant Design ©{new Date().getFullYear()} Created by Ant UED
      </Footer>
    </Layout>
  );
};
export default AI;