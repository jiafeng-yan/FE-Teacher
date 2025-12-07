import { useState, useEffect } from 'react'
import ChatInterface from './components/ChatInterface'
import DocumentUpload from './components/DocumentUpload'
import ChunkSettings from './components/ChunkSettings'
import { progressAPI, knowledgeAPI } from './services/api'

function App() {
  const [userId] = useState(() => {
    // 从 localStorage 获取或生成用户ID
    let id = localStorage.getItem('userId')
    if (!id) {
      id = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      localStorage.setItem('userId', id)
    }
    return id
  })
  
  const [userProgress, setUserProgress] = useState(null)
  const [knowledgeInfo, setKnowledgeInfo] = useState(null)
  const [activeTab, setActiveTab] = useState('chat')

  useEffect(() => {
    // 加载用户进度
    loadProgress()
    // 加载知识库信息
    loadKnowledgeInfo()
  }, [])

  const loadProgress = async () => {
    try {
      const progress = await progressAPI.getProgress(userId)
      setUserProgress(progress)
    } catch (error) {
      console.error('加载进度失败:', error)
    }
  }

  const loadKnowledgeInfo = async () => {
    try {
      const info = await knowledgeAPI.getInfo()
      setKnowledgeInfo(info)
    } catch (error) {
      console.error('加载知识库信息失败:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* 头部 */}
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            📚 金融经济教学智能体
          </h1>
          <p className="text-gray-600">
            基于 LangChain 的个性化智能教学系统
          </p>
        </header>

        {/* 标签页 */}
        <div className="bg-white rounded-lg shadow-lg mb-6">
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab('chat')}
              className={`flex-1 px-6 py-4 font-semibold transition-colors ${
                activeTab === 'chat'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              💬 对话学习
            </button>
            <button
              onClick={() => setActiveTab('upload')}
              className={`flex-1 px-6 py-4 font-semibold transition-colors ${
                activeTab === 'upload'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              📄 上传文档
            </button>
            <button
              onClick={() => setActiveTab('progress')}
              className={`flex-1 px-6 py-4 font-semibold transition-colors ${
                activeTab === 'progress'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              📊 学习进度
            </button>
            <button
              onClick={() => setActiveTab('settings')}
              className={`flex-1 px-6 py-4 font-semibold transition-colors ${
                activeTab === 'settings'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              ⚙️ 设置
            </button>
          </div>

          <div className="p-6">
            {activeTab === 'chat' && (
              <ChatInterface userId={userId} onProgressUpdate={loadProgress} />
            )}
            {activeTab === 'upload' && (
              <DocumentUpload onUploadSuccess={loadKnowledgeInfo} />
            )}
            {activeTab === 'settings' && (
              <ChunkSettings onSettingsUpdate={loadKnowledgeInfo} />
            )}
            {activeTab === 'progress' && (
              <div className="space-y-4">
                <h2 className="text-2xl font-bold text-gray-800 mb-4">
                  学习进度
                </h2>
                {userProgress ? (
                  <div className="space-y-4">
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h3 className="font-semibold text-gray-700 mb-2">
                        当前学习主题
                      </h3>
                      <p className="text-gray-600">
                        {userProgress.current_topic || '未设置'}
                      </p>
                    </div>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h3 className="font-semibold text-gray-700 mb-2">
                        知识点掌握程度
                      </h3>
                      {Object.keys(userProgress.mastery_level).length > 0 ? (
                        <div className="space-y-2">
                          {Object.entries(userProgress.mastery_level).map(
                            ([topic, level]) => (
                              <div key={topic}>
                                <div className="flex justify-between mb-1">
                                  <span className="text-sm text-gray-600">
                                    {topic}
                                  </span>
                                  <span className="text-sm font-semibold">
                                    {level.toFixed(1)}%
                                  </span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2">
                                  <div
                                    className={`h-2 rounded-full ${
                                      level >= 80
                                        ? 'bg-green-500'
                                        : level >= 60
                                        ? 'bg-yellow-500'
                                        : 'bg-red-500'
                                    }`}
                                    style={{ width: `${level}%` }}
                                  ></div>
                                </div>
                              </div>
                            )
                          )}
                        </div>
                      ) : (
                        <p className="text-gray-500">暂无学习记录</p>
                      )}
                    </div>
                    {userProgress.mastered_topics.length > 0 && (
                      <div className="bg-green-50 p-4 rounded-lg">
                        <h3 className="font-semibold text-green-700 mb-2">
                          已掌握知识点
                        </h3>
                        <div className="flex flex-wrap gap-2">
                          {userProgress.mastered_topics.map((topic) => (
                            <span
                              key={topic}
                              className="px-3 py-1 bg-green-200 text-green-800 rounded-full text-sm"
                            >
                              {topic}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {userProgress.weak_points.length > 0 && (
                      <div className="bg-red-50 p-4 rounded-lg">
                        <h3 className="font-semibold text-red-700 mb-2">
                          需要加强的知识点
                        </h3>
                        <ul className="list-disc list-inside space-y-1 text-sm text-red-700">
                          {userProgress.weak_points.slice(0, 5).map(
                            (point, index) => (
                              <li key={index}>{point}</li>
                            )
                          )}
                        </ul>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-gray-500">加载中...</p>
                )}
              </div>
            )}
          </div>
        </div>

        {/* 知识库信息 */}
        {knowledgeInfo && (
          <div className="bg-white rounded-lg shadow-lg p-4 text-center text-sm text-gray-600">
            知识库包含 {knowledgeInfo.document_count} 个文档片段
          </div>
        )}
      </div>
    </div>
  )
}

export default App

