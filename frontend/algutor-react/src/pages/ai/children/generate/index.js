import React from 'react';
import './index.css'
import { Button, Checkbox, Form, Input, Select } from 'antd';
import { useState } from 'react';
import { Editor } from '@monaco-editor/react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { InboxOutlined, LoadingOutlined } from '@ant-design/icons';
import { Spin } from 'antd';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github.css'; // 代码高亮主题

const Generate = () => {
  const navigate = useNavigate();
  const [language, setLanguage] = useState(() => {
    return sessionStorage.getItem('generateLanguage') || 'python';
  });
  const [generateForm] = Form.useForm();

  const [generated_code, serGenerated_code] = useState(() => {
    return sessionStorage.getItem('generated_code') || '';
  });
  const [requirement, setRequirement] = useState(() => {
    return sessionStorage.getItem('requirement') || '';
  });
  async function getGenerated_code(values) {
    try {
      const res = await axios({
        url: 'https://algutor.xyz/api/ai/generate',
        method: 'POST',
        data: {
          "language": values.language,  // 可选，默认为python
          "requirement": values.requirement,
        }
      })
      serGenerated_code(res.data.generated_code)
      setCanSubmit(true);
      setButtonText('生成代码');
      sessionStorage.setItem('generated_code', res.data.generated_code);
    } catch (error) {
      navigate('/error');
    }
  }
  const onFinish = values => {
    setCanSubmit(false);
    setButtonText('生成中...');
    getGenerated_code(values);
    sessionStorage.setItem('requirement', values.requirement);
    sessionStorage.setItem('generateLanguage', values.language);
    console.log('Success:', values);
  };
  const onFinishFailed = errorInfo => {
    console.log('Failed:', errorInfo);
  };
  const [canSubmit, setCanSubmit] = useState(true);
  const [buttonText, setButtonText] = useState('生成代码');
  return (
    <div className="ai-generate">
      <div className="ai-generate-requirement-container">
        <Form
          name="generate"
          form={generateForm}
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
          <Form.Item name="requirement" label="代码需求" rules={[{ required: true, message: '请输入代码需求！' }]}>
            <Input.TextArea
              style={{
                outline: 'none',
                resize: 'none',
                width: '400px',
                height: '200px',
              }}
              defaultValue={requirement}
            />
          </Form.Item>
          <Form.Item label={null}>
            <Button type="primary" htmlType="submit" disabled={!canSubmit}>
              {buttonText}
            </Button>
          </Form.Item>
        </Form>
      </div>
      <div className="ai-generate-generated_code-container">
        {canSubmit ? (
          generated_code == '' ? (
            <div className="ai-generate-no-generated_code">
              <InboxOutlined />
              <p className="empty-title">暂无代码</p>
              <p className="empty-desc">点击「生成代码」获取代码</p>
            </div>
          ) : (
            <div className="ai-generate-generated_code">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeHighlight]}
              >
                {generated_code}
              </ReactMarkdown>
            </div>
          )
        ) : (
          <div className="ai-explain-no-explanation">
            <Spin indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />} />
            <p className="empty-title">正在生成代码中...</p>
            <p className="empty-desc">请稍后，不要离开当前页面</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default Generate
