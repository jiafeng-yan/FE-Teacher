import { useState, useEffect } from 'react'
import { knowledgeAPI } from '../services/api'

export default function ChunkSettings({ onSettingsUpdate }) {
  const [chunkSize, setChunkSize] = useState(1000)
  const [chunkOverlap, setChunkOverlap] = useState(200)
  const [loading, setLoading] = useState(false)
  const [confirmReindex, setConfirmReindex] = useState(false)
  const [reindexing, setReindexing] = useState(false)
  const [message, setMessage] = useState(null)
  const [messageType, setMessageType] = useState(null) // 'success' or 'error'

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      const settings = await knowledgeAPI.getChunkSettings()
      setChunkSize(settings.chunk_size)
      setChunkOverlap(settings.chunk_overlap)
    } catch (error) {
      console.error('加载设置失败:', error)
      setMessage('加载设置失败')
      setMessageType('error')
    }
  }

  const handleSaveSettings = async () => {
    setLoading(true)
    setMessage(null)
    
    try {
      const result = await knowledgeAPI.updateChunkSettings(chunkSize, chunkOverlap)
      setMessage(result.warning || result.message)
      setMessageType('success')
      onSettingsUpdate?.()
    } catch (error) {
      setMessage(error.response?.data?.detail || '保存设置失败')
      setMessageType('error')
    } finally {
      setLoading(false)
    }
  }

  const handleReindex = async () => {
    if (!confirmReindex) {
      setMessage('⚠️ 警告：重新索引会删除所有现有文档块并重新创建，这可能需要较长时间。请确认操作。')
      setMessageType('error')
      setConfirmReindex(true)
      return
    }

    setReindexing(true)
    setMessage(null)
    
    try {
      const result = await knowledgeAPI.reindex(chunkSize, chunkOverlap, true)
      
      if (result.success) {
        setMessage(`✅ ${result.message}`)
        setMessageType('success')
        setConfirmReindex(false)
        onSettingsUpdate?.()
      } else {
        setMessage(result.message)
        setMessageType('error')
      }
    } catch (error) {
      setMessage(error.response?.data?.detail || '重新索引失败')
      setMessageType('error')
      setConfirmReindex(false)
    } finally {
      setReindexing(false)
    }
  }

  const handleCancelReindex = () => {
    setConfirmReindex(false)
    setMessage(null)
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">文档分片设置</h2>
      
      <div className="bg-gray-50 p-4 rounded-lg">
        <p className="text-sm text-gray-600 mb-4">
          调整文档分片参数会影响文档的检索效果。较小的分片提供更精确的匹配，较大的分片包含更多上下文。
        </p>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              文档分块大小 (100-5000)
            </label>
            <input
              type="number"
              min="100"
              max="5000"
              value={chunkSize}
              onChange={(e) => setChunkSize(parseInt(e.target.value) || 1000)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">
              每个文档块的最大字符数
            </p>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              分块重叠大小 (0-1000)
            </label>
            <input
              type="number"
              min="0"
              max="1000"
              value={chunkOverlap}
              onChange={(e) => setChunkOverlap(parseInt(e.target.value) || 200)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">
              相邻文档块之间的重叠字符数，有助于保持上下文连续性
            </p>
          </div>
        </div>
      </div>

      {message && (
        <div
          className={`p-4 rounded-lg ${
            messageType === 'success'
              ? 'bg-green-50 border border-green-200 text-green-800'
              : 'bg-red-50 border border-red-200 text-red-800'
          }`}
        >
          <p className="text-sm">{message}</p>
        </div>
      )}

      <div className="flex space-x-4">
        <button
          onClick={handleSaveSettings}
          disabled={loading}
          className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? '保存中...' : '保存设置'}
        </button>

        {confirmReindex ? (
          <div className="flex space-x-2">
            <button
              onClick={handleReindex}
              disabled={reindexing}
              className="px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              {reindexing ? '重新索引中...' : '确认重新索引'}
            </button>
            <button
              onClick={handleCancelReindex}
              disabled={reindexing}
              className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 disabled:bg-gray-200 disabled:cursor-not-allowed transition-colors"
            >
              取消
            </button>
          </div>
        ) : (
          <button
            onClick={handleReindex}
            disabled={reindexing || loading}
            className="px-6 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {reindexing ? '重新索引中...' : '重新索引所有文档'}
          </button>
        )}
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h3 className="font-semibold text-yellow-800 mb-2">⚠️ 重要提示</h3>
        <ul className="text-sm text-yellow-700 space-y-1 list-disc list-inside">
          <li>保存设置只会更新配置，不会影响现有文档</li>
          <li>新设置只会在上传新文档时生效</li>
          <li>要重新处理现有文档，请使用"重新索引所有文档"功能</li>
          <li>重新索引会删除所有现有文档块并重新创建，可能需要较长时间</li>
          <li>建议在重新索引前备份知识库数据</li>
        </ul>
      </div>
    </div>
  )
}

