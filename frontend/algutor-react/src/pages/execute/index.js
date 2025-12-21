import React, { useState, useEffect } from 'react';
import { Layout, theme, Tooltip, Button, Menu, Form, Select, InputNumber, Input, Spin } from 'antd';
import { LeftOutlined, LoadingOutlined } from '@ant-design/icons';
import { useNavigate, Outlet, Link } from 'react-router-dom';
import { Editor } from '@monaco-editor/react';
import axios from 'axios';
import './index.css'

const { Header, Content, Footer } = Layout;

const Execute = () => {
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  const navigate = useNavigate();
  const [executeForm] = Form.useForm();
  const [canSubmit, setCanSubmit] = useState(true);
  const [buttonText, setButtonText] = useState('运行代码');
  const [language, setLanguage] = useState(() => {
    return sessionStorage.getItem('executeLanguage') || 'python';
  });
  const [code, setCode] = useState(() => {
    return sessionStorage.getItem('executeCode') || '';
  });
  const [executeCompileInformation, setExecuteCompileInformation] = useState('暂无编译信息，运行后查看');
  const [executeoutput, setExecuteOutput] = useState('暂无输出结果');
  async function executeCode(values) {
    try {
      const res = await axios({
        url: 'https://algutor.xyz/api/execute',
        method: 'POST',
        data: {
          "language": values.language,  // 可选，默认为python
          "code": values.code,
          "input": values.input,
          "timeout": values.timeout,
        }
      })
      console.log(res)
      if (res.data.error === '') {
        if (res.data.output === '') { setExecuteOutput('无输出结果，请检查:\n1.是否已输入测试数据\n2.测试数据输入格式是否正确\n3.代码是否可以输出') }
        else { setExecuteOutput(res.data.output) }
        setExecuteCompileInformation(res.data.status)
      } else if (res.data.message === '代码执行超时') {
        setExecuteCompileInformation('success')
        setExecuteOutput(res.data.error)
      } else {
        setExecuteOutput(res.data.message)
        setExecuteCompileInformation(res.data.error)
      }
      setCanSubmit(true);
      setButtonText('运行代码');
      sessionStorage.setItem('generated_code', res.data.generated_code);
    } catch (error) {
      navigate('/error');
    }
  }
  const onFinish = values => {
    setCanSubmit(false);
    setButtonText('运行中...');
    executeCode(values);
    sessionStorage.setItem('executeLanguage', values.language);
    sessionStorage.setItem('executeCode', values.code);
    console.log('Success:', values);
  };
  const onFinishFailed = errorInfo => {
    console.log('Failed:', errorInfo);
  };
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
        <div className="execute-return" onClick={() => navigate('/')}>
          <Tooltip title="返回首页" placement="right">
            <LeftOutlined /><span className="execute-hidden">返回首页</span>
          </Tooltip>
        </div>
        <div className="execute-nav">
          <span><a href="#code">代码</a></span>
          <span><a href="#compileInformation">编译信息</a></span>
          <span><a href="#input">输入</a></span>
          <span><a href="#output">输出</a></span>
        </div>
      </Header>
      <Content style={{ flex: 1, padding: '0 48px', display: 'flex', flexDirection: 'column' }}>
        <div className="execute-h2" id='code'><h2>代码运行</h2></div>
        <div
          style={{
            padding: 24,
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
            flex: 1,
          }}
          className="execute-content-container"
        >
          <div className="execute-code-container">
            <Form
              name="execute-code"
              form={executeForm}
              labelCol={{ flex: 'auto' }}
              wrapperCol={{ flex: 1 }}
              labelWrap={false}
              initialValues={{ remember: true }}
              onFinish={onFinish}
              onFinishFailed={onFinishFailed}
              autoComplete="off"
            >
              <div className="execute-code">
                <Form.Item
                  name="code"
                  label="代码"
                  labelAlign="left"
                  rules={[{ required: true, message: '请输入代码！' }]}
                >
                  <div className='execute-code-editor'>
                    <Editor
                      height="100%"
                      language={language}
                      theme="vs"
                      onChange={(value) => {
                        setCode(value);
                        executeForm.setFieldValue('code', value);
                      }}
                      options={{
                        wordWrap: 'off',          // ← 关键：关闭自动换行
                        tabSize: 2,
                        insertSpaces: true,
                        minimap: { enabled: false },
                        fontSize: 14,
                        scrollBeyondLastLine: false,
                        automaticLayout: true,
                      }}
                      value={code}
                    />
                  </div>
                </Form.Item>
              </div>
              <div className="execute-run-container">
                <div className="execute-run-container-left">
                  <div className="execute-run-container-left-language">
                    <Form.Item name="language" label="编程语言" initialValue={language}>
                      <Select
                        style={{ width: 120 }}
                        onChange={(value) => {
                          setLanguage(value);
                        }}
                        options={[
                          { value: 'python', label: 'Python' },
                          { value: 'c', label: 'C' },
                          { value: 'cpp', label: 'C++' },
                          { value: 'java', label: 'Java' },
                        ]}
                      />
                    </Form.Item>
                  </div>
                  <div className="execute-run-container-left-limit">
                    <Form.Item name="timeout" label="限制时间">
                      <InputNumber defaultValue='3' placeholder='1~6秒(默认3秒)' min='1' max='6' />
                    </Form.Item>
                  </div>
                </div>
                <div className="execute-run-container-right">
                  <Form.Item label={null}>
                    <Button type="primary" htmlType="submit" disabled={!canSubmit}>
                      {buttonText}
                    </Button>
                  </Form.Item>
                </div>
              </div>
            </Form>
          </div>
          <div className="execute-result-container">
            <div className="execute-result-container-compile-information">
              <div className="execute-result-container-compile-information-title">
                <h3 id='compileInformation'>编译信息</h3>
              </div>
              <div className="execute-result-container-compile-information-content">
                {buttonText === '运行代码' ? <pre>{executeCompileInformation}</pre> :
                  <div className="execute-compile-information">
                    <Spin indicator={<LoadingOutlined style={{ fontSize: 24 }} spin />} />
                    <p className="empty-title">编译中...</p>
                    <p className="empty-desc">请稍后，不要离开当前页面</p>
                  </div>
                }
              </div>
            </div>
            <div className="execute-result-container-result">
              <div className="execute-result-container-result-input">
                <div className="execute-result-container-result-input-title">
                  <h3 id='input'>输入</h3>
                </div>
                <div className="execute-result-container-result-input-content">
                  <Form
                    name="execute-input"
                    form={executeForm}
                    labelCol={{ flex: 'auto' }}
                    wrapperCol={{ flex: 1 }}
                    labelWrap={false}
                    initialValues={{ remember: true }}
                    onFinish={onFinish}
                    onFinishFailed={onFinishFailed}
                    autoComplete="off"
                  >
                    <Form.Item name="input">
                      <Input.TextArea
                        style={{
                          outline: 'none',
                          resize: 'none',
                          width: '100%',
                          height: '100%',
                        }}
                      // defaultValue={requirement}
                      />
                    </Form.Item>
                  </Form>
                </div>
              </div>
              <div className="execute-result-container-result-output">
                <div className="execute-result-container-result-output-title">
                  <h3 id='output'>输出</h3>
                </div>
                <div className="execute-result-container-result-output-content">
                  {buttonText === '运行代码' ? <pre>{executeoutput}</pre> :
                    <div className="execute-compile-information">
                      <Spin indicator={<LoadingOutlined style={{ fontSize: 24 }} spin />} />
                      <p className="empty-title">输出中...</p>
                      <p className="empty-desc">请稍后，不要离开当前页面</p>
                    </div>
                  }
                </div>
              </div>
            </div>
          </div>
        </div>
      </Content>
      <Footer style={{ textAlign: 'center' }}>
        Ant Design ©{new Date().getFullYear()} Created by Ant UED
      </Footer>
    </Layout>
  );
};
export default Execute;