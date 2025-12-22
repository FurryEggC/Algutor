import React from 'react';
import './index.css'
import { Button, Checkbox, Form, Input, Select, Spin } from 'antd';
import { useState } from 'react';
import { Editor } from '@monaco-editor/react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { InboxOutlined, LoadingOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github.css'; // 代码高亮主题

const Explain = () => {
  const navigate = useNavigate();
  const [language, setLanguage] = useState(() => {
    return sessionStorage.getItem('explainLanguage') || 'python';
  });
  const [code, setCode] = useState(() => {
    return sessionStorage.getItem('explainCode') || '';
  });
  const [explainForm] = Form.useForm();

  const [explanation, setExplanation] = useState(() => {
    return sessionStorage.getItem('explanation') || '';
  });
  async function getExplanation(values) {
    try {
      const res = await axios({
        url: 'https://algutor.xyz/api/ai/explain',
        method: 'POST',
        data: {
          "language": values.language,  // 可选，默认为python
          "code": values.code,
        }
      })
      console.log(res)
      setExplanation(res.data.explanation);
      setCanSubmit(true);
      setButtonText('提交代码');
      sessionStorage.setItem('explanation', res.data.explanation);
    } catch (error) {
      navigate('/error');
    }
  }
  const onFinish = values => {
    setCanSubmit(false);
    setButtonText('已提交...');
    getExplanation(values);
    sessionStorage.setItem('explainLanguage', values.language);
    sessionStorage.setItem('explainCode', values.code);
    console.log('Success:', values);
  };
  const onFinishFailed = errorInfo => {
    console.log('Failed:', errorInfo);
  };
  const [canSubmit, setCanSubmit] = useState(true);
  const [buttonText, setButtonText] = useState('提交代码');
  return (
    <div className="ai-explain">
      <div className="ai-explain-code-container">
        <Form
          name="explain"
          form={explainForm}
          labelCol={{ span: 8 }}
          wrapperCol={{ span: 16 }}
          style={{ maxWidth: 600 }}
          initialValues={{ remember: true }}
          onFinish={onFinish}
          onFinishFailed={onFinishFailed}
          autoComplete="off"
        >
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
            <div className='ai-explain-code'>
              <Editor
                height="400px"
                language={language}
                theme="vs"
                onChange={(value) => {
                  setCode(value);
                  explainForm.setFieldValue('code', value);
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
                value={code}
              />
            </div>
          </Form.Item>
          <Form.Item label={null}>
            <Button type="primary" htmlType="submit" disabled={!canSubmit}>
              {buttonText}
            </Button>
          </Form.Item>
        </Form>
      </div>
      <div className="ai-explain-explanation-container">
        {canSubmit ? (
          explanation == '' ? (
            <div className="ai-generate-no-generated_code">
              <InboxOutlined />
              <p className="empty-title">暂无解释</p>
              <p className="empty-desc">点击「提交代码」获取解释</p>
            </div>
          ) : (
            <div className="ai-explain-explanation">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeHighlight]}
              >
                {explanation}
              </ReactMarkdown>
            </div>
          )
        ) :
          <div className="ai-generate-no-generated_code">
            <Spin indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />} />
            <p className="empty-title">正在生成解释中...</p>
            <p className="empty-desc">请稍后，不要离开当前页面</p>
          </div>
        }
      </div>
    </div>
  )
}

export default Explain