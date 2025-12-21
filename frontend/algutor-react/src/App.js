import React from 'react';
import { Layout, theme } from 'antd';
import './App.css'
import { useNavigate } from 'react-router-dom'
const { Header, Content, Footer } = Layout;
const App = () => {
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();
  const navigate = useNavigate();
  return (
    <Layout>
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
        <div className="app-nav">
          <span><a href="#introduce">平台简介</a></span>
          <span><a href="#function">相关功能</a></span>
          <span><a href="#about">关于我们</a></span>
        </div>
      </Header>
      <Content style={{ padding: '0 48px' }}>
        {/* 平台简介 */}
        <div className="app-h2" id="introduce"><h2>平台简介</h2></div>
        <div
          style={{
            padding: 24,
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
          }}
          className="app-introduce"
        >
          <div className="app-banner" style={{ marginBottom: 32 }}>
            <h1 style={{ fontSize: 32, marginBottom: 8 }}>Algutor智能编程学习平台</h1>
            <p style={{ fontSize: 16, color: '#555' }}>
              本平台面向编程初学者与进阶者，融合大模型语义理解、知识图谱构建与代码静态分析技术，
              打造“学-测-评”一体化智能学习环境。你可以上传代码获取结构化解析与改进建议，
              也可以通过自然语言提问获取即时代码示例与知识点讲解。系统支持多语言（Python/Java/CSS/HTML等），
              并基于你的学习记录动态推荐个性化训练路径，帮助你高效构建编程思维与实战能力。
            </p>
          </div>
        </div>
        {/* 相关功能 */}
        <div className="app-h2" id="function"><h2>相关功能</h2></div>
        <div
          style={{
            padding: 24,
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
          }}
          className="app-function-container"
        >
          <div className="app-function" onClick={() => navigate('/execute')}>代码运行</div>
          <div className="app-function" onClick={() => navigate('/knowledge')}>知识点管理</div>
          <div className="app-function" onClick={() => navigate('/ai/explain')}>AI编程助手</div>
        </div>
        {/* 相关功能 */}
        <div className="app-h2" id="about"><h2>关于我们</h2></div>
        <div
          style={{
            padding: 24,
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
          }}
          className="app-about"
        >
          <h4>团队简介</h4>
          <p>我们是一群热爱编程的大学生开发者，致力于通过人工智能技术革新传统编程学习方式。</p>
          <h4>团队组成</h4>
          <p>由6名计算机科学与技术专业领域在校大学生组成。团队成员分工明确，包括前端开发、后端开发、AI模型集成等多个方向，共同协作完成项目开发。</p>
          <h4>学习渠道</h4>
          <p>通过bilibili相关视频进行自主学习，获取前端开发、后端架构和AI技术等领域的专业知识，为项目开发提供了坚实的技术基础。团队成员定期分享学习心得，共同进步。</p>
          <h4>联系我们</h4>
          <p>邮箱：contact@algutor.com</p>
        </div>
      </Content>
      <Footer style={{ textAlign: 'center' }}>
        Ant Design ©{new Date().getFullYear()} Created by Ant UED
      </Footer>
    </Layout>
  );
};
export default App;