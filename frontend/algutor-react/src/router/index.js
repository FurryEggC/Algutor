import { createBrowserRouter } from 'react-router-dom'
import App from '../App.js'
import ErrorPage from '../pages/error/index.js'
import Knowledge from '../pages/knowledge/index.js'
import Execute from '../pages/execute/index.js'
import AI from '../pages/ai/index.js'
import Explain from '../pages/ai/children/explain/index.js'
import Generate from '../pages/ai/children/generate/index.js'
import Debug from '../pages/ai/children/debug/index.js'
import Solve from '../pages/ai/children/solve/index.js'



const router = createBrowserRouter([
  {
    path: '/',
    element: <App></App>,
  },
  {
    path: '/error',
    element: <ErrorPage></ErrorPage>
  },
  {
    path: '/ai',
    element: <AI></AI>,
    children: [
      {
        path: '/ai/explain',
        element: <Explain></Explain>
      },
      {
        path: '/ai/generate',
        element: <Generate></Generate>
      },
      {
        path: '/ai/debug',
        element: <Debug></Debug>
      },
      {
        path: '/ai/solve',
        element: <Solve></Solve>
      }
    ]
  },
  {
    path: '/execute',
    element: <Execute></Execute>
  },
  {
    path: '/knowledge',
    element: <Knowledge></Knowledge>
  }
])

export default router