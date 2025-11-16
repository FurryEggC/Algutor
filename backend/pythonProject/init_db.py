from app import app, db
from models import User, Knowledge, UserKnowledge, UserSession, EmailVerification
import datetime

def init_database():
    """初始化数据库，创建所有表"""
    with app.app_context():
        # 删除旧表（开发环境使用，生产环境请勿使用）
        db.drop_all()
        
        # 创建新表
        db.create_all()
        
        # 创建一些示例公共知识点
        public_knowledge = [
            {
                'topic': '快速排序算法',
                'explanation': '快速排序是一种高效的排序算法，采用分治策略。其基本思想是通过一趟排序将要排序的数据分割成独立的两部分，其中一部分的所有数据都比另外一部分的所有数据都要小，然后再按此方法对这两部分数据分别进行快速排序，整个排序过程可以递归进行，以此达到整个数据变成有序序列。',
                'example': 'def quick_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quick_sort(left) + middle + quick_sort(right)\n\n# 使用示例\narr = [3,6,8,10,1,2,1]\nprint(quick_sort(arr))  # 输出: [1, 1, 2, 3, 6, 8, 10]'
            },
            {
                'topic': '动态规划',
                'explanation': '动态规划是一种将复杂问题分解成更小子问题来解决的方法。它适用于具有重叠子问题和最优子结构特性的问题。动态规划通过存储已解决子问题的答案，避免重复计算，从而提高效率。',
                'example': '# 斐波那契数列的动态规划解法\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    # 创建DP表\n    dp = [0] * (n + 1)\n    dp[1] = 1\n    # 填充DP表\n    for i in range(2, n + 1):\n        dp[i] = dp[i-1] + dp[i-2]\n    return dp[n]\n\n# 使用示例\nprint(fibonacci(10))  # 输出: 55'
            },
            {
                'topic': '二叉树遍历',
                'explanation': '二叉树是一种重要的数据结构，常见的遍历方式有四种：前序遍历（根-左-右）、中序遍历（左-根-右）、后序遍历（左-右-根）和层序遍历。每种遍历方式都有其特定的应用场景。',
                'example': 'class TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\n# 前序遍历\ndef preorder_traversal(root):\n    result = []\n    if root:\n        result.append(root.val)\n        result.extend(preorder_traversal(root.left))\n        result.extend(preorder_traversal(root.right))\n    return result\n\n# 中序遍历\ndef inorder_traversal(root):\n    result = []\n    if root:\n        result.extend(inorder_traversal(root.left))\n        result.append(root.val)\n        result.extend(inorder_traversal(root.right))\n    return result'
            }
        ]
        
        # 添加公共知识点到数据库
        for item in public_knowledge:
            knowledge = Knowledge(
                topic=item['topic'],
                explanation=item['explanation'],
                example=item['example'],
                is_public=True,
                created_by=None  # 系统创建
            )
            db.session.add(knowledge)
        
        # 创建一个示例管理员用户
        admin_user = User(
            username='admin',
            email='admin@example.com',
            is_admin=True,
            email_verified=True
        )
        admin_user.set_password('admin123')
        admin_user.generate_api_key()
        db.session.add(admin_user)
        
        try:
            db.session.commit()
            print("数据库初始化成功！")
            print("已创建表结构和示例数据。")
            print("管理员账号: admin / admin123")
            print("已添加3个示例公共知识点。")
        except Exception as e:
            db.session.rollback()
            print(f"数据库初始化失败: {str(e)}")

if __name__ == '__main__':
    print("开始初始化数据库...")
    init_database()