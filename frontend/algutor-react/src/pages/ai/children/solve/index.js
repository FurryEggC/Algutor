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

const Solve = () => {
  const navigate = useNavigate();
  const [language, setLanguage] = useState(() => {
    return sessionStorage.getItem('solveLanguage') || 'python';
  });
  const [generateForm] = Form.useForm();

  const [solution, setSolution] = useState(() => {
    return sessionStorage.getItem('solution') || '';
  });
  const [problem, setProblem] = useState(() => {
    return sessionStorage.getItem('problem') || '';
  });
  async function gsetSolution(values) {
    try {
      const res = await axios({
        url: 'https://algutor.xyz/api/ai/solve',
        method: 'POST',
        data: {
          "language": values.language,  // 可选，默认为python
          "problem": values.problem,
        }
      })
      setSolution(res.data.solution)
      setCanSubmit(true);
      setButtonText('生成代码');
      sessionStorage.setItem('solution', res.data.solution);
    } catch (error) {
      navigate('/error');
    }
  }
  const onFinish = values => {
    setCanSubmit(false);
    setButtonText('生成中...');
    gsetSolution(values);
    sessionStorage.setItem('problem', values.problem);
    sessionStorage.setItem('solveLanguage', values.language);
    console.log('Success:', values);
  };
  const onFinishFailed = errorInfo => {
    console.log('Failed:', errorInfo);
  };
  const [canSubmit, setCanSubmit] = useState(true);
  const [buttonText, setButtonText] = useState('生成代码');
  return (
    <div className="ai-solve">
      <div className="ai-solve-problem-container">
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
          <Form.Item name="problem" label="算法问题" rules={[{ required: true, message: '请输入算法问题！' }]}>
            <Input.TextArea
              style={{
                outline: 'none',
                resize: 'none',
                width: '400px',
                height: '200px',
              }}
              defaultValue={problem}
            />
          </Form.Item>
          <Form.Item label={null}>
            <Button type="primary" htmlType="submit" disabled={!canSubmit}>
              {buttonText}
            </Button>
          </Form.Item>
        </Form>
      </div>
      <div className="ai-solve-solution-container">
        {canSubmit ? (
          solution == '' ? (
            <div className="ai-solve-no-solution">
              <InboxOutlined />
              <p className="empty-title">暂无代码</p>
              <p className="empty-desc">点击「生成代码」获取代码</p>
            </div>
          ) : (
            <div className="ai-solve-solution">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeHighlight]}
              >
                {solution}
              </ReactMarkdown>
            </div>
          )
        ) :
          <div className="ai-solve-no-solution">
            <Spin indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />} />
            <p className="empty-title">正在生成算法中...</p>
            <p className="empty-desc">请稍后，不要离开当前页面</p>
          </div>
        }
      </div>
    </div>
  )
}

export default Solve
