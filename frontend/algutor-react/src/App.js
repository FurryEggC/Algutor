import logo from './logo.svg';
import './App.css';

function App() {
  return (
    <div className="container">
      {/* 左侧显示历史记录 */}
      <div className="left">
        <div className="history"><h2>历史记录</h2></div>
      </div>
      {/* 右侧显示提问引擎 */}
      <div className="right">
        {/* 两个div用于flex布局将标题和输入框居中显示 */}
        {/* 标题 “ Algutor ” */}
        <div className="inputTitle"><h1>Algutor</h1></div>
        {/* 总输入框，用于将提交按钮包裹在输入框内*/}
        <div className="inputBox">
          <form action="#" id="inputForm">
            <textarea name="#" id="inputBox" placeholder="请输入您的问题..."></textarea>
            <input type="submit" id="submitButton" value="↑" />
          </form>
        </div>
      </div>
    </div>
  );
}

export default App;
