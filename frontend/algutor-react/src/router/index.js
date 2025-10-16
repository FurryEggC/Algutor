import { createBrowserRouter } from 'react-router-dom'
import App from '../App.js'
import History from '../pages/history/index.js'
import Answer from '../pages/answer/index.js'
import Question from '../pages/question/index.js'
import Knowledge from '../pages/knowledge/index.js'

const router = createBrowserRouter([
  {
    path: '/',
    element: <App></App>,
  },
  {
    path: '/history',
    element: <History></History>
  },
  {
    path: '/answer',
    element: <Answer></Answer>
  },
  {
    path: '/question',
    element: <Question></Question>
  },
  {
    path: '/knowledge',
    element: <Knowledge></Knowledge>
  }
])

export default router